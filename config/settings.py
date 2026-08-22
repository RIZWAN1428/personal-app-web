"""
Django settings for the personal productivity webapp.
Follows 12-factor principles: all environment-specific values come from .env.
"""
from pathlib import Path
import os
import dj_database_url
import environ

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Initialize django-environ
env = environ.Env(
    DJANGO_DEBUG=(bool, True),
    DJANGO_SECRET_KEY=(str, "django-insecure-dev-fallback-key-change-in-production"),
    DJANGO_ALLOWED_HOSTS=(str, "localhost,127.0.0.1,*"),
)
environ.Env.read_env(BASE_DIR / ".env")

# ---------------------------------------------------------------------------
# CORE SECURITY
# ---------------------------------------------------------------------------
SECRET_KEY = env("DJANGO_SECRET_KEY")
DEBUG = env("DJANGO_DEBUG")

# ALLOWED_HOSTS: comma-separated in .env; fallback to localhost/127.0.0.1
raw_hosts = env("DJANGO_ALLOWED_HOSTS")
ALLOWED_HOSTS = [h.strip() for h in raw_hosts.split(",") if h.strip()]

# Render automatically sets RENDER_EXTERNAL_HOSTNAME in production
render_host = env.str("RENDER_EXTERNAL_HOSTNAME", default="")
if render_host and render_host not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.append(render_host)

if "testserver" not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.append("testserver")

if not ALLOWED_HOSTS:
    ALLOWED_HOSTS = ["localhost", "127.0.0.1", "*"]

# CSRF: needed when deployed behind a domain
CSRF_TRUSTED_ORIGINS = []
raw_csrf = env.str("CSRF_TRUSTED_ORIGINS", default="")
if raw_csrf:
    CSRF_TRUSTED_ORIGINS += [origin.strip() for origin in raw_csrf.split(",") if origin.strip()]
if render_host:
    CSRF_TRUSTED_ORIGINS.append(f"https://{render_host}")

# ---------------------------------------------------------------------------
# APPLICATION DEFINITION
# ---------------------------------------------------------------------------
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Feature apps
    "apps.accounts",
    "apps.notes",
    "apps.checklist",
    "apps.reminders",
    "apps.salah",
    "apps.quran",
    "apps.hadith",
    "apps.books",
    "apps.movies",
    "apps.core",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",  # serves CSS/static files directly, no NGINX needed
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
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

WSGI_APPLICATION = "config.wsgi.application"

# ---------------------------------------------------------------------------
# DATABASE (Neon PostgreSQL in production / dev)
# ---------------------------------------------------------------------------
DATABASES = {
    "default": dj_database_url.config(
        default=f"postgresql://{env.str('POSTGRES_USER', default='personalapp')}:{env.str('POSTGRES_PASSWORD', default='personalapp')}@{env.str('POSTGRES_HOST', default='localhost')}:{env.str('POSTGRES_PORT', default='5432')}/{env.str('POSTGRES_DB', default='personalapp')}",
        conn_max_age=600,
        ssl_require=bool(os.environ.get("DATABASE_URL")),
    )
}

# ---------------------------------------------------------------------------
# CUSTOM USER MODEL & AUTHENTICATION
# ---------------------------------------------------------------------------
AUTH_USER_MODEL = "accounts.User"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator", "OPTIONS": {"min_length": 8}},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LOGIN_URL = "accounts:login"
LOGIN_REDIRECT_URL = "home"
LOGOUT_REDIRECT_URL = "accounts:login"

# ---------------------------------------------------------------------------
# SESSIONS
# ---------------------------------------------------------------------------
SESSION_ENGINE = "django.contrib.sessions.backends.db"
SESSION_COOKIE_AGE = 60 * 60 * 24 * 30  # 30 days
SESSION_SAVE_EVERY_REQUEST = True

# ---------------------------------------------------------------------------
# INTERNATIONALIZATION
# ---------------------------------------------------------------------------
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# ---------------------------------------------------------------------------
# STATIC FILES (CSS) — served by WhiteNoise
# ---------------------------------------------------------------------------
STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

# ---------------------------------------------------------------------------
# MEDIA FILES (User-uploaded PDFs and book assets)
# ---------------------------------------------------------------------------
MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
