from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from catalog.models import Product
from core.models import BaseModel
from orders.models import Order

User = get_user_model()


class ProductReview(BaseModel):
    """Product reviews and ratings"""

    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="reviews"
    )
    customer = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="reviews"
    )
    order = models.ForeignKey(
        Order, on_delete=models.SET_NULL, null=True, blank=True
    )

    rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    title = models.CharField(max_length=200)
    review = models.TextField()

    # Verification
    is_verified_purchase = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=False)

    # Helpful votes
    helpful_count = models.PositiveIntegerField(default=0)

    # created_at = models.DateTimeField(auto_now_add=True)
    # updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        unique_together = ["product", "customer", "order"]

    def __str__(self):
        return f"{self.product.name} - {self.customer} - {self.rating} stars"


class ReviewImage(BaseModel):
    """Images attached to reviews"""

    review = models.ForeignKey(
        ProductReview, on_delete=models.CASCADE, related_name="images"
    )
    image = models.ImageField(upload_to="reviews/")
    # created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image for review {self.review.id}"


class ReviewComment(BaseModel):
    """Comments/replies on reviews"""

    review = models.ForeignKey(
        ProductReview, on_delete=models.CASCADE, related_name="comments"
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.TextField()
    is_staff = models.BooleanField(default=False)
    # created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"Comment by {self.user.username} on review {self.review.id}"
