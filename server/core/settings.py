import os
import sys
from pathlib import Path
from datetime import timedelta
import logging
import logging.config
from typing import Dict, Any

from django.utils.log import DEFAULT_LOGGING
import environ

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR / 'src/apps'))
env = environ.Env()
environ.Env.read_env(os.path.join(BASE_DIR, ".env"))

SECRET_KEY = "django-insecure-ykk2(twh5mv#atw0u*&u&f)_evbzmfl=y=)3c(b04ep@(m@eq-"

WSDL_URL = "tmp/4tochki.wsdl"
API_URL = "api/v3"

CHUNK_STEP = 1000

DEBUG = True

ALLOWED_HOSTS = ["*"]

CSRF_TRUSTED_ORIGINS = [
    "https://xn--116-mddafavmp2daz.xn--p1ai/admin",
    "https://xn--116-mddafavmp2daz.xn--p1ai/docs",
    "https://xn--116-mddafavmp2daz.xn--p1ai",
    "https://лидертрейд116.рф/admin",
    "https://лидертрейд116.рф/docs",
    "https://лидертрейд116.рф",
    "http://localhost",
    "http://127.0.0.1",
]

# Application definition

DJANGO_APPS = [
    # "jazzmin",
    "django.contrib.admin",
    "django.contrib.postgres",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

SITE_ID = 1

THIRD_PARTY_APPS = [
    "rest_framework",
    "django_filters",
    "django_countries",
    "phonenumber_field",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    "django_celery_beat",
    "django_celery_results",
    "corsheaders",
    "nested_inline",
    "drf_yasg",
    "froala_editor"
]

WAGTAIL_APPS = [
    "wagtail.contrib.forms",
    "wagtail.contrib.redirects",
    "wagtail.embeds",
    "wagtail.sites",
    "wagtail.users",
    "wagtail.snippets",
    "wagtail.documents",
    "wagtail.images",
    "wagtail.search",
    "wagtail.admin",
    "wagtail",
    "modelcluster",
    "taggit",
]

LOCAL_APPS = [
    "base.apps.BaseConfig",
    "users.apps.UsersConfig",
    "profiles.apps.ProfilesConfig",
    "locations.apps.LocationsConfig",
    "catalog.apps.CatalogConfig",
    "interface.apps.InterfaceConfig",
    "products.apps.ProductsConfig",
    "billing.apps.BillingConfig",
    "orders.apps.OrdersConfig",
    "actions.apps.ActionsConfig",
    "unloads.apps.UnloadsConfig",
    "news.apps.NewsConfig",
    "promo",
    "web.apps.WebConfig"
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + WAGTAIL_APPS + LOCAL_APPS

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "wagtail.contrib.redirects.middleware.RedirectMiddleware",
]

ROOT_URLCONF = "core.urls"

TEMPLATES = [
    {
        "NAME": "jinja2",
        "BACKEND": "django.template.backends.jinja2.Jinja2",
        'APP_DIRS': False,
        'DIRS': [
            BASE_DIR / 'src/apps/web/jtemplates',
        ],
        'OPTIONS': {
            "environment": 'web.jinja.environment',
            'extensions': [
                'wagtail.jinja2tags.core',
                'wagtail.admin.jinja2tags.userbar',
                'wagtail.images.jinja2tags.images',
            ],
        }
    },
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "core.wsgi.application"

# Celery
CELERY_BROKER_URL = f"{env('RABBITMQ_URL')}"
# CELERY_RESULT_BACKEND = f"{env('RABBITMQ_URL')}"
CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers:DatabaseScheduler"
CELERY_ACCEPT_CONTENT = ["application/json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = "Europe/Moscow"
CELERY_CACHE_BACKEND = "default"

# Database
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": env("DB_NAME"),
        "USER": env("DB_USER"),
        "PASSWORD": env("DB_PASSWORD"),
        "HOST": env("DB_HOST"),
        "PORT": env("DB_PORT"),
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

LANGUAGE_CODE = "ru-ru"

TIME_ZONE = "Europe/Moscow"

USE_I18N = True

USE_TZ = True

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "static/")
STATICFILES_DIR = []

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

WAGTAIL_SITE_NAME = "LeaderTrade Wagtail"

WAGTAILADMIN_BASE_URL = "http://localhost:8000"

AUTH_USER_MODEL = "users.User"

REST_FRAMEWORK = {
    "NON_FIELD_ERRORS_KEY": "error",
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.LimitOffsetPagination",
    "PAGE_SIZE": 25,
}

# CACHE
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": f"redis://{env('REDIS_HOST')}:{env('REDIS_PORT')}/3",
    }
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=90),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=90),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "UPDATE_LAST_LOGIN": False,
    "ALGORITHM": "HS256",
    "VERIFYING_KEY": None,
    "AUDIENCE": None,
    "ISSUER": None,
    "JWK_URL": None,
    "LEEWAY": 0,
    "AUTH_HEADER_TYPES": ("Bearer",),
    "AUTH_HEADER_NAME": "HTTP_AUTHORIZATION",
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
    "USER_AUTHENTICATION_RULE": "rest_framework_simplejwt.authentication.default_user_authentication_rule",
    "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
    "TOKEN_TYPE_CLAIM": "token_type",
    "TOKEN_USER_CLASS": "rest_framework_simplejwt.models.TokenUser",
    "JTI_CLAIM": "jti",
    "SLIDING_TOKEN_REFRESH_EXP_CLAIM": "refresh_exp",
    "SLIDING_TOKEN_LIFETIME": timedelta(minutes=5),
    "SLIDING_TOKEN_REFRESH_LIFETIME": timedelta(days=1),
}

SWAGGER_SETTINGS = {
    "USE_SESSION_AUTH": False,
    "SECURITY_DEFINITIONS": {
        "Bearer": {"type": "apiKey", "name": "Authorization", "in": "header"}
    },
}

CORS_ORIGIN_ALLOW_ALL = True

CORS_ALLOW_METHODS = (
    "DELETE",
    "GET",
    "OPTIONS",
    "PATCH",
    "POST",
    "PUT",
)

DATA_UPLOAD_MAX_NUMBER_FIELDS = 50000

FROALA_EDITOR_OPTIONS = {
    'language': 'ru'
}