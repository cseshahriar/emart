"""base urls."""

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

SITE_HEADER = "Shorna Mart Administration"
SITE_TITLE = "Shorna Mart Administration"
INDEX_TITLE = "Shorna Mart Admin Panel"


urlpatterns = [
    # JWT Authentication
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/token/verify/", TokenVerifyView.as_view(), name="token_verify"),
    path("i18n/", include("django.conf.urls.i18n")),
    # include apps urls
    path("", include("frontend.urls")),
]

urlpatterns += i18n_patterns(
    path("set-language/", set_language, name="set_language"),
    # admin urls
    path(f"{settings.ADMIN_URL}/", admin.site.urls),
)

# Serve media files in development environment
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# debug toolbar ---------------------------------------------------------------
if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [
        path("__debug__/", include(debug_toolbar.urls))
    ] + urlpatterns  # noqa

# admin site customizations
admin.sites.AdminSite.site_header = SITE_HEADER
admin.sites.AdminSite.site_title = SITE_TITLE
admin.sites.AdminSite.index_title = INDEX_TITLE
