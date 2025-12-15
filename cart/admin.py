from django.contrib import admin

from .models import Cart, CartItem


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    # autocomplete_fields = ("product", "variant")
    readonly_fields = ("unit_price", "total_price")

    def unit_price(self, obj):
        return obj.unit_price

    def total_price(self, obj):
        return obj.total_price


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "customer",
        "session_key",
        "total_items",
        "subtotal",
        "created_at",
    )
    list_filter = ("created_at",)
    search_fields = ("customer__email", "session_key")
    inlines = [CartItemInline]
    readonly_fields = ("total_items", "subtotal")

    def total_items(self, obj):
        return obj.total_items

    def subtotal(self, obj):
        return obj.subtotal


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "cart",
        "product",
        "variant",
        "quantity",
        "unit_price",
        "total_price",
    )
    list_filter = ("product",)
    search_fields = ("product__name", "cart__id")

    def unit_price(self, obj):
        return obj.unit_price

    def total_price(self, obj):
        return obj.total_price
