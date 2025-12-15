from django.contrib import admin
from django.utils.html import format_html

from .models import ProductReview, ReviewComment, ReviewImage


class ReviewImageInline(admin.TabularInline):
    model = ReviewImage
    extra = 0
    readonly_fields = ("preview", "created_at")

    def preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="height:60px; border-radius:4px;" />',
                obj.image.url,
            )
        return "-"

    preview.short_description = "Image"


class ReviewCommentInline(admin.TabularInline):
    model = ReviewComment
    extra = 0
    readonly_fields = ("user", "is_staff", "created_at")
    fields = ("user", "comment", "is_staff", "created_at")


@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    list_display = (
        "product",
        "customer",
        "rating",
        "is_verified_purchase",
        "is_approved",
        "helpful_count",
        "created_at",
    )

    list_filter = (
        "rating",
        "is_verified_purchase",
        "is_approved",
        "created_at",
    )

    search_fields = (
        "product__name",
        "customer__email",
        "title",
        "review",
    )

    autocomplete_fields = ("product", "customer", "order")

    readonly_fields = (
        "helpful_count",
        "created_at",
        "updated_at",
    )

    fieldsets = (
        (
            "Review Info",
            {
                "fields": (
                    "product",
                    "customer",
                    "order",
                    "rating",
                )
            },
        ),
        (
            "Content",
            {
                "fields": (
                    "title",
                    "review",
                )
            },
        ),
        (
            "Verification & Moderation",
            {
                "fields": (
                    "is_verified_purchase",
                    "is_approved",
                    "helpful_count",
                )
            },
        ),
        (
            "Timestamps",
            {
                "classes": ("collapse",),
                "fields": (
                    "created_at",
                    "updated_at",
                ),
            },
        ),
    )

    inlines = [ReviewImageInline, ReviewCommentInline]

    actions = [
        "approve_reviews",
        "unapprove_reviews",
        "mark_verified_purchase",
    ]

    # ---------- Admin Actions ----------

    @admin.action(description="Approve selected reviews")
    def approve_reviews(self, request, queryset):
        queryset.update(is_approved=True)

    @admin.action(description="Unapprove selected reviews")
    def unapprove_reviews(self, request, queryset):
        queryset.update(is_approved=False)

    @admin.action(description="Mark as verified purchase")
    def mark_verified_purchase(self, request, queryset):
        queryset.update(is_verified_purchase=True)


@admin.register(ReviewComment)
class ReviewCommentAdmin(admin.ModelAdmin):
    list_display = (
        "review",
        "user",
        "is_staff",
        "created_at",
    )

    list_filter = ("is_staff", "created_at")
    search_fields = ("comment", "user__email")

    readonly_fields = ("created_at", "updated_at")
