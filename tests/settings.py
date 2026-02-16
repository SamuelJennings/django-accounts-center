"""
Test-specific Django settings.

This module provides a stable, minimal configuration for testing that won't be
affected by changes to example.settings during development.

Tests should use this as the base configuration and override specific settings
when testing optional features like passkeys, MFA, or social login.
"""

from pathlib import Path

BASE_DIR = Path(__file__).resolve(strict=True).parent.parent

SECRET_KEY = "test-secret-key-for-testing-only"

DEBUG = True

ALLOWED_HOSTS = ["*"]

USE_I18N = True

# Minimal app configuration for testing
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.sites",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",
    "compressor",
    "example",
    "dac",
    "dac.addons.allauth",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.mfa",
    "allauth.usersessions",
    "easy_icons",
    "crispy_forms",
    "crispy_bootstrap5",
    "flex_menu",
    "django_cotton",
    "cotton_bs5",
]

SITE_ID = 1

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "allauth.account.middleware.AccountMiddleware",
]

ROOT_URLCONF = "example.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
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

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",  # Use in-memory database for faster tests
    }
}

AUTH_PASSWORD_VALIDATORS = []

STATIC_URL = "/static/"
STATIC_ROOT = str(BASE_DIR / "test_static")

STATICFILES_FINDERS = (
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
    "compressor.finders.CompressorFinder",
)

STORAGES = {
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}

COMPRESS_ENABLED = False
COMPRESS_OFFLINE = False

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.dummy.DummyCache",
    },
}

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]

CRISPY_ALLOWED_TEMPLATE_PACKS = ["bootstrap5"]
CRISPY_TEMPLATE_PACK = "bootstrap5"

# ======= Basic Allauth Settings for Tests =======
# Tests start with username/password authentication only
# Individual tests can override these to test optional features

# Basic authentication - username or email
ACCOUNT_AUTHENTICATION_METHOD = "username_email"

# No email verification by default (tests can override)
ACCOUNT_EMAIL_VERIFICATION = "none"

# Disable optional features by default (enable in specific tests)
MFA_PASSKEY_LOGIN_ENABLED = False
ACCOUNT_LOGIN_BY_CODE_ENABLED = False

# Email backend for testing
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

# URL configuration
LOGIN_URL = "/"
LOGIN_REDIRECT_URL = "/account-center/"

# Easy Icons configuration
EASY_ICONS = {
    "default": {
        "renderer": "easy_icons.renderers.ProviderRenderer",
        "config": {"tag": "i"},
        "icons": {
            "arrow-left": "fas fa-arrow-left",
            "home": "fas fa-home",
            "email": "fas fa-envelope",
            "user": "fas fa-user",
            "settings": "fas fa-cog",
            "edit": "fas fa-edit",
            "delete": "fas fa-trash",
            "link": "fas fa-link",
            "sessions": "fas fa-desktop",
            "password": "fas fa-lock",
            "password_change": "fas fa-key",
            "mfa": "fas fa-shield-alt",
            "success": "fas fa-check-circle",
            "info": "fas fa-info-circle",
            "warning": "fas fa-exclamation-triangle",
            "error": "fas fa-times-circle",
            "logout": "fas fa-sign-out-alt",
        },
    },
    "svg": {
        "renderer": "easy_icons.renderers.SvgRenderer",
        "config": {"default_attrs": {"fill": "currentColor"}},
        "icons": {
            "dac": "dac.svg",
            "entrance_check": "check.svg",
            "entrance_warning": "warning.svg",
            "account_center": "dac",
        },
    },
}

# Flex Menu configuration
FLEX_MENUS = {
    "renderers": {
        "dac_sidebar": "dac.renderers.SidebarRenderer",
        "dac_dropdown": "dac.renderers.DropdownRenderer",
    },
    "log_url_failures": DEBUG,
}
