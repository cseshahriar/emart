from django.contrib import admin

from .models import (
    Brand,
    Category,
    Product,
    ProductAttribute,
    ProductAttributeValue,
    ProductFeature,
    ProductImage,
    ProductSpecification,
    ProductVariant,
    VariantAttribute,
)

# ==========================
# CATEGORY & BRAND
# ==========================


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "parent")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}
    list_filter = ("parent",)


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ("name", "website")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}


# ==========================
# PRODUCT INLINES
# ==========================


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


class ProductFeatureInline(admin.TabularInline):
    model = ProductFeature
    extra = 1


class ProductSpecificationInline(admin.TabularInline):
    model = ProductSpecification
    extra = 1


# ==========================
# VARIANT ATTRIBUTE INLINE
# ==========================


class VariantAttributeInline(admin.TabularInline):
    model = VariantAttribute
    extra = 1
    autocomplete_fields = ("attribute_value",)


# ==========================
# PRODUCT VARIANT INLINE
# ==========================


class ProductVariantInline(admin.StackedInline):
    model = ProductVariant
    extra = 0
    show_change_link = True
    inlines = [VariantAttributeInline]  # visual grouping only


# ==========================
# PRODUCT ADMIN
# ==========================


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "category",
        "brand",
        "base_price",
        "stock_quantity",
        "is_featured",
        "published_at",
    )

    list_filter = (
        "category",
        "brand",
        "is_featured",
        "is_new",
        "is_bestseller",
    )

    search_fields = ("name", "sku")
    prepopulated_fields = {"slug": ("name",)}
    autocomplete_fields = ("category", "brand")

    readonly_fields = ("view_count", "sale_count")

    fieldsets = (
        (
            "Basic Info",
            {"fields": ("name", "slug", "sku", "category", "brand")},
        ),
        ("Pricing", {"fields": ("base_price", "compare_price", "cost_price")}),
        (
            "Inventory",
            {
                "fields": (
                    "track_inventory",
                    "stock_quantity",
                    "low_stock_threshold",
                    "allow_backorder",
                )
            },
        ),
        ("Physical", {"fields": ("weight", "length", "width", "height")}),
        (
            "SEO",
            {
                "classes": ("collapse",),
                "fields": ("meta_title", "meta_description", "meta_keywords"),
            },
        ),
        (
            "Status",
            {
                "fields": (
                    "is_featured",
                    "is_new",
                    "is_bestseller",
                    "is_top_rated",
                    "is_slider",
                    "published_at",
                )
            },
        ),
        (
            "Stats",
            {
                "classes": ("collapse",),
                "fields": ("view_count", "sale_count"),
            },
        ),
    )

    inlines = [
        ProductImageInline,
        ProductFeatureInline,
        ProductSpecificationInline,
    ]


# ==========================
# VARIANT ADMIN (SEPARATE)
# ==========================


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ("product", "sku", "price", "stock_quantity", "is_default")
    list_filter = ("product", "is_default")
    search_fields = ("sku", "product__name")
    autocomplete_fields = ("product",)

    inlines = [VariantAttributeInline]


# ==========================
# ATTRIBUTES
# ==========================


@admin.register(ProductAttribute)
class ProductAttributeAdmin(admin.ModelAdmin):
    list_display = (
        "pk",
        "serial",
        "name",
        "slug",
    )
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}
    ordering = ("serial",)
    list_editable = ("serial",)


@admin.register(ProductAttributeValue)
class ProductAttributeValueAdmin(admin.ModelAdmin):
    list_display = ("attribute", "value", "color_code")
    list_filter = ("attribute",)
    search_fields = ("value", "attribute__name")
    autocomplete_fields = ("attribute",)
