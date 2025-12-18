from django.contrib import admin

from .models import District, Division, Upazila

# ==========================
# DIVISION
# ==========================


@admin.register(Division)
class DivisionAdmin(admin.ModelAdmin):
    list_display = ("serial", "name", "bn_name", "slug")
    search_fields = ("name", "bn_name")
    prepopulated_fields = {"slug": ("name",)}
    list_editable = ("serial",)
    list_display_links = ("name",)

    def has_delete_permission(self, request, obj=None):
        # Prevent delete if districts exist
        if obj and obj.districts.exists():
            return False
        return super().has_delete_permission(request, obj)


# ==========================
# DISTRICT
# ==========================


@admin.register(District)
class DistrictAdmin(admin.ModelAdmin):
    list_display = ("serial", "name", "bn_name", "division", "shipping_zone")
    list_filter = ("division",)
    search_fields = ("name", "bn_name", "division__name")
    autocomplete_fields = ("division",)
    prepopulated_fields = {"slug": ("name",)}
    list_editable = (
        "serial",
        "shipping_zone",
    )
    list_display_links = ("name",)

    def has_delete_permission(self, request, obj=None):
        # Prevent delete if upazilas exist
        if obj and obj.upazilas.exists():
            return False
        return super().has_delete_permission(request, obj)


# ==========================
# UPAZILA / THANA
# ==========================


@admin.register(Upazila)
class UpazilaAdmin(admin.ModelAdmin):
    list_display = ("name", "district", "is_thana", "bn_name")
    list_filter = ("district__division", "district", "is_thana")
    search_fields = (
        "name",
        "bn_name",
        "district__name",
        "district__division__name",
    )

    autocomplete_fields = ("district",)
    prepopulated_fields = {"slug": ("name",)}
