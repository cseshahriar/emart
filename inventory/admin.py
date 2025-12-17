from django.contrib import admin

from .models import (
    InventoryStock,
    PurchaseOrder,
    PurchaseOrderItem,
    StockMovement,
    Warehouse,
)

# ==========================
# WAREHOUSE
# ==========================


@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "division", "district", "is_default")
    list_filter = ("division", "district", "is_default")
    search_fields = ("name", "code")
    # autocomplete_fields = ("division", "district", "upazila", "manager")

    def save_model(self, request, obj, form, change):
        if obj.is_default:
            Warehouse.objects.exclude(pk=obj.pk).update(is_default=False)
        super().save_model(request, obj, form, change)


# ==========================
# INVENTORY STOCK
# ==========================


@admin.register(InventoryStock)
class InventoryStockAdmin(admin.ModelAdmin):
    list_display = (
        "warehouse",
        "product",
        "variant",
        "quantity",
        "reserved_quantity",
        "available_quantity",
        "is_low_stock",
        "needs_reorder",
    )

    list_filter = ("warehouse",)
    search_fields = ("product__name", "variant__sku")
    # autocomplete_fields = ("warehouse", "product", "variant")

    readonly_fields = (
        "available_quantity",
        "is_low_stock",
        "needs_reorder",
        "updated_at",
    )

    def has_add_permission(self, request):
        return True

    def has_delete_permission(self, request, obj=None):
        return False


# ==========================
# STOCK MOVEMENT (READ ONLY)
# ==========================


@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = (
        "created_at",
        "movement_type",
        "warehouse",
        "product",
        "variant",
        "quantity",
        "order",
        "created_by",
    )

    list_filter = ("movement_type", "warehouse", "created_at")
    search_fields = ("product__name", "variant__sku", "reference_number")
    # autocomplete_fields = (
    #     "warehouse",
    #     "product",
    #     "variant",
    #     "order",
    #     "transfer_to_warehouse",
    # )

    readonly_fields = [field.name for field in StockMovement._meta.fields]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


# ==========================
# PURCHASE ORDER ITEMS INLINE
# ==========================


class PurchaseOrderItemInline(admin.TabularInline):
    model = PurchaseOrderItem
    extra = 1
    # autocomplete_fields = ("product", "variant")
    readonly_fields = ("total_cost",)


# ==========================
# PURCHASE ORDER
# ==========================


@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(admin.ModelAdmin):
    list_display = (
        "po_number",
        "supplier_name",
        "warehouse",
        "status",
        "order_date",
        "total_amount",
    )

    list_filter = ("status", "warehouse", "order_date")
    search_fields = ("po_number", "supplier_name")

    autocomplete_fields = ("warehouse", "created_by")

    readonly_fields = (
        "subtotal",
        "tax_amount",
        "shipping_cost",
        "total_amount",
    )

    inlines = [PurchaseOrderItemInline]

    fieldsets = (
        ("PO Info", {"fields": ("po_number", "status", "warehouse")}),
        (
            "Supplier",
            {
                "fields": (
                    "supplier_name",
                    "supplier_email",
                    "supplier_phone",
                    "supplier_address",
                )
            },
        ),
        (
            "Dates",
            {
                "fields": (
                    "order_date",
                    "expected_delivery_date",
                    "received_date",
                )
            },
        ),
        (
            "Amounts",
            {
                "fields": (
                    "subtotal",
                    "tax_amount",
                    "shipping_cost",
                    "total_amount",
                )
            },
        ),
        ("Notes", {"classes": ("collapse",), "fields": ("notes",)}),
    )

    def save_model(self, request, obj, form, change):
        if not obj.created_by:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
