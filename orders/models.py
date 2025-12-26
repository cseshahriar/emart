from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

from catalog.models import Product, ProductVariant
from core.models import BaseModel
from shipping.models import ShippingMethod
from users.models import Address

User = get_user_model()


class Order(BaseModel):
    """Main order model"""

    ORDER_STATUS_CHOICES = [
        ("pending", "Pending"),
        ("processing", "Processing"),
        ("confirmed", "Confirmed"),
        ("shipped", "Shipped"),
        ("delivered", "Delivered"),
        ("cancelled", "Cancelled"),
        ("refunded", "Refunded"),
    ]

    PAYMENT_STATUS_CHOICES = [
        ("pending", "Pending"),
        ("paid", "Paid"),
        ("failed", "Failed"),
        ("refunded", "Refunded"),
    ]

    PAYMENT_METHOD_CHOICES = [
        ("cod", "Cash on Delivery"),
        ("bkash", "bKash"),
        ("nagad", "Nagad"),
        ("rocket", "Rocket"),
        ("card", "Credit/Debit Card"),
        ("bank", "Bank Transfer"),
    ]

    # Order Info
    order_number = models.CharField(max_length=50, unique=True)
    customer = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="orders",
    )
    session_key = models.CharField(
        max_length=100,
        blank=True,
        null=True,
    )
    # Status
    order_status = models.CharField(
        max_length=20, choices=ORDER_STATUS_CHOICES, default="pending"
    )
    payment_status = models.CharField(
        max_length=20, choices=PAYMENT_STATUS_CHOICES, default="pending"
    )
    payment_method = models.CharField(
        max_length=20, choices=PAYMENT_METHOD_CHOICES
    )

    # Amounts
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    shipping_cost = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal(0)
    )
    cod_charge = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal(0)
    )
    tax_amount = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal(0)
    )
    discount_amount = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal(0)
    )
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)

    # by Address
    # full_name = models.CharField(max_length=200)
    # phone = models.CharField(max_length=20)
    # district = models.ForeignKey(
    #     District, on_delete=models.SET_NULL, null=True
    # )  # location base per kg product shipping charge calculate

    # Shipping
    shipping_method = models.ForeignKey(
        ShippingMethod, on_delete=models.SET_NULL, null=True
    )
    shipping_address = models.ForeignKey(
        Address,
        on_delete=models.SET_NULL,
        related_name="shipping_orders",
        null=True,
        blank=True,
    )
    billing_address = models.ForeignKey(
        Address,
        on_delete=models.SET_NULL,
        related_name="billing_orders",
        null=True,
        blank=True,
    )

    # Tracking
    tracking_number = models.CharField(max_length=200, blank=True)

    # Notes
    customer_notes = models.TextField(blank=True)
    admin_notes = models.TextField(blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    shipped_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["order_number"]),
            models.Index(fields=["-created_at"]),
            models.Index(fields=["customer", "-created_at"]),
        ]

    def __str__(self):
        return f"Order #{self.order_number}"

    def save(self, *args, **kwargs):
        if not self.order_number:
            import uuid

            self.order_number = f"ORD-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)


class OrderItem(models.Model):
    """Order line items"""

    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="items"
    )
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    variant = models.ForeignKey(
        ProductVariant, on_delete=models.SET_NULL, null=True, blank=True
    )

    # Snapshot of product details at time of order
    product_name = models.CharField(max_length=500)
    variant_details = models.CharField(max_length=500, blank=True)
    sku = models.CharField(max_length=100, blank=True)

    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product_name} x {self.quantity}"

    def save(self, *args, **kwargs):
        self.total_price = self.unit_price * self.quantity
        super().save(*args, **kwargs)


class OrderStatusHistory(models.Model):
    """Track order status changes"""

    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="status_history"
    )
    status = models.CharField(max_length=20)
    note = models.TextField(blank=True)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name_plural = "Order status histories"

    def __str__(self):
        return f"{self.order.order_number} - {self.status}"
