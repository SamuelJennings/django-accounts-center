# Quickstart: Allauth Login Page

**Feature**: 002-allauth-login-page
**Package**: `django-accounts-center`
**Target**: Developers integrating django-allauth with a styled login page

---

## Prerequisites

- Django 5.2+
- django-allauth v65+ installed and configured
- django-mvp installed and configured (AdminLTE4 + Bootstrap 5 shell)
- django-cotton configured as a template engine
- crispy-bootstrap5 installed

If you completed the [Allauth Signup Page quickstart](../../001-allauth-signup-page/quickstart.md), `dac.addons.allauth` is already installed — the login page is included automatically with no additional steps.

---

## Setup (If Starting Fresh)

### 1. Add to `INSTALLED_APPS`

```python
INSTALLED_APPS = [
    # ... your existing apps ...
    "dac",
    "dac.addons.allauth",
    # allauth apps (already required)
    "allauth",
    "allauth.account",
    # optional — enables social provider buttons on the login page:
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

### 3. Visit the Login Page

Navigate to `/accounts/login/`. The page renders with:

- The django-mvp AdminLTE4 visual shell (CSS, fonts, Bootstrap 5)
- A centred card with the email/password login form
- A "Forgot your password?" link
- A "Don't have an account? Sign up" cross-link (when signup is open)
- Social provider buttons at the top (if `allauth.socialaccount` is configured)
- Passkey / sign-in code buttons (when the respective features are enabled)

---

## Optional Feature Configuration

The login page adapts automatically to allauth settings. The following settings affect rendered UI:

### Authentication Method

| Setting | Form label |
|---|---|
| `ACCOUNT_AUTHENTICATION_METHOD = "email"` | "Email address" |
| `ACCOUNT_AUTHENTICATION_METHOD = "username"` | "Username" |
| `ACCOUNT_AUTHENTICATION_METHOD = "username_email"` | "Username or Email" |

### "Remember Me" Checkbox

| Setting | Effect |
|---|---|
| `ACCOUNT_SESSION_REMEMBER = None` (default) | "Remember me" checkbox is shown |
| `ACCOUNT_SESSION_REMEMBER = True` | Checkbox hidden; always remembers |
| `ACCOUNT_SESSION_REMEMBER = False` | Checkbox hidden; never remembers |

### Social Providers

Social buttons appear at the top of the login card automatically when:

1. `allauth.socialaccount` is in `INSTALLED_APPS`
2. At least one provider is configured in `SOCIALACCOUNT_PROVIDERS`

When `SOCIALACCOUNT_ONLY = True`, the email/password form and the passkey/code alternatives are hidden — only social buttons are shown.

### Sign-In by Code (passwordless)

Enable the "Send me a sign-in code" button:

```python
ACCOUNT_LOGIN_BY_CODE_ENABLED = True
```

When enabled:

- A "Send me a sign-in code" button appears below the password form.
- Navigating it shows the `account/request_login_code.html` page.
- After submitting email, the `account/confirm_login_code.html` page prompts for the code.

### Passkey Login (WebAuthn)

Enable the "Sign in with a passkey" button:

```python
# settings.py
INSTALLED_APPS = [
    ...,
    "allauth.mfa",
]

MFA_WEBAUTHN_ALLOW_INSECURE_ORIGIN = False  # Must be True only in local dev over HTTP
```

When `allauth.mfa` is installed with WebAuthn configured, a passkey login button appears below the password form. The WebAuthn browser dialog is triggered on click via an injected script.

---

## Customisation

### Changing the Entrance Shell

The login page uses the same `<c-entrance>` Cotton component as the signup page. Override it by creating matching templates in your project's `templates/` directory:

| File to create | Effect |
|---|---|
| `templates/cotton/entrance/background.html` | Change page background colour, gradient, or image |
| `templates/cotton/entrance/logo.html` | Replace the default DAC logo with your own |
| `templates/cotton/entrance/index.html` | Full control of the entrance card structure |

Example — dark background:

```html
{# templates/cotton/entrance/background.html #}
<div class="bg-dark bg-gradient min-vh-100">{{ slot }}</div>
```

Example — custom logo:

```html
{# templates/cotton/entrance/logo.html #}
{% load static %}
<img src="{% static 'myapp/logo.svg' %}" alt="My App" style="height: 80px;" class="d-block mx-auto" />
```

### Overriding a Specific Login Template

Override any template by creating it at the same path within your project's `templates/` directory (must appear before `dac.addons.allauth` in `INSTALLED_APPS`'s template resolution):

| Template | Purpose |
|---|---|
| `account/login.html` | Main login form page |
| `account/request_login_code.html` | Request a sign-in code by email |
| `account/confirm_login_code.html` | Enter the received sign-in code |

---

## Screenshot Tests

To regenerate the visual regression screenshots:

```bash
pytest screenshots/ -v
```

This requires Playwright to be installed and browsers downloaded:

```bash
playwright install chromium
```

Screenshots are written to `docs/_static/{desktop,tablet,mobile}/` and cover all supported feature flag permutations.
