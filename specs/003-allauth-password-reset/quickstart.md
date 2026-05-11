# Quickstart: Allauth Password Reset Flow

**Feature**: 003-allauth-password-reset
**Package**: `django-accounts-center`
**Target**: Developers integrating django-allauth with a styled password-reset flow

---

## Prerequisites

- Django 5.2+
- django-allauth v65+ installed and configured
- django-mvp installed and configured (AdminLTE4 + Bootstrap 5 shell)
- django-cotton configured as a template engine
- crispy-bootstrap5 installed

If you completed the [Allauth Login Page quickstart](../../002-allauth-login-page/quickstart.md), `dac.addons.allauth` is already installed — the password-reset flow is included automatically with no additional steps.

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

### 3. Configure an Email Backend

Allauth sends the reset link (or code) by email. For development, use the console backend:

```python
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
```

For production, use a real SMTP backend or a transactional email service.

---

## Standard Link-Based Flow

With the default allauth configuration, the password-reset flow uses four pages:

| URL | Template | Description |
|---|---|---|
| `/accounts/password/reset/` | `account/password_reset.html` | Email-input form |
| `/accounts/password/reset/done/` | `account/password_reset_done.html` | "Check your inbox" confirmation |
| `/accounts/password/reset/key/<uidb36>-<key>/` | `account/password_reset_from_key.html` | New-password form (or invalid-token error) |
| `/accounts/password/reset/key/done/` | `account/password_reset_from_key_done.html` | Success confirmation |

All four use the `<c-entrance>` shell (centred card, logo, background inherited from spec 001).

### Invalid / Expired Token

If a user clicks an expired or already-used reset link, `password_reset_from_key.html` renders the **invalid-token branch** automatically (the `token_fail=True` context variable is set by allauth). The page displays an explanation and an inline link back to `/accounts/password/reset/` — no configuration required.

---

## Code-Based Password Reset (Optional)

When `ACCOUNT_EMAIL_VERIFICATION_BY_CODE_ENABLED = True`, allauth replaces the link-based confirmation with a short-lived numeric code delivered by email. A fifth template is then used:

| URL | Template | Description |
|---|---|---|
| `/accounts/password/reset/by-code/confirm/` | `account/confirm_password_reset_code.html` | Code entry form |

```python
# settings.py
ACCOUNT_EMAIL_VERIFICATION_BY_CODE_ENABLED = True
```

The code-entry page extends `account/base_confirm_code.html` (the shared Cotton base for all code-confirmation flows). It renders:

- A heading: "Enter Password Reset Code"
- A "We've sent a code to `<email>`…" paragraph
- A code-entry form with Confirm, Request new code (when `can_resend`), and Cancel buttons

---

## Page Behaviour Reference

### `account/password_reset.html`

- If the user is already authenticated, the `already_logged_in.html` snippet is shown above the form.
- Submitting any email address (registered or not) redirects to `password_reset_done.html`. Allauth silently discards unrecognised addresses to prevent email enumeration — the template does not indicate success or failure.

### `account/password_reset_from_key.html`

- **Cancel button**: Submits a hidden form that POSTs to `/accounts/logout/` and redirects to `/accounts/login/`. This terminates any mid-reset session.
- `cancel_url` can be set by allauth (e.g. when a social-connect reset is in progress) to override the default cancel destination.

### `account/base_confirm_code.html`

- **"Request new code" button**: Visible when `can_resend=True`. Submits a hidden `#resend` form to the same `action_url` with `action=resend`.
- **Cancel button**: If `cancel_url` is set, it is a plain link. Otherwise it submits a hidden `#logout-from-stage` form.
- **Change address** (collapsible): Visible when `can_change=True`. Renders a `<details>` element with a form to update the recipient email and trigger a new code send.

---

## Customisation

All templates are standard Django template overrides. To customise the appearance or wording:

1. Create a `templates/account/` directory in your project.
2. Copy the relevant template from `dac/addons/allauth/templates/account/`.
3. Edit the copy — your version takes priority via Django's template loader order.

No Python code changes are required for template customisation.
