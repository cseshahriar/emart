from django.contrib.auth import get_user_model
from django.db import models

from catalog.models import Category, Product
from core.models import BaseModel
from orders.models import Order

User = get_user_model()


class Coupon(BaseModel):
    """Discount coupons"""

    DISCOUNT_TYPE_CHOICES = [
        ("percentage", "Percentage"),
        ("fixed", "Fixed Amount"),
        ("free_shipping", "Free Shipping"),
    ]

    code = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    discount_type = models.CharField(
        max_length=20, choices=DISCOUNT_TYPE_CHOICES
    )
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)

    # Limitations
    minimum_purchase = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    maximum_discount = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    usage_limit = models.PositiveIntegerField(null=True, blank=True)
    usage_limit_per_customer = models.PositiveIntegerField(
        null=True, blank=True
    )

    # Validity
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()

    # Restrictions
    categories = models.ManyToManyField(Category, blank=True)
    products = models.ManyToManyField(Product, blank=True)

    # Status
    # is_active = models.BooleanField(default=True)

    # Stats
    usage_count = models.PositiveIntegerField(default=0)

    # created_at = models.DateTimeField(auto_now_add=True)
    # updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.code

    def is_valid(self):
        from django.utils import timezone

        now = timezone.now()
        if not self.is_active:
            return False
        if self.valid_from > now or self.valid_to < now:
            return False
        if self.usage_limit and self.usage_count >= self.usage_limit:
            return False
        return True


class CouponUsage(BaseModel):
    """Track coupon usage"""

    coupon = models.ForeignKey(
        Coupon, on_delete=models.CASCADE, related_name="usages"
    )
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2)
    used_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.coupon.code} used by {self.customer}"
