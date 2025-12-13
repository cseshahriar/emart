# ==================== Wishlist ====================
from django.contrib.auth import get_user_model
from django.db import models

from catalog.models import Product
from core.models import BaseModel

User = get_user_model()


class Wishlist(BaseModel):
    """Customer wishlist"""

    customer = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="wishlist"
    )

    def __str__(self):
        return f"Wishlist - {self.customer}"


class WishlistItem(BaseModel):
    """Wishlist items"""

    wishlist = models.ForeignKey(
        Wishlist, on_delete=models.CASCADE, related_name="items"
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    class Meta:
        unique_together = ["wishlist", "product"]
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.wishlist.customer} - {self.product.name}"
