import os
from pathlib import Path
# from django.core.management.utils import get_random_secret_key
from datetime import timedelta
from config.logging import get_logging_config
from dotenv import load_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Load .env file
load_dotenv(BASE_DIR / ".env")

# Build paths inside the project like this: os.path.join(BASE_DIR, ...) -------
TEMPLATES_DIR = os.getenv('TEMPLATES_DIR')
STATICFILES_DIR = os.getenv('STATICFILES_DIR')
STATIC_DIR = os.getenv('STATIC_DIR')
MEDIA_DIR = os.getenv('MEDIA_DIR')
LOGS_DIR = os.getenv('LOGS_DIR', BASE_DIR / "logs")


# Logging config
os.makedirs(LOGS_DIR, exist_ok=True)
LOGGING = get_logging_config(LOGS_DIR)

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv("SECRET_KEY", "34v-i9fg8vbuvbij434395fvi-v-vv8lsdfnsdl")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv("DEBUG", True)

# Add domain name or ip i.e. example.com
ALLOWED_HOSTS = [
    '127.0.0.1',
    'localhost',
]

# For Debug Toolbar
INTERNAL_IPS = [
    '127.0.0.1',
]

# Allow frontend
CORS_ALLOWED_ORIGINS = []
CORS_ALLOWED_ORIGIN_REGEXES = [
    'http://127.0.0.1:3000',
    "http://localhost:3000",
]

ENABLE_HTTPS = os.getenv("ENABLE_HTTPS")

# HTTPS configuration
if ENABLE_HTTPS:  # local_settings
    USE_X_FORWARDED_HOST = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'django.contrib.humanize',

    # Third-party apps
    "rest_framework",
    "rest_framework_simplejwt.token_blacklist",
    "crispy_forms",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "axes",
    "corsheaders",
    "django_countries",
    "djmoney",
    "import_export",
    "drf_yasg",
    "debug_toolbar",

    # Custom Service Apps
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'allauth.account.middleware.AccountMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    "axes.middleware.AxesMiddleware",  # << Add this
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.getenv("TEMPLATES_DIR"), ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.i18n',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

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
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

AUTHENTICATION_BACKENDS = (
    "axes.backends.AxesStandaloneBackend",
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
)

SITE_ID = 1

# AUTH_USER_MODEL = 'users.User'

# Internationalization
# https://docs.djangoproject.com/en/6.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/6.0/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.getenv("STATIC_DIR", BASE_DIR / "static")
STATICFILES_DIRS = [os.getenv("STATICFILES_DIR", BASE_DIR / "staticfiles")]

MEDIA_URL = '/media/'
MEDIA_ROOT = os.getenv("MEDIA_DIR", BASE_DIR / "media")

SITE_HEADER = "Shorna Mart Administration"
SITE_TITLE = "Shorna Mart Administration"
INDEX_TITLE = "Shorna Mart Admin Panel"


ADMIN_URL = 'superadmin'

# SMS Credentials
SMS_API_KEY = os.getenv("SMS_API_KEY")
SMS_SENDER_ID = os.getenv("SMS_SENDER_ID")

MAINTENANCE_MODE = os.getenv("MAINTENANCE_MODE")

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    },
    "file_resubmit": {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        "LOCATION": '/tmp/file_resubmit/'
    },
}

# Celery
CELERY_BROKER_URL = 'amqp://127.0.0.1:5672/'
CELERY_RESULT_BACKEND = 'django-db'
CELERY_CACHE_BACKEND = 'django-cache'

SERVICE_NAME = 'TIGER ONE'

# Email
EMAIL_BACKEND = os.getenv("EMAIL_BACKEND")
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")

LANGUAGES = [
    ('en', 'English'),
    ('bn', 'Bengali'),
]

CRONJOBS = [
    # Added job scheduling everyday morning 5:00 am for db backup
    ('0 5 * * *', 'config.cron.db_backup'),
]


REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',  # optional for web login
    ],
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter'
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}

CRISPY_TEMPLATE_PACK = "bootstrap5"

AXES_FAILURE_LIMIT = 5
AXES_LOCK_OUT_AT_FAILURE = True
AXES_COOLOFF_TIME = 1  # in hours


SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),  # adjust as needed
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,       # issue a new refresh token on refresh
    'BLACKLIST_AFTER_ROTATION': True,    # requires 'rest_framework_simplejwt.token_blacklist'
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'TOKEN_OBTAIN_SERIALIZER': 'rest_framework_simplejwt.serializers.TokenObtainPairSerializer',
}
