from django.contrib import admin

from .models import Order, OrderItem, OrderStatusHistory

# ==========================
# ORDER ITEM INLINE
# ==========================


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    can_delete = False
    readonly_fields = (
        "product",
        "variant",
        "product_name",
        "variant_details",
        "sku",
        "quantity",
        "unit_price",
        "total_price",
    )


# ==========================
# ORDER STATUS HISTORY INLINE
# ==========================


class OrderStatusHistoryInline(admin.TabularInline):
    model = OrderStatusHistory
    extra = 0
    can_delete = False
    readonly_fields = ("status", "note", "created_by", "created_at")


# ==========================
# ORDER ADMIN
# ==========================


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "order_number",
        "customer",
        "order_status",
        "payment_status",
        "payment_method",
        "total_amount",
        "created_at",
    )

    list_filter = (
        "order_status",
        "payment_status",
        "payment_method",
        "created_at",
    )

    search_fields = (
        "order_number",
        "customer__email",
        "customer__phone",
    )

    # autocomplete_fields = (
    #     "customer",
    #     "shipping_address",
    #     "billing_address",
    #     "shipping_method",
    # )

    readonly_fields = (
        "order_number",
        "subtotal",
        "shipping_cost",
        "tax_amount",
        "discount_amount",
        "total_amount",
        "paid_at",
        "shipped_at",
        "delivered_at",
        "created_at",
        "updated_at",
    )

    fieldsets = (
        ("Order Info", {"fields": ("order_number", "customer")}),
        (
            "Status",
            {
                "fields": (
                    "order_status",
                    "payment_status",
                    "payment_method",
                )
            },
        ),
        (
            "Amounts",
            {
                "fields": (
                    "subtotal",
                    "shipping_cost",
                    "tax_amount",
                    "discount_amount",
                    "total_amount",
                )
            },
        ),
        (
            "Shipping",
            {
                "fields": (
                    "shipping_method",
                    "tracking_number",
                    "shipping_address",
                )
            },
        ),
        ("Billing", {"fields": ("billing_address",)}),
        (
            "Notes",
            {
                "classes": ("collapse",),
                "fields": ("customer_notes", "admin_notes"),
            },
        ),
        (
            "Timestamps",
            {
                "classes": ("collapse",),
                "fields": (
                    "paid_at",
                    "shipped_at",
                    "delivered_at",
                    "created_at",
                    "updated_at",
                ),
            },
        ),
    )

    inlines = [OrderItemInline, OrderStatusHistoryInline]

    actions = ["mark_as_confirmed", "mark_as_shipped", "mark_as_delivered"]

    def save_model(self, request, obj, form, change):
        if change:
            if "order_status" in form.changed_data:
                OrderStatusHistory.objects.create(
                    order=obj,
                    status=obj.order_status,
                    created_by=request.user,
                )
        super().save_model(request, obj, form, change)

    # ==========================
    # ADMIN ACTIONS
    # ==========================

    @admin.action(description="Mark selected orders as Confirmed")
    def mark_as_confirmed(self, request, queryset):
        queryset.update(order_status="confirmed")

    @admin.action(description="Mark selected orders as Shipped")
    def mark_as_shipped(self, request, queryset):
        queryset.update(order_status="shipped")

    @admin.action(description="Mark selected orders as Delivered")
    def mark_as_delivered(self, request, queryset):
        queryset.update(order_status="delivered")


# ==========================
# READ-ONLY STATUS HISTORY
# ==========================


@admin.register(OrderStatusHistory)
class OrderStatusHistoryAdmin(admin.ModelAdmin):
    list_display = ("order", "status", "created_by", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("order__order_number",)

    readonly_fields = [field.name for field in OrderStatusHistory._meta.fields]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
