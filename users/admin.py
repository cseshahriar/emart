from django.contrib import admin, messages
from django.contrib.admin.models import LogEntry
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.db.models import Count, Q
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import path, reverse
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from .forms import UserChangeForm, UserCreationForm
from .models import User


# ============== CUSTOM ADMIN FILTERS ==============
class HasEmailFilter(admin.SimpleListFilter):
    """Filter users who have/do not have email"""

    title = _("Email status")
    parameter_name = "has_email"

    def lookups(self, request, model_admin):
        return (
            ("has", _("Has email")),
            ("no", _("No email")),
        )

    def queryset(self, request, queryset):
        if self.value() == "has":
            return queryset.filter(email__isnull=False).exclude(email="")
        if self.value() == "no":
            return queryset.filter(Q(email__isnull=True) | Q(email=""))
        return queryset


class HasPhoneFilter(admin.SimpleListFilter):
    """Filter users who have/do not have phone"""

    title = _("Phone status")
    parameter_name = "has_phone"

    def lookups(self, request, model_admin):
        return (
            ("has", _("Has phone")),
            ("no", _("No phone")),
        )

    def queryset(self, request, queryset):
        if self.value() == "has":
            return queryset.filter(phone__isnull=False).exclude(phone="")
        if self.value() == "no":
            return queryset.filter(Q(phone__isnull=True) | Q(phone=""))
        return queryset


class GroupFilter(admin.SimpleListFilter):
    """Filter users by group"""

    title = _("Group")
    parameter_name = "group"

    def lookups(self, request, model_admin):
        groups = Group.objects.all()
        return [(group.id, group.name) for group in groups]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(groups__id=self.value())
        return queryset


class SocialLoginFilter(admin.SimpleListFilter):
    """Filter users by social login type"""

    title = _("Social login")
    parameter_name = "social"

    def lookups(self, request, model_admin):
        return (
            ("facebook", _("Facebook login")),
            ("google", _("Google login")),
            ("github", _("GitHub login")),
            ("any", _("Any social login")),
            ("none", _("No social login")),
        )

    def queryset(self, request, queryset):
        if self.value() == "facebook":
            return queryset.filter(facebook_id__isnull=False).exclude(facebook_id="")
        elif self.value() == "google":
            return queryset.filter(google_id__isnull=False).exclude(google_id="")
        elif self.value() == "github":
            return queryset.filter(github_id__isnull=False).exclude(github_id="")
        elif self.value() == "any":
            return queryset.filter(
                Q(facebook_id__isnull=False)
                | Q(google_id__isnull=False)
                | Q(github_id__isnull=False)
            ).exclude(Q(facebook_id="") & Q(google_id="") & Q(github_id=""))
        elif self.value() == "none":
            return queryset.filter(
                Q(facebook_id__isnull=True) | Q(facebook_id=""),
                Q(google_id__isnull=True) | Q(google_id=""),
                Q(github_id__isnull=True) | Q(github_id=""),
            )
        return queryset


# ============== CUSTOM USER ADMIN ==============
@admin.register(User)
class CustomUserAdmin(UserAdmin):
    # Forms
    add_form = UserCreationForm
    form = UserChangeForm

    # List display configuration
    list_display = (
        "email_phone_display",
        "full_name_display",
        "groups_display",
        "social_login_display",
        "is_active",
        "is_staff",
        "date_joined_short",
        "actions_column",
    )

    list_display_links = ("email_phone_display",)
    list_filter = (
        HasEmailFilter,
        HasPhoneFilter,
        GroupFilter,
        SocialLoginFilter,
        "is_active",
        "is_staff",
        "is_superuser",
        "date_joined",
    )

    search_fields = (
        "email",
        "phone",
        "first_name",
        "last_name",
        "facebook_id",
        "google_id",
        "github_id",
    )

    ordering = ("-date_joined",)
    filter_horizontal = (
        "groups",
        "user_permissions",
    )
    readonly_fields = (
        "last_login",
        "date_joined",
        "social_ids_display",
        "permissions_summary",
    )

    # Fieldsets for detail view
    fieldsets = (
        (
            _("Authentication"),
            {
                "fields": (
                    "email",
                    "phone",
                    "password_display",
                )
            },
        ),
        (
            _("Personal Information"),
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "profile_picture_display",
                    "bio",
                )
            },
        ),
        (
            _("Social Accounts"),
            {
                "fields": (
                    "social_ids_display",
                    "facebook_id",
                    "google_id",
                    "github_id",
                ),
                "classes": ("collapse",),
            },
        ),
        (
            _("Permissions & Status"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                    "permissions_summary",
                ),
            },
        ),
        (
            _("Important Dates"),
            {
                "fields": (
                    "last_login",
                    "date_joined",
                ),
                "classes": ("collapse",),
            },
        ),
    )

    # Fieldsets for add view
    add_fieldsets = (
        (
            _("Authentication (Required)"),
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "phone",
                    "password1",
                    "password2",
                ),
            },
        ),
        (
            _("Personal Information (Optional)"),
            {
                "classes": ("wide",),
                "fields": (
                    "first_name",
                    "last_name",
                ),
            },
        ),
        (
            _("Permissions (Optional)"),
            {
                "classes": ("collapse",),
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                ),
            },
        ),
    )

    # Custom actions
    actions = [
        "activate_users",
        "deactivate_users",
        "make_staff",
        "remove_staff",
        "send_welcome_email",
        "export_selected_users",
    ]

    # Custom admin views
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "group-stats/",
                self.admin_site.admin_view(self.group_stats_view),
                name="accounts_user_group_stats",
            ),
            path(
                "<path:object_id>/impersonate/",
                self.admin_site.admin_view(self.impersonate_view),
                name="accounts_user_impersonate",
            ),
        ]
        return custom_urls + urls

    # ============ CUSTOM METHODS ============

    # Display methods
    def email_phone_display(self, obj):
        """Display email and phone in list view"""
        items = []
        if obj.email:
            items.append(f"📧 {obj.email}")
        if obj.phone:
            items.append(f"📱 {obj.phone}")

        if not items:
            items.append(f"ID: {obj.id}")

        return format_html("<br>".join(items))

    email_phone_display.short_description = _("Contact")
    email_phone_display.admin_order_field = "email"

    def full_name_display(self, obj):
        """Display full name with avatar"""
        name = obj.get_full_name()
        if not name.strip():
            return "-"

        # Simple avatar based on first letter
        if obj.first_name:
            initial = obj.first_name[0].upper()
            color = "bg-primary"
        else:
            initial = "U"
            color = "bg-secondary"

        avatar = f"""
        <div style="display: inline-block; width: 32px; height: 32px;
                    border-radius: 50%; background: {color}; color: white;
                    text-align: center; line-height: 32px; margin-right: 8px;">
            {initial}
        </div>
        """

        return format_html(f"{avatar} {name}")

    full_name_display.short_description = _("Name")
    full_name_display.admin_order_field = "first_name"

    def groups_display(self, obj):
        """Display groups with badges"""
        groups = obj.groups.all()
        if not groups:
            return format_html('<span class="badge badge-secondary">No groups</span>')

        badges = []
        for group in groups:
            badges.append(
                f'<span class="badge badge-info" style="margin-right: 4px;">{group.name}</span>'
            )
        return format_html(" ".join(badges))

    groups_display.short_description = _("Groups")

    def social_login_display(self, obj):
        """Display social login providers"""
        providers = []
        if obj.facebook_id:
            providers.append('<span style="color: #1877F2;">FB</span>')
        if obj.google_id:
            providers.append('<span style="color: #DB4437;">G</span>')
        if obj.github_id:
            providers.append('<span style="color: #333;">GH</span>')

        if not providers:
            return "-"

        return format_html(" ".join(providers))

    social_login_display.short_description = _("Social")

    def date_joined_short(self, obj):
        """Display date joined in short format"""
        return obj.date_joined.strftime("%Y-%m-%d")

    date_joined_short.short_description = _("Joined")
    date_joined_short.admin_order_field = "date_joined"

    def actions_column(self, obj):
        """Quick action buttons"""
        links = []

        # Impersonate button (for superusers)
        if self.request.user.is_superuser and obj != self.request.user:
            impersonate_url = reverse("admin:accounts_user_impersonate", args=[obj.id])
            links.append(
                f'<a href="{impersonate_url}" class="button" title="Impersonate">👤</a>'
            )

        # Edit button
        edit_url = reverse("admin:accounts_user_change", args=[obj.id])
        links.append(f'<a href="{edit_url}" class="button">✏️</a>')

        return format_html(" ".join(links))

    actions_column.short_description = _("Actions")

    # Detail view display methods
    def password_display(self, obj):
        """Show password change link"""
        if obj.pk:
            change_url = reverse("admin:auth_user_password_change", args=[obj.id])
            return format_html(
                '<a href="{}" class="button">Change Password</a>', change_url
            )
        return "Password will be set after saving"

    password_display.short_description = _("Password")

    def profile_picture_display(self, obj):
        """Display profile picture if exists"""
        if obj.profile_picture:
            return format_html(
                '<img src="{}" style="max-width: 150px; max-height: 150px; \
                    border-radius: 50%;" />',
                obj.profile_picture.url,
            )
        return "No profile picture"

    profile_picture_display.short_description = _("Profile Picture")

    def social_ids_display(self, obj):
        """Display social IDs nicely"""
        items = []
        if obj.facebook_id:
            items.append(f"<strong>Facebook:</strong> {obj.facebook_id}")
        if obj.google_id:
            items.append(f"<strong>Google:</strong> {obj.google_id}")
        if obj.github_id:
            items.append(f"<strong>GitHub:</strong> {obj.github_id}")

        if not items:
            return "No social accounts linked"

        return format_html("<br>".join(items))

    social_ids_display.short_description = _("Linked Social Accounts")

    def permissions_summary(self, obj):
        """Show summary of permissions"""
        total_perms = obj.user_permissions.count()
        group_perms = sum(group.permissions.count() for group in obj.groups.all())

        return format_html(
            "<strong>Direct permissions:</strong> {}<br>"
            "<strong>Group permissions:</strong> {}<br>"
            "<strong>Total effective:</strong> {}",
            total_perms,
            group_perms,
            total_perms + group_perms,
        )

    permissions_summary.short_description = _("Permissions Summary")

    # ============ CUSTOM ACTIONS ============

    @admin.action(description=_("Activate selected users"))
    def activate_users(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(
            request, f"{updated} user(s) have been activated.", messages.SUCCESS
        )

    @admin.action(description=_("Deactivate selected users"))
    def deactivate_users(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(
            request, f"{updated} user(s) have been deactivated.", messages.WARNING
        )

    @admin.action(description=_("Make selected users staff"))
    def make_staff(self, request, queryset):
        updated = queryset.update(is_staff=True)
        self.message_user(
            request, f"{updated} user(s) are now staff members.", messages.SUCCESS
        )

    @admin.action(description=_("Remove staff status"))
    def remove_staff(self, request, queryset):
        # Don't allow removing staff from superusers
        queryset = queryset.exclude(is_superuser=True)
        updated = queryset.update(is_staff=False)
        self.message_user(
            request, f"{updated} user(s) are no longer staff.", messages.WARNING
        )

    @admin.action(description=_("Send welcome email"))
    def send_welcome_email(self, request, queryset):
        # Implement email sending logic here
        count = queryset.count()
        self.message_user(
            request, f"Welcome email would be sent to {count} user(s).", messages.INFO
        )

    @admin.action(description=_("Export selected users to CSV"))
    def export_selected_users(self, request, queryset):
        # Implement CSV export logic here
        self.message_user(
            request,
            f"Export functionality for {queryset.count()} users.",
            messages.INFO,
        )

    # ============ CUSTOM VIEWS ============

    def group_stats_view(self, request):
        """Custom view for group statistics"""
        groups = Group.objects.annotate(
            user_count=Count("user"),
            active_users=Count("user", filter=Q(user__is_active=True)),
            staff_users=Count("user", filter=Q(user__is_staff=True)),
        ).order_by("-user_count")

        context = {
            "title": _("Group Statistics"),
            "groups": groups,
            "total_users": User.objects.count(),
            "opts": self.model._meta,
            "has_view_permission": self.has_view_permission(request),
        }

        return render(request, "admin/accounts/user/group_stats.html", context)

    def impersonate_view(self, request, object_id):
        """Allow admin to impersonate a user"""
        if not request.user.is_superuser:
            messages.error(request, _("Only superusers can impersonate users."))
            return HttpResponseRedirect(reverse("admin:accounts_user_changelist"))

        try:
            user = User.objects.get(id=object_id)
            if user == request.user:
                messages.warning(request, _("You cannot impersonate yourself."))
                return HttpResponseRedirect(reverse("admin:accounts_user_changelist"))

            # Store original user ID in session
            request.session["original_user_id"] = request.user.id
            request.session["impersonated_user_id"] = user.id

            # Log the impersonation
            LogEntry.objects.log_action(
                user_id=request.user.id,
                content_type_id=ContentType.objects.get_for_model(User).id,
                object_id=user.id,
                object_repr=str(user),
                action_flag=4,  # ADDITION
                change_message=f"Impersonated by {request.user}",
            )

            messages.success(
                request,
                _(
                    "You are now impersonating {}. \
                    Use /admin/stop-impersonate/ to stop."
                ).format(user),
            )

            # Redirect to homepage or user's profile
            return HttpResponseRedirect("/")

        except User.DoesNotExist:
            messages.error(request, _("User not found."))
            return HttpResponseRedirect(reverse("admin:accounts_user_changelist"))

    # ============ OVERRIDES ============

    def get_queryset(self, request):
        """Optimize queryset with prefetching"""
        self.request = request
        queryset = super().get_queryset(request)
        queryset = queryset.prefetch_related("groups")
        return queryset

    def changelist_view(self, request, extra_context=None):
        """Add custom context to changelist"""
        extra_context = extra_context or {}

        # Add statistics
        extra_context.update(
            {
                "total_users": User.objects.count(),
                "active_users": User.objects.filter(is_active=True).count(),
                "staff_users": User.objects.filter(is_staff=True).count(),
                "social_users": User.objects.filter(
                    Q(facebook_id__isnull=False)
                    | Q(google_id__isnull=False)
                    | Q(github_id__isnull=False)
                ).count(),
            }
        )

        return super().changelist_view(request, extra_context)


# ============== ADDITIONAL ADMIN REGISTRATIONS ==============
@admin.register(LogEntry)
class LogEntryAdmin(admin.ModelAdmin):
    """Admin for audit logs"""

    list_display = (
        "action_time",
        "user",
        "content_type",
        "object_repr",
        "action_flag_display",
        "change_message",
    )

    list_filter = (
        "action_time",
        "content_type",
        "action_flag",
    )

    search_fields = (
        "user__username",
        "user__email",
        "object_repr",
        "change_message",
    )

    date_hierarchy = "action_time"

    def action_flag_display(self, obj):
        flags = {
            1: "Addition",
            2: "Change",
            3: "Deletion",
            4: "Impersonation",
        }
        return flags.get(obj.action_flag, obj.action_flag)

    action_flag_display.short_description = "Action"

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser


# Optional: Register Permission model for direct management
@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    list_display = ("name", "codename", "content_type", "model_name")
    list_filter = ("content_type",)
    search_fields = ("name", "codename")

    def model_name(self, obj):
        return obj.content_type.model

    model_name.short_description = "Model"

    def has_add_permission(self, request):
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser


# ============== ADMIN SITE CUSTOMIZATION ==============
class CustomAdminSite(admin.AdminSite):
    site_header = "🔐 User Management System"
    site_title = "User Admin"
    index_title = "👋 Welcome to User Administration"

    def get_app_list(self, request):
        """
        Customize the app list ordering
        """
        app_list = super().get_app_list(request)

        # Reorder apps - put auth-related apps first
        ordered_app_list = []
        for app in app_list:
            if app["app_label"] in ["auth", "accounts"]:
                ordered_app_list.insert(0, app)
            else:
                ordered_app_list.append(app)

        return ordered_app_list


# Optional: Use custom admin site
# custom_admin_site = CustomAdminSite(name='custom_admin')
# custom_admin_site.register(User, CustomUserAdmin)
# custom_admin_site.register(Group, CustomGroupAdmin)
