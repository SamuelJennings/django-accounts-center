# Quickstart: Allauth Signup Page

**Feature**: 001-allauth-signup-page
**Package**: `django-accounts-center`
**Target**: Developers integrating django-allauth with a styled signup page

---

## Prerequisites

- Django 5.2+
- django-allauth v65+ installed and configured
- django-mvp installed and configured (AdminLTE4 + Bootstrap 5 shell)
- django-cotton configured as a template engine
- crispy-bootstrap5 installed

---

## Setup (5 Lines or Fewer)

### 1. Add to `INSTALLED_APPS`

```python
INSTALLED_APPS = [
    # ... your existing apps ...
    "dac",
    "dac.addons.allauth",
    # allauth apps (already required)
    "allauth",
    "allauth.account",
    # optional — enables social provider buttons on signup page:
    "allauth.socialaccount",
]
```

### 2. Include allauth URLs

If not already done:

```python
# urls.py
from django.urls import path, include

urlpatterns = [
    # ...
    path("accounts/", include("allauth.urls")),
]
```

### 3. Visit the Signup Page

Navigate to `/accounts/signup/`. The page will render with:

- The django-mvp AdminLTE4 visual shell (CSS, fonts, Bootstrap 5)
- A centered card containing the signup form
- Field set determined by your active allauth settings
- Social provider buttons (if `allauth.socialaccount` is enabled and providers are configured)

---

## Configuration Reference

The signup page adapts automatically to allauth settings. No additional configuration is needed beyond your existing allauth setup.

### Field Visibility

| Setting | Effect |
|---|---|
| `ACCOUNT_USERNAME_REQUIRED = True` | Shows username field |
| `ACCOUNT_EMAIL_REQUIRED = True` | Shows email field |
| `ACCOUNT_EMAIL_CONFIRMATION_REQUIRED = True` | Shows confirm email field |
| `ACCOUNT_SIGNUP_PASSWORD_ENTER_TWICE = True` | Shows confirm password field |
| `ACCOUNT_SIGNUP_FORM_CLASS = "myapp.forms.MySignupForm"` | Appends custom fields |

### Social Providers

Social buttons appear automatically when:

1. `allauth.socialaccount` is in `INSTALLED_APPS`
2. At least one provider is configured in `SOCIALACCOUNT_PROVIDERS`

```python
# Example — Google provider
SOCIALACCOUNT_PROVIDERS = {
    "google": {
        "APP": {
            "client_id": "your-client-id",
            "secret": "your-client-secret",
        }
    }
}
```

### Disabling Signup

To display a "Signup is closed" message instead of the form, override `is_open_for_signup` in a custom adapter:

```python
# myapp/adapter.py
from allauth.account.adapter import DefaultAccountAdapter

class MyAccountAdapter(DefaultAccountAdapter):
    def is_open_for_signup(self, request):
        return False  # or any logic

# settings.py
ACCOUNT_ADAPTER = "myapp.adapter.MyAccountAdapter"
```

---

## Customization

### Override the Entire Signup Page

Create `templates/account/signup.html` in your project. Django's template loader will use your file instead of the addon's version.

### Override Just the Social Provider Buttons

Create `templates/socialaccount/snippets/provider_list.html` in your project:

```html
{# templates/socialaccount/snippets/provider_list.html #}
{% load socialaccount %}
{% get_providers as providers %}
{% for provider in providers %}
  {% provider_login_url provider process="signup" as href %}
  {# Your custom button markup: #}
  <a href="{{ href }}" class="btn btn-dark w-100 mb-2">
    Continue with {{ provider.name }}
  </a>
{% endfor %}
```

### Override the Entrance Layout

Create `templates/allauth/layouts/entrance.html` in your project to change the centering, background, or card width for ALL allauth entrance pages (signup, login, password reset, etc.).

---

## Template Component Map

| UI Section | Cotton Component | Override Path |
|---|---|---|
| Page outer container | `<c-card>` (django-mvp) | `account/signup.html` |
| Social provider buttons | `<c-button>` (cotton_bs5) | `socialaccount/snippets/provider_list.html` |
| "or" divider | `<c-divider>` (django-mvp) | `account/signup.html` |
| Form fields | `<c-form.render>` (django-mvp) | `account/signup.html` |
| Submit button | `<c-button>` (cotton_bs5) | `account/signup.html` |
| Flash messages | `<c-messages>` (django-mvp) | `allauth/layouts/entrance.html` |
| Passkey signup button | `<c-button>` (cotton_bs5) | `account/signup.html` |

---

## Assumptions

- `allauth.account.middleware.AccountMiddleware` is in `MIDDLEWARE` (required by allauth v65+).
- `crispy_forms` and `crispy_bootstrap5` are in `INSTALLED_APPS`.
- `CRISPY_TEMPLATE_PACK = "bootstrap5"` is set.
- Django Sites framework (`django.contrib.sites`) is in `INSTALLED_APPS` and `SITE_ID` is set.
