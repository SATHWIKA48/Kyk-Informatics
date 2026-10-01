"""
Django settings for the KYK Technologies backend.
"""
import os
from pathlib import Path
import os
import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY: replace with a real secret in production, e.g. via environment variable.
SECRET_KEY = os.environ.get("KYK_SECRET_KEY", "dev-only-secret-change-me")

DEBUG = os.environ.get("KYK_DEBUG", "1") == "1"

ALLOWED_HOSTS = os.environ.get("KYK_ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "corsheaders",
    "leads",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
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

# Default: SQLite for local development. Swap for Postgres in production.
# DATABASES = {
#     "default": {
#         "ENGINE": "django.db.backends.sqlite3",
#         "NAME": BASE_DIR / "db.sqlite3",
#     }
# }
DATABASES = {
    "default": dj_database_url.config(
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
        conn_max_age=600,
    )
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

LOGIN_URL = "/accounts/login/"
LOGIN_REDIRECT_URL = "/dashboard/"
LOGOUT_REDIRECT_URL = "/"

# Dev: password-reset emails print to the terminal instead of actually sending.
# In production, swap this for a real backend (SMTP, SES, SendGrid, etc.).
EMAIL_BACKEND = os.environ.get(
    "KYK_EMAIL_BACKEND", "django.core.mail.backends.console.EmailBackend"
)
DEFAULT_FROM_EMAIL = os.environ.get("KYK_FROM_EMAIL", "no-reply@kykinformatics.com")

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# CORS: allow the KYK frontend (adjust to your deployed frontend origin(s))
CORS_ALLOWED_ORIGINS = os.environ.get(
    "KYK_CORS_ORIGINS",
    "http://localhost:5500,http://127.0.0.1:5500"
).split(",")

# Simple keyword lists used by the AI-domain interest classifier (see leads/utils.py)
KYK_DOMAIN_KEYWORDS = {
    "recruitment": ["hire", "hiring", "recruit", "candidate", "staffing", "talent", "workforce"],
    "software": ["app", "website", "software", "platform", "integration", "api", "portal", "automation"],
    "ai": ["ai", "agi", "asi", "machine learning", "ml", "agent", "generative", "intelligent", "automation"],
}
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
ANTHROPIC_MODEL = os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-4-6")
