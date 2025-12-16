# product, category, attributes
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models
from django.utils.text import slugify

from core.models import BaseModel

User = get_user_model()


class Category(BaseModel):
    """Nested Category for products"""

    parent = models.ForeignKey(
        "self",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="children",
    )
    name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(
        max_length=100, blank=True, help_text="Icon class (e.g., fa fa-search)"
    )
    image = models.ImageField(upload_to="categories/", blank=True, null=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "Categories"

    def __str__(self):
        full_path = [self.name]
        parent = self.parent
        while parent:
            full_path.append(parent.name)
            parent = parent.parent
        return " > ".join(full_path[::-1])

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_all_children(self):
        """Get all descendant categories"""
        children = list(self.children.all())
        for child in list(children):
            children.extend(child.get_all_children())
        return children


# ==================== Product Models ====================
class Brand(BaseModel):
    """Product Brands"""

    name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(unique=True)
    logo = models.ImageField(upload_to="brands/", blank=True, null=True)
    description = models.TextField(blank=True)
    website = models.URLField(blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Product(BaseModel):
    """Main Product Model"""

    # Basic Information
    name = models.CharField(max_length=500)
    slug = models.SlugField(unique=True, max_length=550)
    sku = models.CharField(max_length=100, unique=True, blank=True)
    category = models.ForeignKey(
        Category, on_delete=models.PROTECT, related_name="products"
    )
    brand = models.ForeignKey(
        Brand,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="products",
    )

    # Descriptions
    short_description = models.TextField(max_length=500, blank=True)
    description = models.TextField(blank=True)

    # Pricing
    base_price = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(0)]
    )
    compare_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Original price for discount display",
    )
    cost_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Your cost (not shown to customers)",
    )

    # Inventory
    track_inventory = models.BooleanField(default=True)
    stock_quantity = models.PositiveIntegerField(default=0)
    low_stock_threshold = models.PositiveIntegerField(default=5)
    allow_backorder = models.BooleanField(default=False)

    # Physical Properties
    weight = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Weight in KG",  # Todo make gm
    )
    length = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Length in CM",
    )
    width = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Width in CM",
    )
    height = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Height in CM",
    )

    # SEO
    meta_title = models.CharField(max_length=200, blank=True)
    meta_description = models.TextField(max_length=300, blank=True)
    meta_keywords = models.CharField(max_length=500, blank=True)

    # Status
    # is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    is_new = models.BooleanField(default=False)  # new arrivals
    is_bestseller = models.BooleanField(default=False)  # best sellers
    is_top_rated = models.BooleanField(default=False)  # top rated
    is_slider = models.BooleanField(default=False)  # top rated

    # Timestamps
    # created_at = models.DateTimeField(auto_now_add=True)
    # updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)

    # Statistics
    view_count = models.PositiveIntegerField(default=0)
    sale_count = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["slug"]),
            models.Index(fields=["sku"]),
            models.Index(fields=["-created_at"]),
            models.Index(fields=["is_active", "-created_at"]),
        ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    @property
    def discount_percentage(self):
        if self.compare_price and self.compare_price > self.base_price:
            return int(
                ((self.compare_price - self.base_price) / self.compare_price)
                * 100
            )

        return 0

    @property
    def is_in_stock(self):
        if not self.track_inventory:
            return True
        return self.stock_quantity > 0 or self.allow_backorder

    @property
    def average_rating(self):
        reviews = self.reviews.filter(is_approved=True)
        if reviews.exists():
            return reviews.aggregate(models.Avg("rating"))["rating__avg"]
        return 0

    @property
    def review_count(self):
        return self.reviews.filter(is_approved=True).count()


class ProductImage(BaseModel):
    """Product Images"""

    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="images"
    )
    image = models.ImageField(upload_to="products/")
    alt_text = models.CharField(max_length=200, blank=True)
    is_primary = models.BooleanField(default=False)

    class Meta:
        ordering = ["-is_primary"]

    def __str__(self):
        return f"{self.product.name} - Image"

    def save(self, *args, **kwargs):
        if self.is_primary:
            ProductImage.objects.filter(
                product=self.product, is_primary=True
            ).update(is_primary=False)

        super().save(*args, **kwargs)


class ProductFeature(BaseModel):
    """
    Product Features List
    ✔ Long-lasting battery
    ✔ Fast charging support
    ✔ Premium metal body
    ✔ Water resistant
    ✔ Suitable for daily use
    """

    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="features"
    )
    title = models.CharField(max_length=500)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = []

    def __str__(self):
        return f"{self.product.name} - {self.title}"


class ProductSpecification(BaseModel):
    """
    Product Specifications
    Brand: Apple
    Model: iPhone 15
    Battery: 5100 mAh
    Screen Size: 6.1 inches
    Weight: 171 g
    """

    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="specifications"
    )
    attribute = models.ForeignKey(
        "catalog.ProductAttribute",
        on_delete=models.PROTECT,
        related_name="specifications",
        null=True,
        blank=False,
    )
    value = models.CharField(max_length=500)

    class Meta:
        ordering = []

    def __str__(self):
        return f"{self.product.name} - \
            {self.attribute.name if self.attribute else ''}: {self.value}"


# ==================== Product Variants ====================
class ProductAttribute(BaseModel):
    """Attribute types (Color, Size, Battery, etc.)"""

    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class ProductAttributeValue(BaseModel):
    """Attribute values (Red, Large, 5100mAh, etc.)"""

    attribute = models.ForeignKey(
        ProductAttribute, on_delete=models.PROTECT, related_name="values"
    )
    value = models.CharField(max_length=200)
    color_code = models.CharField(
        max_length=7,
        blank=True,
        help_text="Hex color code for color attributes",
    )

    class Meta:
        unique_together = ["attribute", "value"]
        ordering = ["attribute", "value"]

    def __str__(self):
        return f"{self.attribute.name}: {self.value}"


# =================== product variant =========================================
class ProductVariant(BaseModel):
    """Product Variants with different prices and stock"""

    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="variants"
    )
    sku = models.CharField(max_length=100, unique=True, blank=True)
    # Pricing
    price = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(0)]
    )
    compare_price = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )

    # Inventory
    stock_quantity = models.PositiveIntegerField(default=0)

    # Physical
    weight = models.DecimalField(
        max_digits=8, decimal_places=2, null=True, blank=True
    )

    # Image
    image = models.ImageField(upload_to="variants/", blank=True, null=True)

    # Status
    # is_active = models.BooleanField(default=True)
    is_default = models.BooleanField(default=False)

    # created_at = models.DateTimeField(auto_now_add=True)
    # updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-is_default", "price"]

    def __str__(self):
        attrs = " - ".join(
            [
                f"{va.attribute_value.attribute.name}: {va.attribute_value.value}"
                for va in self.variant_attributes.all()
            ]
        )
        return f"{self.product.name} ({attrs})"

    @property
    def is_in_stock(self):
        return self.stock_quantity > 0


class VariantAttribute(BaseModel):
    """Link variants to their attribute values"""

    variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.CASCADE,
        related_name="variant_attributes",
    )
    attribute_value = models.ForeignKey(
        ProductAttributeValue, on_delete=models.PROTECT
    )

    class Meta:
        unique_together = ["variant", "attribute_value"]

    def __str__(self):
        return f"{self.variant} - {self.attribute_value}"
