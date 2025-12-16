from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

from catalog.models import Product, ProductVariant
from core.models import BaseModel

User = get_user_model()


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

    def __str__(self):
        return f"Cart {self.id} - {self.customer or self.session_key}"

    @property
    def total_items(self):
        return sum(item.quantity for item in self.items.all())

    @property
    def subtotal(self):
        return sum(item.total_price for item in self.items.all())

    def get_shipping_weight(self):
        """Calculate total weight for shipping"""
        total_weight = Decimal("0.00")
        for item in self.items.all():
            if item.variant:
                weight = item.variant.weight or item.product.weight or 0
            else:
                weight = item.product.weight or 0
            total_weight += weight * item.quantity
        return total_weight


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
