"""Settings.py."""

import os

# from django.core.management.utils import get_random_secret_key
from datetime import timedelta
from pathlib import Path

from dotenv import load_dotenv

from config.logging import get_logging_config

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Load .env file
load_dotenv(BASE_DIR / ".env")

TEMPLATES_DIR = os.getenv("TEMPLATES_DIR")
STATICFILES_DIR = os.getenv("STATICFILES_DIR")
STATIC_DIR = os.getenv("STATIC_DIR")
MEDIA_DIR = os.getenv("MEDIA_DIR")
LOGS_DIR = os.getenv("LOGS_DIR", BASE_DIR / "logs")

SITE_NAME = os.getenv("SITE_NAME")

# Logging config
os.makedirs(LOGS_DIR, exist_ok=True)
LOGGING = get_logging_config(LOGS_DIR)

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv("SECRET_KEY", "34v-i9fg8vbuvbij434395fvi-v-vv8lsdfnsdl")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv("DEBUG", "True") == "True"  # String comparison

# Add domain name or ip i.e. example.com
ALLOWED_HOSTS_ENV = os.getenv("ALLOWED_HOSTS", "")
ALLOWED_HOSTS = [
    host.strip() for host in ALLOWED_HOSTS_ENV.split(",") if host.strip()
]

# For Debug Toolbar
INTERNAL_IPS = [
    "127.0.0.1",
]

# Allow frontend
CORS_ALLOWED_ORIGINS = []
CORS_ALLOWED_ORIGIN_REGEXES = [
    "http://127.0.0.1:3000",
    "http://localhost:3000",
]

ENABLE_HTTPS = os.getenv("ENABLE_HTTPS")

# Application definition

INSTALLED_APPS = [
    "nested_admin",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    "django.contrib.humanize",
    # Third-party apps
    "rest_framework",
    "rest_framework_simplejwt.token_blacklist",
    "crispy_forms",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.google",
    "axes",
    "corsheaders",
    "django_countries",
    "djmoney",
    "import_export",
    "drf_yasg",
    "widget_tweaks",
    # Custom Service Apps
    "core",
    "users",
    "frontend",
    "catalog",
    "inventory",
    "cart",
    "orders",
    "shipping",
    "locations",
    "reviews",
    "payments",
    "wishlist",
    "coupon",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "core.middleware.LanguageMiddleware",  # Add custom middleware
    "allauth.account.middleware.AccountMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "axes.middleware.AxesMiddleware",  # << Add this
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# Add debug toolbar only if DEBUG=True and app is installed
# FIXED: Add debug toolbar only if DEBUG=True and app is installed
if DEBUG:
    try:
        import debug_toolbar  # noqa

        INSTALLED_APPS.insert(0, "debug_toolbar")  # Add at beginning
        MIDDLEWARE.insert(1, "debug_toolbar.middleware.DebugToolbarMiddleware")
        # Optional: Add django_extensions for development
        # import django_extensions
        # INSTALLED_APPS.append("django_extensions")
    except ImportError:
        # If debug_toolbar is not installed, just skip it
        pass


ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            os.getenv("TEMPLATES_DIR"),
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "django.template.context_processors.i18n",
                # ✅ your custom processor
                "core.context_processors.common_data",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# Database
# https://docs.djangoproject.com/en/6.0/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("DB_NAME"),
        "USER": os.getenv("DB_USER"),
        "PASSWORD": os.getenv("DB_PASS"),
        "HOST": os.getenv("DB_HOST", "127.0.0.1"),
        "PORT": os.getenv("DB_PORT", "5432"),
    }
}


# Password validation
# https://docs.djangoproject.com/en/6.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "UserAttributeSimilarityValidator"
        )
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation." "MinimumLengthValidator"
        )
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "CommonPasswordValidator"
        )
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "NumericPasswordValidator"
        )
    },
]


AUTHENTICATION_BACKENDS = (
    "axes.backends.AxesStandaloneBackend",
    "users.backends.EmailOrPhoneBackend",
    "django.contrib.auth.backends.ModelBackend",
)

SITE_ID = 1  # It allows Django to Know which domain your project is running on

AUTH_USER_MODEL = "users.User"

TIME_ZONE = "Asia/Dhaka"

# Internationalization
# https://docs.djangoproject.com/en/6.0/topics/i18n/
LANGUAGE_COOKIE_NAME = "django_language"
LANGUAGE_COOKIE_AGE = 60 * 60 * 24 * 365  # 1 year
LANGUAGE_COOKIE_SAMESITE = "Lax"
LANGUAGE_COOKIE_HTTPONLY = False  # Required for JavaScript access
LANGUAGE_CODE = "bn"  # default language


# Enable i18n
LANGUAGES = [
    ("bn", "বাংলা"),
    ("en", "English"),
]

USE_I18N = True

USE_L10N = True

USE_TZ = True

LOCALE_PATHS = [
    os.path.join(BASE_DIR, "locale"),
]

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/6.0/howto/static-files/

STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "static")
STATICFILES_DIRS = [os.path.join(BASE_DIR, "staticfiles")]
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

SITE_HEADER = os.getenv("SITE_HEADER")
SITE_TITLE = os.getenv("SITE_TITLE")
INDEX_TITLE = os.getenv("INDEX_TITLE")


ADMIN_URL = "superadmin"

# SMS Credentials
SMS_API_KEY = os.getenv("SMS_API_KEY")
SMS_SENDER_ID = os.getenv("SMS_SENDER_ID")

MAINTENANCE_MODE = os.getenv("MAINTENANCE_MODE")

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    },
    "file_resubmit": {
        "BACKEND": "django.core.cache.backends.filebased.FileBasedCache",
        "LOCATION": "/tmp/file_resubmit/",
    },
}

# Celery
CELERY_BROKER_URL = "amqp://127.0.0.1:5672/"
CELERY_RESULT_BACKEND = "django-db"
CELERY_CACHE_BACKEND = "django-cache"

SERVICE_NAME = "TIGER ONE"

# Email
EMAIL_BACKEND = os.getenv("EMAIL_BACKEND")
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")

CRONJOBS = [
    # Added job scheduling everyday morning 5:00 am for db backup
    ("0 5 * * *", "config.cron.db_backup"),
]


REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        "rest_framework.authentication.SessionAuthentication",
        # optional for web login
    ],
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ],
    "DEFAULT_PAGINATION_CLASS": (
        "rest_framework.pagination." "PageNumberPagination"
    ),
    "PAGE_SIZE": 20,
}

CRISPY_TEMPLATE_PACK = "bootstrap5"

AXES_FAILURE_LIMIT = 5
AXES_LOCK_OUT_AT_FAILURE = True
AXES_COOLOFF_TIME = 1  # in hours


SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=60),  # adjust as needed
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,  # issue a new refresh token on refresh
    "BLACKLIST_AFTER_ROTATION": True,
    # requires 'rest_framework_simplejwt.token_blacklist'
    "ALGORITHM": "HS256",
    "SIGNING_KEY": SECRET_KEY,
    "AUTH_HEADER_TYPES": ("Bearer",),
    "AUTH_HEADER_NAME": "HTTP_AUTHORIZATION",
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
    "TOKEN_OBTAIN_SERIALIZER": (
        "rest_framework_simplejwt.serializers." "TokenObtainPairSerializer"
    ),
}

# =============== PRODUCTION SECURITY SETTINGS ===============
# These should be enabled when not in DEBUG mode (production)
ENABLE_HTTPS = os.getenv("ENABLE_HTTPS", "False") == "True"

if not DEBUG:
    # Security settings
    SECURE_BROWSER_XSS_FILTER = ENABLE_HTTPS
    SECURE_CONTENT_TYPE_NOSNIFF = ENABLE_HTTPS
    X_FRAME_OPTIONS = "DENY"

    # HSTS Settings (Warning W004)
    SECURE_HSTS_SECONDS = 31_536_000  # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = ENABLE_HTTPS
    SECURE_HSTS_PRELOAD = ENABLE_HTTPS

    # SSL Settings (Warning W008)
    SECURE_SSL_REDIRECT = ENABLE_HTTPS
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

    # Cookie security
    SESSION_COOKIE_SECURE = ENABLE_HTTPS
    CSRF_COOKIE_SECURE = ENABLE_HTTPS
    SESSION_COOKIE_HTTPONLY = ENABLE_HTTPS
    CSRF_COOKIE_HTTPONLY = ENABLE_HTTPS

    # Additional security
    SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"

    # Use WhiteNoise for static files in production
    STATICFILES_STORAGE = (
        "whitenoise.storage.CompressedManifestStaticFilesStorage"
    )

    # Add WhiteNoise middleware
    MIDDLEWARE.insert(1, "whitenoise.middleware.WhiteNoiseMiddleware")
else:
    # Development settings
    SECURE_SSL_REDIRECT = False
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False

    # Development cache
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        },
        "file_resubmit": {
            "BACKEND": "django.core.cache.backends.filebased.FileBasedCache",
            "LOCATION": "/tmp/file_resubmit/",
        },
    }
