import nested_admin

from django.contrib import admin

from .models import (
    Brand,
    Category,
    Color,
    Product,
    ProductAttribute,
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
    list_display = (
        "serial",
        "name",
        "bn_name",
        "parent",
        "is_active",
        "is_featured",
        "is_main_menu",
    )
    search_fields = ("name",)
    list_display_links = ("name",)
    prepopulated_fields = {"slug": ("name",)}
    list_filter = ("parent",)
    list_editable = (
        "serial",
        "bn_name",
        "is_active",
        "is_featured",
        "is_main_menu",
    )


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ("serial", "name", "website")
    list_display_links = ("name",)
    list_editable = ("serial",)
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Color)
class ColorAdmin(admin.ModelAdmin):
    list_display = (
        "serial",
        "name",
        "code",
    )
    list_display_links = ("name",)
    search_fields = ("name",)
    list_editable = ("serial",)
    ordering = ("serial",)


# ==========================
# PRODUCT INLINES
# ==========================


class ProductImageInline(nested_admin.NestedTabularInline):
    model = ProductImage
    extra = 1
    # Don't specify fields - Django will show all fields


class ProductFeatureInline(nested_admin.NestedTabularInline):
    model = ProductFeature
    extra = 1
    # Don't specify fields - Django will show all fields


class ProductSpecificationInline(nested_admin.NestedTabularInline):
    model = ProductSpecification
    extra = 1
    # Don't specify fields - Django will show all fields


# ==========================
# VARIANT ATTRIBUTE INLINE
# ==========================


class VariantAttributeInline(nested_admin.NestedTabularInline):
    model = VariantAttribute
    extra = 1
    autocomplete_fields = ("value",)
    min_num = 0


# ==========================
# PRODUCT VARIANT INLINE
# ==========================


class ProductVariantInline(nested_admin.NestedStackedInline):
    model = ProductVariant
    extra = 1
    show_change_link = True
    # Optional: Customize displayed fields
    fields = (
        "sku",
        "price",
        "compare_price",
        "stock_quantity",
        "weight",
        "is_default",
    )
    readonly_fields = ("sku",)  # If you want to make SKU read-only
    inlines = [VariantAttributeInline]  # This will work with nested_admin


# ==========================
# PRODUCT ADMIN
# ==========================


@admin.register(Product)
class ProductAdmin(nested_admin.NestedModelAdmin):
    list_display = (
        "name",
        "category",
        "brand",
        "base_price",
        "stock_quantity",
        "is_active",
        "is_new",
        "is_slider",
        "is_featured",
        "is_most_popular",
        "is_bestseller",
        "published_at",
    )

    list_filter = (
        "category",
        "brand",
        "is_active",
        "is_slider",
        "is_most_popular",
        "is_featured",
        "is_new",
        "is_bestseller",
    )

    search_fields = ("name", "sku")
    prepopulated_fields = {"slug": ("name",)}
    autocomplete_fields = ("category", "brand")
    readonly_fields = ("view_count", "sale_count")
    list_editable = (
        "is_active",
        "is_slider",
        "is_new",
        "is_featured",
        "is_most_popular",
        "is_bestseller",
    )
    fieldsets = (
        (
            "Basic Info",
            {
                "fields": (
                    "name",
                    "slug",
                    "sku",
                    "category",
                    "brand",
                    "short_description",
                    "description",
                )
            },
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
                    "is_active",
                    "is_most_popular",
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
        ProductVariantInline,
    ]


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
