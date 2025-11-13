# Django Account Center

A comprehensive Django package for managing user accounts with a modern, customizable interface built on Bootstrap 5 and Django Cotton components.

## Features

- **Complete Account Management**: Email management, password changes, session management, and MFA support
- **Social Authentication**: Integration with django-allauth for social login providers
- **Payment Integration**: Optional Stripe integration for subscription management
- **Responsive Design**: Built with Bootstrap 5 and Cotton components
- **Flexible Menu System**: Powered by django-flex-menus for customizable navigation
- **Activity Streams**: Optional integration with django-activity-stream for social features
- **Theme Support**: Customizable templates and themes

## Installation

### Using pip

```bash
pip install django-accounts-center
```

### Using Poetry (Development)

```bash
git clone https://github.com/SamuelJennings/django-accounts-center.git
cd django-accounts-center
poetry install
```

## Quick Start

### 1. Add to Django Settings

Add the required packages to your `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    # Django core apps
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.sites",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    
    # Third-party packages
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.mfa",
    "allauth.usersessions",
    "crispy_forms",
    "crispy_bootstrap5",
    "flex_menu",
    "django_cotton",
    "cotton_bs5",
    "easy_icons",
    
    # Django Account Center
    "dac",
    "dac.addons.allauth",
    
    # Optional addons
    "dac.addons.stripe",  # For Stripe integration
    "dac.addons.actstream",  # For activity streams
    
    # Your apps
    "your_app",
]
```

### 2. Configure Authentication

```python
# Authentication backends
AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]

# Crispy forms configuration
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# Site ID (required for allauth)
SITE_ID = 1
```

### 3. Configure URLs

Add the account center URLs to your main `urls.py`:

```python
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("account-center/", include("dac.urls")),
    path("accounts/", include("allauth.urls")),  # For allauth integration
    path("", include("your_app.urls")),
]
```

### 4. Run Migrations

```bash
python manage.py migrate
```
