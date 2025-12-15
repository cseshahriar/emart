from django.contrib import admin

from .models import (
    Payment,
    PaymentGateway,
    PaymentMethodAccount,
    Refund,
)


@admin.register(PaymentGateway)
class PaymentGatewayAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "gateway_type",
        "is_test_mode",
        "transaction_fee_percentage",
        "transaction_fee_fixed",
        "created_at",
    )

    list_filter = ("gateway_type", "is_test_mode")
    search_fields = ("name", "gateway_type")

    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        ("Basic Info", {"fields": ("name", "gateway_type", "is_test_mode")}),
        (
            "Credentials",
            {
                "classes": ("collapse",),
                "fields": ("api_key", "api_secret", "merchant_id"),
            },
        ),
        (
            "Fees",
            {
                "fields": (
                    "transaction_fee_percentage",
                    "transaction_fee_fixed",
                )
            },
        ),
        (
            "Display",
            {
                "classes": ("collapse",),
                "fields": ("logo", "description", "instructions"),
            },
        ),
        (
            "Timestamps",
            {
                "classes": ("collapse",),
                "fields": ("created_at", "updated_at"),
            },
        ),
    )


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        "payment_id",
        "order",
        "payment_gateway",
        "amount",
        "transaction_fee",
        "net_amount",
        "status",
        "created_at",
    )

    list_filter = (
        "status",
        "payment_gateway",
        "currency",
        "created_at",
    )

    search_fields = (
        "payment_id",
        "transaction_id",
        "order__order_number",
        "customer_email",
        "customer_phone",
    )

    autocomplete_fields = ("order", "payment_gateway")

    readonly_fields = (
        "payment_id",
        "transaction_fee",
        "net_amount",
        "transaction_id",
        "gateway_response",
        "ip_address",
        "user_agent",
        "created_at",
        "updated_at",
        "completed_at",
    )

    fieldsets = (
        (
            "Payment Info",
            {"fields": ("payment_id", "order", "payment_gateway", "status")},
        ),
        (
            "Amount",
            {
                "fields": (
                    "amount",
                    "transaction_fee",
                    "net_amount",
                    "currency",
                )
            },
        ),
        (
            "Gateway Data",
            {
                "classes": ("collapse",),
                "fields": (
                    "transaction_id",
                    "gateway_response",
                ),
            },
        ),
        (
            "Customer Snapshot",
            {
                "classes": ("collapse",),
                "fields": (
                    "customer_name",
                    "customer_email",
                    "customer_phone",
                ),
            },
        ),
        (
            "Technical Info",
            {
                "classes": ("collapse",),
                "fields": ("ip_address", "user_agent"),
            },
        ),
        (
            "Notes",
            {
                "classes": ("collapse",),
                "fields": ("notes", "failure_reason"),
            },
        ),
        (
            "Timestamps",
            {
                "classes": ("collapse",),
                "fields": (
                    "created_at",
                    "updated_at",
                    "completed_at",
                ),
            },
        ),
    )

    actions = ["mark_completed", "mark_failed"]

    def save_model(self, request, obj, form, change):
        # Prevent admin from changing amount after creation
        if change and "amount" in form.changed_data:
            raise ValueError("Payment amount cannot be modified.")
        super().save_model(request, obj, form, change)

    @admin.action(description="Mark selected payments as Completed")
    def mark_completed(self, request, queryset):
        queryset.update(status="completed")

    @admin.action(description="Mark selected payments as Failed")
    def mark_failed(self, request, queryset):
        queryset.update(status="failed")


@admin.register(Refund)
class RefundAdmin(admin.ModelAdmin):
    list_display = (
        "refund_id",
        "order",
        "payment",
        "refund_type",
        "amount",
        "status",
        "created_at",
    )

    list_filter = ("status", "refund_type", "created_at")
    search_fields = (
        "refund_id",
        "payment__payment_id",
        "order__order_number",
    )

    autocomplete_fields = ("payment", "order", "requested_by", "processed_by")

    readonly_fields = (
        "refund_id",
        "transaction_id",
        "gateway_response",
        "created_at",
        "updated_at",
        "completed_at",
    )

    fieldsets = (
        (
            "Refund Info",
            {
                "fields": (
                    "refund_id",
                    "payment",
                    "order",
                    "refund_type",
                    "amount",
                    "status",
                )
            },
        ),
        (
            "Gateway Data",
            {
                "classes": ("collapse",),
                "fields": ("transaction_id", "gateway_response"),
            },
        ),
        (
            "Reason",
            {
                "fields": ("reason", "admin_notes"),
            },
        ),
        (
            "Processing",
            {
                "fields": ("requested_by", "processed_by"),
            },
        ),
        (
            "Timestamps",
            {
                "classes": ("collapse",),
                "fields": (
                    "created_at",
                    "updated_at",
                    "completed_at",
                ),
            },
        ),
    )


@admin.register(PaymentMethodAccount)
class PaymentMethodAccountAdmin(admin.ModelAdmin):
    list_display = (
        "customer",
        "payment_gateway",
        "account_number",
        "is_default",
        "is_verified",
        "created_at",
    )

    list_filter = ("payment_gateway", "is_default", "is_verified")
    search_fields = ("account_number", "customer__email", "customer__phone")

    autocomplete_fields = ("customer", "payment_gateway")

    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        (
            "Account Info",
            {
                "fields": (
                    "customer",
                    "payment_gateway",
                    "account_number",
                    "account_holder_name",
                    "payment_token",
                )
            },
        ),
        (
            "Status",
            {
                "fields": ("is_default", "is_verified"),
            },
        ),
        (
            "Timestamps",
            {
                "classes": ("collapse",),
                "fields": ("created_at", "updated_at"),
            },
        ),
    )
