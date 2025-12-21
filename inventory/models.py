# stock, sku
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.db import models

from catalog.models import Product, ProductVariant
from core.models import BaseModel
from locations.models import District, Division, Upazila
from orders.models import Order

User = get_user_model()


class Warehouse(BaseModel):
    """Warehouse/Store locations for inventory management"""

    name = models.CharField(max_length=200)
    code = models.CharField(max_length=50, unique=True)

    # Location
    address = models.TextField()
    division = models.ForeignKey(
        Division, on_delete=models.PROTECT, null=True, blank=True
    )
    district = models.ForeignKey(
        District, on_delete=models.PROTECT, null=True, blank=True
    )
    upazila = models.ForeignKey(
        Upazila, on_delete=models.PROTECT, null=True, blank=True
    )

    # Contact
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    manager = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="managed_warehouses",
    )

    # Status
    # is_active = models.BooleanField(default=True)
    is_default = models.BooleanField(default=False)

    # created_at = models.DateTimeField(auto_now_add=True)
    # updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-is_default", "name"]

    def __str__(self):
        return f"{self.name} ({self.code})"

    def save(self, *args, **kwargs):
        if self.is_default:
            Warehouse.objects.filter(is_default=True).update(is_default=False)
        super().save(*args, **kwargs)


class InventoryStock(BaseModel):
    """Track inventory for each product/variant in each warehouse"""

    warehouse = models.ForeignKey(
        Warehouse, on_delete=models.CASCADE, related_name="inventory_stocks"
    )
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="inventory_stocks"
    )
    variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="inventory_stocks",
    )

    # Stock Levels
    quantity = models.IntegerField(default=0)
    reserved_quantity = models.IntegerField(
        default=0, help_text="Quantity reserved for pending orders"
    )

    # Thresholds
    low_stock_threshold = models.PositiveIntegerField(default=5)
    reorder_point = models.PositiveIntegerField(
        default=10, help_text="Trigger reorder at this level"
    )
    reorder_quantity = models.PositiveIntegerField(
        default=50, help_text="Quantity to reorder"
    )

    # Cost tracking
    unit_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Current unit cost",
    )

    # Timestamps
    last_restocked = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ["warehouse", "product", "variant"]
        ordering = ["warehouse", "product"]
        verbose_name = "Inventory Stock"
        verbose_name_plural = "Inventory Stocks"

    def __str__(self):
        variant_info = f" - {self.variant}" if self.variant else ""
        return f"{self.warehouse.code}: {self.product.name}{variant_info} ({self.available_quantity})"  # noqa

    @property
    def available_quantity(self):
        """Available quantity = Total - Reserved"""
        return max(0, self.quantity - self.reserved_quantity)

    @property
    def needs_reorder(self):
        """Check if stock needs to be reordered"""
        return self.available_quantity <= self.reorder_point

    @property
    def is_low_stock(self):
        """Check if stock is low"""
        return self.available_quantity <= self.low_stock_threshold


class StockMovement(BaseModel):
    """Track all inventory movements"""

    MOVEMENT_TYPE_CHOICES = [
        ("purchase", "Purchase/Restock"),
        ("sale", "Sale"),
        ("return", "Return"),
        ("adjustment", "Manual Adjustment"),
        ("transfer", "Warehouse Transfer"),
        ("damaged", "Damaged/Lost"),
        ("reserved", "Reserved for Order"),
        ("released", "Released from Reserve"),
    ]

    warehouse = models.ForeignKey(
        Warehouse, on_delete=models.CASCADE, related_name="stock_movements"
    )
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="stock_movements"
    )
    variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="stock_movements",
    )
    movement_type = models.CharField(
        max_length=20, choices=MOVEMENT_TYPE_CHOICES
    )
    quantity = models.IntegerField(
        help_text="Positive for additions, negative for deductions"
    )

    # Previous and new quantity
    quantity_before = models.IntegerField()
    quantity_after = models.IntegerField()

    # Cost
    unit_cost = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    total_cost = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True
    )

    # References
    order = models.ForeignKey(
        Order,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="stock_movements",
    )
    reference_number = models.CharField(
        max_length=100, blank=True, help_text="PO number, invoice number, etc."
    )

    # Transfer details
    transfer_to_warehouse = models.ForeignKey(
        Warehouse,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="received_transfers",
    )

    # Notes
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["warehouse", "-created_at"]),
            models.Index(fields=["product", "-created_at"]),
        ]

    def __str__(self):
        return f"{self.get_movement_type_display()}: {self.product.name} \
            ({self.quantity:+d})"

    def save(self, *args, **kwargs):
        # Calculate total cost
        if self.unit_cost and self.quantity:
            self.total_cost = abs(self.quantity) * self.unit_cost

        super().save(*args, **kwargs)


class PurchaseOrder(BaseModel):
    """Purchase orders for restocking inventory"""

    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("sent", "Sent to Supplier"),
        ("confirmed", "Confirmed"),
        ("partially_received", "Partially Received"),
        ("received", "Fully Received"),
        ("cancelled", "Cancelled"),
    ]

    po_number = models.CharField(max_length=50, unique=True)
    warehouse = models.ForeignKey(
        Warehouse, on_delete=models.PROTECT, related_name="purchase_orders"
    )
    supplier_name = models.CharField(max_length=200)
    supplier_email = models.EmailField(blank=True)
    supplier_phone = models.CharField(max_length=20, blank=True)
    supplier_address = models.TextField(blank=True)

    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="draft"
    )

    # Dates
    order_date = models.DateField()
    expected_delivery_date = models.DateField(null=True, blank=True)
    received_date = models.DateField(null=True, blank=True)

    # Amounts
    subtotal = models.DecimalField(
        max_digits=12, decimal_places=2, default=Decimal(0)
    )
    tax_amount = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal(0)
    )
    shipping_cost = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal(0)
    )
    total_amount = models.DecimalField(
        max_digits=12, decimal_places=2, default=Decimal(0)
    )

    # Notes
    notes = models.TextField(blank=True)

    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_purchase_orders",
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Purchase Order"
        verbose_name_plural = "Purchase Orders"

    def __str__(self):
        return f"PO-{self.po_number} - {self.supplier_name}"

    def save(self, *args, **kwargs):
        if not self.po_number:
            import uuid

            self.po_number = f"{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)


class PurchaseOrderItem(BaseModel):
    """Items in a purchase order"""

    purchase_order = models.ForeignKey(
        PurchaseOrder, on_delete=models.CASCADE, related_name="items"
    )
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    variant = models.ForeignKey(
        ProductVariant, on_delete=models.PROTECT, null=True, blank=True
    )

    quantity_ordered = models.PositiveIntegerField()
    quantity_received = models.PositiveIntegerField(default=0)

    unit_cost = models.DecimalField(max_digits=10, decimal_places=2)
    total_cost = models.DecimalField(max_digits=12, decimal_places=2)

    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return f"{self.product.name} x {self.quantity_ordered}"

    @property
    def quantity_pending(self):
        return self.quantity_ordered - self.quantity_received

    @property
    def is_fully_received(self):
        return self.quantity_received >= self.quantity_ordered

    def save(self, *args, **kwargs):
        self.total_cost = self.quantity_ordered * self.unit_cost
        super().save(*args, **kwargs)
