"""
This settings file is used for static site generation. The set of installed apps and
middlewares is only those needed for static pages. There is a separate adminsettings.py
file that includes the full set of installed apps and middlewares for the admin site.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/


See also https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

"""
from pathlib import Path

import environ
import genericsite.apps

PROJECT = __name__.split(".")[0]
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


#######################################################################################
# SECTION 0: Application definition, settings that should not vary between environments
#######################################################################################
WSGI_APPLICATION = f"{PROJECT}.wsgi.application"
ROOT_URLCONF = f"{PROJECT}.urls"

django_apps = [
    # Standard Django stuff we require
    "django.contrib.contenttypes",
    "django.contrib.redirects",
    "django.contrib.sites",
    "django.contrib.staticfiles",
]

INSTALLED_APPS = [
    "genericsite",
    # 3rd party apps we require
    "django_bootstrap_icons",
    "easy_thumbnails",
    "taggit",
    # Insert the user's stuff here, above Django defaults, in case they
    # want to override default templates.
    # Third party apps:
    "django_distill",
    *django_apps,
]

MIDDLEWARE = [
    # https://docs.djangoproject.com/en/4.2/ref/middleware/#django.middleware.security.SecurityMiddleware
    # "django.middleware.security.SecurityMiddleware",
    # "django.contrib.sessions.middleware.SessionMiddleware",
    # "django.middleware.common.CommonMiddleware",
    # "django.middleware.csrf.CsrfViewMiddleware",
    # "django.contrib.auth.middleware.AuthenticationMiddleware",
    # "django.contrib.messages.middleware.MessageMiddleware",
    # # https://docs.djangoproject.com/en/4.2/ref/clickjacking/
    # "django.middleware.clickjacking.XFrameOptionsMiddleware",
    # Set request.site by checking for a Site where domain is the host header
    "django.contrib.sites.middleware.CurrentSiteMiddleware",
    "genericsite.redirects.TemporaryRedirectFallbackMiddleware",
]

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                # "django.contrib.auth.context_processors.auth",
                # "django.contrib.messages.context_processors.messages",
                "django.template.context_processors.media",
                "django.template.context_processors.static",
                "genericsite.apps.context_defaults",
            ],
        },
    },
]

# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/
LANGUAGE_CODE = "en-US"
TIME_ZONE = "America/New_York"
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

#######################################################################################
# SECTION 1: Settings that can (and maybe should) differ between environments
#######################################################################################

# Get environment settings
env = environ.Env()
DOTENV = BASE_DIR / ".env"
if DOTENV.exists() and not env("IGNORE_ENV_FILE", default=False):
    environ.Env.read_env(DOTENV)

# SECRET_KEY intentionally has no default, and will error if not provided
# in the environment. This ensures you don't accidentally run with an
# insecure configuration in production.
SECRET_KEY = env("SECRET_KEY")
DEBUG = env("DEBUG", default=False)
ALLOWED_HOSTS = env("ALLOWED_HOSTS", default=[])

# Local data written by the app should be kept in one directory for ease of backup.
# In DEV this can be a subdir of BASE_DIR. In production, for single-server setups
# this should be a directory outside BASE_DIR that is backed up on a regular basis.
# For scalable configurations, you should not use local paths but external services
# like S3 and a dedicated database server.
DATA_DIR = Path(env("DATA_DIR", default=BASE_DIR.joinpath("var")))

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/
STATIC_URL = "/static/"
STATIC_ROOT = DATA_DIR / "static"
STATIC_ROOT.mkdir(parents=True, exist_ok=True)
STATICFILES_DIRS = [BASE_DIR / "static"]
MEDIA_URL = "/media/"
MEDIA_ROOT = DATA_DIR / "media"
MEDIA_ROOT.mkdir(parents=True, exist_ok=True)

# ManifestStaticFilesStorage is recommended in production, to prevent outdated
# Javascript / CSS assets being served from cache.
# See https://docs.djangoproject.com/en/4.2/ref/contrib/staticfiles/#manifeststaticfilesstorage
# But for production, you almost certainly should be using a shared storage backend, like:
# https://django-storages.readthedocs.io/en/latest/backends/amazon-S3.html
STORAGES = {
    "default": {
        "BACKEND": env(
            "DEFAULT_STORAGE", default="django.core.files.storage.FileSystemStorage"
        ),
    },
    "staticfiles": {
        "BACKEND": env(
            "STATICFILES_STORAGE",
            default="django.contrib.staticfiles.storage.ManifestStaticFilesStorage",
        ),
    },
}

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases
DB_DIR = DATA_DIR / "db"
DB_DIR.mkdir(parents=True, exist_ok=True)
SQLITE_DB = DB_DIR / "db.sqlite3"
DATABASES = {"default": env.db("DATABASE_URL", default=f"sqlite:///{SQLITE_DB}")}

CACHES = {"default": env.cache("CACHE_URL", default="locmemcache://")}

# Email settings don't use a dict. Add to local vars instead.
# https://django-environ.readthedocs.io/en/latest/#email-settings
EMAIL_CONFIG = env.email_url("EMAIL_URL", default="consolemail://")
vars().update(EMAIL_CONFIG)


# CELERY settings
# If the environment has not provided settings, assume there is no broker
# and run celery tasks in-process. This means you MUST provide
# CELERY_TASK_ALWAYS_EAGER=False in your environment to actually use celery.
CELERY_TASK_ALWAYS_EAGER = env("CELERY_TASK_ALWAYS_EAGER", default=True)
CELERY_TASK_EAGER_PROPAGATES = env("CELERY_TASK_EAGER_PROPAGATES", default=True)
# For development setup, assume default of local redis.
CELERY_BROKER_URL = env("CELERY_BROKER_URL", default="redis://localhost:6379/1")
CELERY_RESULT_BACKEND = env("CELERY_RESULT_BACKEND", default="")
CELERY_TIME_ZONE = TIME_ZONE
try:
    import django_celery_beat

    CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers:DatabaseScheduler"
    INSTALLED_APPS.append("django_celery_beat")
except ImportError:
    pass


# Use rich logging for pretty console logs
# https://www.willmcgugan.com/blog/tech/post/richer-django-logging/
LOG_LEVEL = env("LOG_LEVEL", default="INFO")
LOG_FILE = env("LOG_FILE", default=None)
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {"rich": {"datefmt": "[%X]"}},
    "handlers": {
        "console": {
            "class": "rich.logging.RichHandler",
            "formatter": "rich",
            "level": LOG_LEVEL,
            "rich_tracebacks": True,
        }
    },
    "loggers": {
        "django": {"handlers": ["console"]},
        "": {"handlers": ["console"]},
    },
}
if LOG_FILE:
    LOGGING["handlers"]["file"] = {
        "level": LOG_LEVEL,
        "class": "logging.handlers.TimedRotatingFileHandler",
        "filename": LOG_FILE,
        "when": "W0",  # Rotate weekly on Monday
        "backupCount": 8,
    }
    LOGGING["loggers"][""]["handlers"].append("file")

#######################################################################################
# SECTION 2: App configuration.
#######################################################################################

THUMBNAIL_PROCESSORS = genericsite.apps.THUMBNAIL_PROCESSORS
THUMBNAIL_WIDGET_OPTIONS = genericsite.apps.THUMBNAIL_WIDGET_OPTIONS
THUMBNAIL_DEBUG = DEBUG

TINYMCE_DEFAULT_CONFIG = genericsite.apps.TINYMCE_CONFIG

#######################################################################################
# SECTION 3: DEVELOPMENT: If running in a dev environment, loosen restrictions
# and add debugging tools.
#######################################################################################
SITE_ID = env("SITE_ID", default=None, cast=int)

# Rich test output
TEST_RUNNER = "django_rich.test.RichRunner"

if DEBUG:
    ALLOWED_HOSTS = ["*"]
    # So you don't have to add localhost and/or 127.0.0.1 to your Sites table:
    # But note: if your Django project only serves one site, you can set this outside
    # the DEBUG section. See README for details.
    # SITE_ID = 1

    try:
        import debug_toolbar

        INSTALLED_APPS.append("debug_toolbar")
        MIDDLEWARE.append("debug_toolbar.middleware.DebugToolbarMiddleware")
        INTERNAL_IPS = [
            "127.0.0.1",
        ]
        # See also urls.py for debug_toolbar urls
    except ImportError:
        # Dev tools are optional
        pass
