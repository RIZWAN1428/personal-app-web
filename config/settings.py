"""
Django settings for the Personal App (web version).

WHAT THIS FILE DOES (plain English):
This is the "control panel" for the whole app. It tells Django:
  - which apps (features) are installed
  - how to connect to PostgreSQL
  - which security rules to enforce
  - where static files (CSS) are served from

This is a classic server-rendered Django app: no separate frontend, no
JWT, no CORS. The browser talks directly to Django, and Django's built-in
session-based login handles authentication.
"""

from pathlib import Path

import dj_database_url
import environ

# BASE_DIR points to the project root (where manage.py lives).
BASE_DIR = Path(__file__).resolve().parent.parent

# env() reads values from the .env file sitting next to manage.py.
env = environ.Env()
environ.Env.read_env(BASE_DIR / ".env")

# ---------------------------------------------------------------------------
# CORE / SECURITY
# ---------------------------------------------------------------------------
SECRET_KEY = env("DJANGO_SECRET_KEY")
DEBUG = env.bool("DJANGO_DEBUG", default=False)

# Render gives every service a *.onrender.com hostname automatically.
# RENDER_EXTERNAL_HOSTNAME is injected by Render itself at runtime, so you
# don't have to hard-code your app's URL here.
ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS", default=["localhost", "127.0.0.1"])
if "testserver" not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.append("testserver")
render_hostname = env("RENDER_EXTERNAL_HOSTNAME", default="")
if render_hostname:
    ALLOWED_HOSTS.append(render_hostname)

# CSRF needs to know which origins are trusted to POST forms (login, signup,
# add-note, etc.) — this must include your Render URL (and later, your own
# domain if you add one).
CSRF_TRUSTED_ORIGINS = env.list("CSRF_TRUSTED_ORIGINS", default=[])
if render_hostname:
    CSRF_TRUSTED_ORIGINS.append(f"https://{render_hostname}")

# Render's load balancer terminates HTTPS and forwards plain HTTP internally,
# so Django needs to trust the X-Forwarded-Proto header to know a request was
# really HTTPS (otherwise SECURE_SSL_REDIRECT would redirect-loop forever).
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# These headers/flags harden the app once DEBUG=False (production).
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = "DENY"
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True

# ---------------------------------------------------------------------------
# APPLICATIONS
# ---------------------------------------------------------------------------
# Every "feature" of the app (notes, checklist, reminders...) is its own
# Django app. To add a NEW feature later, you create a new folder under
# apps/ and register it here — that's the whole extension pattern.
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Our apps (feature modules) — add new ones here as you build them
    "apps.accounts",
    "apps.notes",
    "apps.checklist",
    "apps.reminders",
    "apps.salah",
    "apps.quran",
    "apps.hadith",
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
        # Project-wide templates (base.html, home.html) live in templates/
        # at the project root; each app's own templates live inside
        # apps/<name>/templates/ and Django finds those automatically
        # because APP_DIRS is True below.
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
# DATABASE (PostgreSQL, hosted on Neon — see SETUP_MANUAL.md Part 5)
# ---------------------------------------------------------------------------
# You'll set DATABASE_URL to the connection string Neon gives you (both
# locally in .env, and as an environment variable on Render). Locally you
# can instead fall back to the individual POSTGRES_* vars below if you'd
# rather run a local Postgres for development.
#
# Neon pauses its compute after a few minutes of inactivity and closes
# idle connections when it does. CONN_MAX_AGE=0 tells Django to open a
# fresh connection on every request instead of trying to reuse one that
# Neon may have already closed — without this, you'd see intermittent
# "server closed the connection unexpectedly" errors after idle periods.
# CONN_HEALTH_CHECKS makes Django verify a reused connection is still
# alive before using it, as extra insurance.
if env("DATABASE_URL", default=""):
    DATABASES = {
        "default": dj_database_url.parse(env("DATABASE_URL"), conn_max_age=0)
    }
    DATABASES["default"]["CONN_HEALTH_CHECKS"] = True
    # sslmode only makes sense for a real Postgres connection — the
    # sqlite:/// fallback some people use for quick local testing doesn't
    # understand it, so we only add it when we're actually on Postgres.
    if DATABASES["default"]["ENGINE"] == "django.db.backends.postgresql":
        DATABASES["default"].setdefault("OPTIONS", {})
        DATABASES["default"]["OPTIONS"]["sslmode"] = "require"
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": env("POSTGRES_DB", default="personalapp"),
            "USER": env("POSTGRES_USER", default="personalapp"),
            "PASSWORD": env("POSTGRES_PASSWORD", default="personalapp"),
            "HOST": env("POSTGRES_HOST", default="localhost"),
            "PORT": env("POSTGRES_PORT", default="5432"),
            "CONN_MAX_AGE": 60,
        }
    }

# Custom user model: we log in with EMAIL instead of Django's default username.
AUTH_USER_MODEL = "accounts.User"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator", "OPTIONS": {"min_length": 8}},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# Where Django's built-in login_required / LoginView send you.
LOGIN_URL = "accounts:login"
LOGIN_REDIRECT_URL = "home"
LOGOUT_REDIRECT_URL = "accounts:login"

# ---------------------------------------------------------------------------
# INTERNATIONALIZATION
# ---------------------------------------------------------------------------
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"  # store everything in UTC; templates convert to local time in the browser
USE_I18N = True
USE_TZ = True

# ---------------------------------------------------------------------------
# STATIC FILES (CSS) — served by WhiteNoise, no NGINX/CDN needed
# ---------------------------------------------------------------------------
STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"
STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
