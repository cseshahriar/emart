from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.i18n import set_language
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

SITE_HEADER = settings.SITE_HEADER
SITE_TITLE = settings.SITE_TITLE
INDEX_TITLE = settings.SITE_TITLE


# ======================
# NON-TRANSLATED URLS
# ======================
urlpatterns = [
    # Custom set_language view to fix redirect issues
    path("set-language/", set_language, name="set_language_custom"),
    # admin urls
    path(f"{settings.ADMIN_URL}/", admin.site.urls),
    path("_nested_admin/", include("nested_admin.urls")),
    # JWT Authentication
    path(
        "api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"
    ),
    path(
        "api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"
    ),
    path("api/token/verify/", TokenVerifyView.as_view(), name="token_verify"),
]


# ======================
# TRANSLATED URLS
# /en/  /bn/
# ======================
urlpatterns += i18n_patterns(
    path("", include("frontend.urls")),
    # Add the default django set_language as fallback
    path("i18n/", include("django.conf.urls.i18n")),
    prefix_default_language=True,  # Important: This prefixes default language too
)


# ======================
# MEDIA & DEBUG
# ======================
if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )

    try:
        import debug_toolbar  # noqa

        urlpatterns = [
            path("__debug__/", include(debug_toolbar.urls)),
        ] + urlpatterns
    except ImportError:
        pass


# ======================
# ADMIN UI TEXT
# ======================
admin.sites.AdminSite.site_header = SITE_HEADER
admin.sites.AdminSite.site_title = SITE_TITLE
admin.sites.AdminSite.index_title = INDEX_TITLE
