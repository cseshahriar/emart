import logging
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

from catalog.models import Product, ProductVariant
from core.models import BaseModel
from locations.models import District
from shipping.models import ShippingRate

User = get_user_model()

logger = logging.getLogger(__name__)


class Cart(BaseModel):
    """Shopping cart"""

    customer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="carts",
        null=True,
        blank=True,
    )
    session_key = models.CharField(max_length=100, blank=True)
    district = models.ForeignKey(
        District,
        on_delete=models.SET_NULL,
        related_name="carts",
        null=True,
        blank=True,
    )

    def __str__(self):
        return f"Cart {self.id} - {self.customer or self.session_key}"

    @property
    def total_items(self):
        return sum(item.quantity for item in self.items.all())

    @property
    def subtotal(self):
        total = sum(item.total_price for item in self.items.all())
        return Decimal(total) or 0

    def get_shipping_weight(self):
        """Calculate total weight for shipping in KG"""
        total_weight = Decimal("0.00")
        for item in self.items.all():
            if item.variant:
                weight = item.variant.weight or item.product.weight or 0
            else:
                weight = item.product.weight or 0
            total_weight += weight * item.quantity
        return total_weight

    def get_shipping_charge(self):
        """
        Calculate shipping charge based on:
        - district -> shipping zone
        - total weight
        """
        if not self.district:
            return Decimal("0.00")

        weight = self.get_shipping_weight()
        logger.info(f"{'*' * 10} weight: {weight}\n")

        # Find shipping zone for district
        shipping_zone = self.district.shipping_zone
        logger.info(f"{'*' * 10} shipping_zone: {shipping_zone}\n")
        if not shipping_zone:
            return Decimal("0.00")

        # Find matching rate slab, by method
        rate = ShippingRate.objects.filter(
            shipping_zone=shipping_zone,
        ).first()
        logger.info(f"{'*' * 10} rate: {rate}\n")

        if rate:
            return rate.rate_per_kg

        return Decimal("0.00")

    @property
    def grand_total(self):
        return self.subtotal + self.get_shipping_charge()


class CartItem(BaseModel):
    """Cart items"""

    cart = models.ForeignKey(
        Cart, on_delete=models.CASCADE, related_name="items"
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variant = models.ForeignKey(
        ProductVariant, on_delete=models.CASCADE, null=True, blank=True
    )
    quantity = models.PositiveIntegerField(
        default=1, validators=[MinValueValidator(1)]
    )

    class Meta:
        unique_together = ["cart", "product", "variant"]

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"

    @property
    def unit_price(self):
        if self.variant:
            return self.variant.price
        return self.product.base_price

    @property
    def total_price(self):
        return self.unit_price * self.quantity
