import logging
import os
from pathlib import Path

import environ

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
BASE_DIR = PROJECT_ROOT / "src"
CONTRIB_DIR = PROJECT_ROOT / "contrib"


env = environ.Env(
    DEBUG=(bool, False),
    SECRET_KEY=(str, "g7Dpw*NPF&qGYh%fCE@FEu6T5iT2^TUg&5ysH6xFio*S^9U5FV"),
    ALLOWED_HOSTS=(list, []),
    DEBUG_TOOLBAR=(bool, True),
    STATIC_ROOT=(Path, BASE_DIR / "public" / "static"),
    LOG_LEVEL=(str, "DEBUG"),
    LOG_FORMAT=(str, "default"),
    APP_DATA=(Path, PROJECT_ROOT / "data"),
    DATABASE_URL=(str, "sqlite:////app/db/db.sqlite3"),
    REGISTRATION_OPEN=(bool, True),
    MAILGUN_API_KEY=(str, ""),
    MAILGUN_SENDER_DOMAIN=(str, ""),
    CSRF_TRUSTED_ORIGINS=(list, ["http://localhost:8000"]),
)

env_file = os.getenv("ENV_FILE", None)

if env_file:
    environ.Env.read_env(env_file)


SECRET_KEY = env("SECRET_KEY")

DEBUG = env("DEBUG")
DEBUG_TOOLBAR = env("DEBUG") and env("DEBUG_TOOLBAR")

INTERNAL_IPS = [
    "127.0.0.1",
]
ALLOWED_HOSTS = env("ALLOWED_HOSTS")

if DEBUG:
    try:
        import socket

        hostname = socket.gethostname()
        ip = socket.gethostbyname(hostname)
        INTERNAL_IPS.append(ip)
        ALLOWED_HOSTS.append(ip)
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.info("couldn't setup allowed host in debug: %s", e)


CSRF_TRUSTED_ORIGINS = env("CSRF_TRUSTED_ORIGINS")

# Application definition

DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

EXTERNAL_APPS = [
    "django_linear_migrations",
    "django_extensions",
    "django_htmx",
    "django_bootstrap5",
    "django_cleanup.apps.CleanupConfig",  # should be last: https://pypi.org/project/django-cleanup/
]
if DEBUG_TOOLBAR:
    EXTERNAL_APPS.insert(-2, "debug_toolbar")
if DEBUG:
    EXTERNAL_APPS.insert(-2, "django_browser_reload")

CUSTOM_APPS = [
    "whitenoise.runserver_nostatic",  # should be first
    "common",
    "character",
    "party",
]

INSTALLED_APPS = CUSTOM_APPS + DJANGO_APPS + EXTERNAL_APPS

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django_htmx.middleware.HtmxMiddleware",
]
if DEBUG_TOOLBAR:
    MIDDLEWARE.insert(0, "debug_toolbar.middleware.DebugToolbarMiddleware")
if DEBUG:
    MIDDLEWARE.append("django_browser_reload.middleware.BrowserReloadMiddleware")

ROOT_URLCONF = "charasheet.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "charasheet.context_processors.app",
            ],
        },
    },
]

WSGI_APPLICATION = "charasheet.wsgi.application"


DATABASES = {"default": env.db()}

############################################################
# Cache configuration

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.db.DatabaseCache",
    },
}

SOLO_CACHE = "default"
SOLO_CACHE_TIMEOUT = 60 * 10  # 10 mins

# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

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

# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "Europe/Paris"
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

APP_DATA = env("APP_DATA")

STATIC_URL = "/static/"
STATIC_ROOT = env("STATIC_ROOT")
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

# Medias
MEDIA_URL = "/media/"
MEDIA_ROOT = APP_DATA / "media"

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "[%(asctime)s - %(levelname)s - %(processName)s/%(module)s.%(funcName)s:%(lineno)d] %(message)s",
        },
    },
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "default",
        },
    },
    "loggers": {
        "django.db.backends": {
            "handlers": ["console"],
            "level": "INFO",  # set to DEBUG for SQL log
            "propagate": False,
        },
        "root": {
            "handlers": ["console"],
            "level": "WARNING",
            "propagate": False,
        },
    },
}

for app in CUSTOM_APPS:
    LOGGING["loggers"][app] = {
        "handlers": ["console"],
        "level": env("LOG_LEVEL"),
        "propagate": False,
    }

DEBUG_TOOLBAR_CONFIG = {
    "SHOW_TOOLBAR_CALLBACK": "charasheet.middleware.debug_toolbar_bypass_internal_ips",
    "RESULTS_CACHE_SIZE": 100,
}

# Authentication configuration.
AUTHENTICATION_BACKENDS = ("django.contrib.auth.backends.ModelBackend",)

LOGOUT_REDIRECT_URL = "/"
LOGIN_REDIRECT_URL = "/"
LOGIN_URL = "login"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
AUTH_USER_MODEL = "common.User"

ACCOUNT_ACTIVATION_DAYS = 2
REGISTRATION_OPEN = env("REGISTRATION_OPEN")

ANYMAIL = {
    "MAILGUN_API_KEY": env("MAILGUN_API_KEY"),
    "MAILGUN_SENDER_DOMAIN": env("MAILGUN_SENDER_DOMAIN"),
}
EMAIL_BACKEND = "anymail.backends.mailgun.EmailBackend"
DEFAULT_FROM_EMAIL = "charasheet@mg.augendre.info"
SERVER_EMAIL = "charasheet@mg.augendre.info"

if DEBUG:
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

APP = {
    "build": {
        "date": "latest-date",
        "commit": "latest-commit",
        "describe": "latest-describe",
    },
}
try:
    with Path("/app/git/build-date").open() as f:
        APP["build"]["date"] = f.read().strip()
except Exception:  # noqa: S110
    pass
try:
    with Path("/app/git/git-commit").open() as f:
        APP["build"]["commit"] = f.read().strip()
except Exception:  # noqa: S110
    pass
try:
    with Path("/app/git/git-describe").open() as f:
        APP["build"]["describe"] = f.read().strip()
except Exception:  # noqa: S110
    pass
