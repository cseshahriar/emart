from django.contrib import admin

from .models import ShippingMethod, ShippingRate, ShippingSetting, ShippingZone


@admin.register(ShippingZone)
class ShippingZoneAdmin(admin.ModelAdmin):
    list_display = ("serial", "name", "division_list", "created_at")
    list_display_links = ("name",)
    search_fields = ("name", "divisions__name")
    filter_horizontal = ("divisions",)
    readonly_fields = ("created_at", "updated_at")
    list_editable = (("serial"),)

    def division_list(self, obj):
        return ", ".join(obj.divisions.values_list("name", flat=True))

    division_list.short_description = "Divisions"


@admin.register(ShippingMethod)
class ShippingMethodAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "delivery_type",
        "estimated_days_min",
        "estimated_days_max",
        "created_at",
    )

    list_filter = ("delivery_type",)
    search_fields = ("name", "description")
    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        (
            "Method Info",
            {
                "fields": (
                    "name",
                    "delivery_type",
                    "description",
                )
            },
        ),
        (
            "Delivery Time",
            {
                "fields": (
                    "estimated_days_min",
                    "estimated_days_max",
                )
            },
        ),
        (
            "System",
            {
                "classes": ("collapse",),
                "fields": ("created_at", "updated_at"),
            },
        ),
    )


@admin.register(ShippingRate)
class ShippingRateAdmin(admin.ModelAdmin):
    list_display = (
        "shipping_method",
        "shipping_zone",
        "calculation_type",
        "min_weight",
        "max_weight",
        "rate_per_kg",
        "free_shipping_over",
    )

    list_filter = (
        "calculation_type",
        "shipping_method",
        "shipping_zone",
    )

    search_fields = (
        "shipping_method__name",
        "shipping_zone__name",
    )

    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        (
            "Basic Info",
            {
                "fields": (
                    "shipping_method",
                    "shipping_zone",
                    "calculation_type",
                )
            },
        ),
        (
            "Flat Rate",
            {
                "fields": ("flat_rate",),
            },
        ),
        (
            "Weight Based Rules",
            {
                "classes": ("collapse",),
                "fields": (
                    "min_weight",
                    "max_weight",
                    "rate_per_kg",
                ),
            },
        ),
        (
            "Order Price Rules",
            {
                "classes": ("collapse",),
                "fields": (
                    "min_order_value",
                    "max_order_value",
                ),
            },
        ),
        (
            "Free Shipping",
            {
                "fields": ("free_shipping_over",),
            },
        ),
        (
            "System",
            {
                "classes": ("collapse",),
                "fields": ("created_at", "updated_at"),
            },
        ),
    )


@admin.register(ShippingSetting)
class ShippingSettingAdmin(admin.ModelAdmin):
    list_display = (
        "serial",
        "cod_percentage",
        "vat_percentage",
        "is_active",
        "created_at",
    )
    readonly_fields = ("created_at", "updated_at")
