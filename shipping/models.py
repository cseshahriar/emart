from decimal import Decimal

from django.contrib.auth import get_user_model
from django.db import models

from core.models import BaseModel
from locations.models import Division

User = get_user_model()


# ==================== Shipping Models ====================
class ShippingZone(BaseModel):
    """Shipping zones based on divisions"""

    name = models.CharField(max_length=200)
    divisions = models.ManyToManyField(Division, related_name="shipping_zones")
    # is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class ShippingMethod(BaseModel):
    """Shipping methods with different options"""

    DELIVERY_TYPE_CHOICES = [
        ("standard", "Standard Delivery"),
        ("express", "Express Delivery"),
        ("overnight", "Overnight Delivery"),
        ("pickup", "Store Pickup"),
    ]

    name = models.CharField(max_length=200)
    delivery_type = models.CharField(
        max_length=20, choices=DELIVERY_TYPE_CHOICES
    )
    description = models.TextField(blank=True)
    estimated_days_min = models.PositiveIntegerField(default=1)
    estimated_days_max = models.PositiveIntegerField(default=7)
    # is_active = models.BooleanField(default=True)
    # order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = []

    def __str__(self):
        return f"{self.name} ({self.estimated_days_min}-{self.estimated_days_max} days)"


class ShippingRate(BaseModel):
    """Shipping rates based on zone, weight, and method"""

    CALCULATION_TYPE_CHOICES = [
        ("flat", "Flat Rate"),
        ("weight", "Weight Based"),
        ("price", "Price Based"),
    ]

    shipping_method = models.ForeignKey(
        ShippingMethod, on_delete=models.CASCADE, related_name="rates"
    )
    shipping_zone = models.ForeignKey(
        ShippingZone, on_delete=models.CASCADE, related_name="rates"
    )
    calculation_type = models.CharField(
        max_length=20, choices=CALCULATION_TYPE_CHOICES, default="flat"
    )

    # Flat rate
    flat_rate = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal(0)
    )

    # Weight based
    min_weight = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Min weight in KG",
    )
    max_weight = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Max weight in KG",
    )
    rate_per_kg = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )

    # Price based
    min_order_value = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    max_order_value = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )

    # Free shipping
    free_shipping_over = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Free shipping for orders over this amount",
    )

    # is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["shipping_zone", "shipping_method"]

    def __str__(self):
        return f"{self.shipping_method.name} - {self.shipping_zone.name}"

    def calculate_shipping_cost(self, weight=None, order_value=None):
        """Calculate shipping cost based on weight and order value"""
        # Check free shipping
        if (
            self.free_shipping_over
            and order_value
            and order_value >= self.free_shipping_over
        ):
            return Decimal("0.00")

        if self.calculation_type == "flat":
            return self.flat_rate

        elif self.calculation_type == "weight" and weight:
            if self.min_weight and weight < self.min_weight:
                return None  # Out of range
            if self.max_weight and weight > self.max_weight:
                return None  # Out of range
            return self.flat_rate + (weight * (self.rate_per_kg or 0))

        elif self.calculation_type == "price" and order_value:
            if self.min_order_value and order_value < self.min_order_value:
                return None  # Out of range
            if self.max_order_value and order_value > self.max_order_value:
                return None  # Out of range
            return self.flat_rate

        return self.flat_rate
