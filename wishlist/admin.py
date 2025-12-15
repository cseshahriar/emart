from django.contrib import admin

from .models import Wishlist, WishlistItem


class WishlistItemInline(admin.TabularInline):
    model = WishlistItem
    extra = 0
    autocomplete_fields = ("product",)
    readonly_fields = ("created_at", "updated_at")


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = (
        "customer",
        "item_count",
        "created_at",
    )

    search_fields = (
        "customer__username",
        "customer__email",
    )

    inlines = [WishlistItemInline]
    readonly_fields = ("created_at", "updated_at")

    def item_count(self, obj):
        return obj.items.count()

    item_count.short_description = "Total Items"


@admin.register(WishlistItem)
class WishlistItemAdmin(admin.ModelAdmin):
    list_display = (
        "wishlist",
        "product",
        "created_at",
    )

    list_filter = ("created_at",)
    search_fields = (
        "wishlist__customer__username",
        "product__name",
    )

    autocomplete_fields = ("wishlist", "product")
    readonly_fields = ("created_at", "updated_at")
