from django.contrib import admin

from .models import Coupon, CouponUsage

# ==========================
# COUPON ADMIN
# ==========================


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = (
        "code",
        "discount_type",
        "discount_value",
        "valid_from",
        "valid_to",
        "usage_count",
        "usage_limit",
    )

    list_filter = (
        "discount_type",
        "valid_from",
        "valid_to",
    )

    search_fields = ("code", "description")

    filter_horizontal = ("categories", "products")

    readonly_fields = ("usage_count",)

    fieldsets = (
        ("Basic Info", {"fields": ("code", "description")}),
        (
            "Discount",
            {
                "fields": (
                    "discount_type",
                    "discount_value",
                    "maximum_discount",
                )
            },
        ),
        (
            "Limitations",
            {
                "classes": ("collapse",),
                "fields": (
                    "minimum_purchase",
                    "usage_limit",
                    "usage_limit_per_customer",
                ),
            },
        ),
        ("Validity", {"fields": ("valid_from", "valid_to")}),
        (
            "Restrictions",
            {
                "classes": ("collapse",),
                "fields": ("categories", "products"),
            },
        ),
        (
            "Statistics",
            {
                "classes": ("collapse",),
                "fields": ("usage_count",),
            },
        ),
    )

    def has_delete_permission(self, request, obj=None):
        # Prevent deleting used coupons
        if obj and obj.usage_count > 0:
            return False
        return super().has_delete_permission(request, obj)


# ==========================
# COUPON USAGE (READ-ONLY)
# ==========================


@admin.register(CouponUsage)
class CouponUsageAdmin(admin.ModelAdmin):
    list_display = (
        "coupon",
        "customer",
        "order",
        "discount_amount",
        "used_at",
    )

    list_filter = ("coupon", "used_at")
    search_fields = (
        "coupon__code",
        "customer__email",
        "order__id",
    )

    readonly_fields = (
        "coupon",
        "customer",
        "order",
        "discount_amount",
        "used_at",
    )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
