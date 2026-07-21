# Quickstart: MFA Management Templates

**Feature**: 011-mfa-management-templates

## Overview

`dac.addons.allauth` ships template overrides for `allauth.mfa` that render all MFA
management pages inside the full DAC Account Center layout — sidebar, breadcrumbs,
card-stack, and consistent headings. This is an automatic override: once `allauth.mfa`
is in `INSTALLED_APPS`, the DAC templates take effect without any additional configuration.

Ten template files are affected: `mfa/base_manage.html` (one-line extends fix) and
nine content templates (full Cotton rewrites removing all `{% element %}` /
`{% endelement %}` / allauth-`{% slot %}` tags).

## Prerequisites

- `dac` installed and wired (see `specs/005-dac-base-template/quickstart.md`)
- `dac.addons.allauth` in `INSTALLED_APPS`
- `allauth.mfa` in `INSTALLED_APPS`
- `allauth.urls` included in your URL configuration

## Setup

```python
# settings.py
INSTALLED_APPS = [
    ...
    "allauth",
    "allauth.account",
    "allauth.mfa",            # ← enable MFA support
    "dac",
    "dac.addons.allauth",     # ← DAC template overrides (includes mfa/)
    ...
]

# Optional: enable supported MFA types
MFA_TOTP_ENABLED = True
MFA_RECOVERY_CODES_ENABLED = True
MFA_WEBAUTHN_ENABLED = True        # requires django-allauth[mfa] extras
```

```python
# urls.py
from django.urls import path, include

urlpatterns = [
    ...
    path("accounts/", include("allauth.urls")),
    # allauth.mfa.urls is included automatically via allauth.urls
    ...
]
```

No additional URL patterns are required.

## What Gets Overridden

| File | Change |
|---|---|
| `mfa/base_manage.html` | `extends` changed from `allauth/layouts/manage.html` to `dac/base.html` |
| `mfa/index.html` | Full Cotton rewrite — 3 × `<c-card>` panels (TOTP, Recovery Codes, WebAuthn) |
| `mfa/totp/activate_form.html` | Full rewrite — `<c-form>` with QR code + secret display |
| `mfa/totp/deactivate_form.html` | Full rewrite — `<c-form>` with danger submit |
| `mfa/recovery_codes/index.html` | Full rewrite — raw textarea + Download/Generate buttons |
| `mfa/recovery_codes/generate.html` | Full rewrite — `<c-form>` with conditional danger submit |
| `mfa/webauthn/authenticator_list.html` | Full rewrite — `<c-card>` + Bootstrap table + `<c-badge>` |
| `mfa/webauthn/add_form.html` | Rewrite — `<c-form>` + preserved WebAuthn JS block |
| `mfa/webauthn/edit_form.html` | Rewrite — `<c-form>` |
| `mfa/webauthn/authenticator_confirm_delete.html` | Rewrite — `<c-form>` with danger submit |

## Out of Scope

The following templates are **not** overridden by this feature. They are login-flow
templates rather than management templates:

- `mfa/base_entrance.html`
- `mfa/authenticate.html`
- `mfa/reauthenticate.html`
- `mfa/trust.html`
- `mfa/webauthn/reauthenticate.html`
- `mfa/webauthn/signup_form.html`

## Template Block Reference

All content templates override `{% block page.content %}`. Additionally:

| Block | Used in | Purpose |
|---|---|---|
| `{% block title %}` | All content templates | Page heading (visible in card-stack title bar) |
| `{% block page.breadcrumbs %}` | All content templates | Appends leaf to "Account Center" trail |
| `{% block page.content %}` | All content templates | Main page content area |
| `{% block extra_js %}` | `recovery_codes/index.html`, `webauthn/add_form.html` | Preserves JS includes |

## Template Context Reference

### All MFA templates

| Variable | Type | Description |
|---|---|---|
| `authenticators` | `dict` | MFA authenticators keyed by type (`totp`, `recovery_codes`, `webauthn`) |
| `MFA_SUPPORTED_TYPES` | `list[str]` | Enabled MFA types |
| `is_mfa_enabled` | `bool` | `True` when user has at least one active method |

### TOTP activate form

| Variable | Type | Description |
|---|---|---|
| `form.secret` | `str` | Raw secret for manual entry |
| `totp_svg_data_uri` | `str` | Base64 SVG data URI for QR code |

### Recovery codes view

| Variable | Type | Description |
|---|---|---|
| `unused_codes` | `list[str]` | Unused code strings |
| `total_count` | `int` | Total code count |

### Recovery codes generate

| Variable | Type | Description |
|---|---|---|
| `unused_code_count` | `int` | Existing unused codes (0 = no codes yet) |

### WebAuthn list / edit / remove

| Variable | Type | Description |
|---|---|---|
| `authenticators` | `list[Authenticator]` | Registered security keys |
| `authenticator` | `Authenticator` | Single key (edit/remove views) |

## Running the Tests

Integration tests (fast, no browser):

```bash
poetry run pytest tests/test_addons/test_allauth/test_mfa_management_view.py --no-cov -v
```

Screenshot tests (requires Playwright browsers installed):

```bash
poetry run pytest screenshots/test_mfa_management_screenshots.py -v
```

Regenerate all screenshots:

```bash
poetry run pytest screenshots/ -v
```

## Page States (22 PNGs)

Each state is captured at desktop (1440×900) and mobile (390×844) = 2 PNGs per state.

| # | State | Screenshot name | Template |
|---|---|---|---|
| 1 | MFA overview — TOTP active + recovery codes set up | `mfa-overview-active` | `mfa/index.html` |
| 2 | MFA overview — nothing active (fresh state) | `mfa-overview-inactive` | `mfa/index.html` |
| 3 | TOTP activate form (with QR code) | `mfa-totp-activate` | `mfa/totp/activate_form.html` |
| 4 | TOTP deactivate confirmation | `mfa-totp-deactivate` | `mfa/totp/deactivate_form.html` |
| 5 | Recovery codes view (with codes) | `mfa-recovery-codes-view` | `mfa/recovery_codes/index.html` |
| 6 | Recovery codes generate confirmation | `mfa-recovery-codes-generate` | `mfa/recovery_codes/generate.html` |
| 7 | WebAuthn key list — with registered keys | `mfa-webauthn-list` | `mfa/webauthn/authenticator_list.html` |
| 8 | WebAuthn key list — empty state | `mfa-webauthn-list-empty` | `mfa/webauthn/authenticator_list.html` |
| 9 | WebAuthn add security key form | `mfa-webauthn-add` | `mfa/webauthn/add_form.html` |
| 10 | WebAuthn edit security key form | `mfa-webauthn-edit` | `mfa/webauthn/edit_form.html` |
| 11 | WebAuthn remove security key confirmation | `mfa-webauthn-remove` | `mfa/webauthn/authenticator_confirm_delete.html` |

PNG paths:

- Desktop: `docs/_static/desktop/mfa-{name}.png`
- Mobile: `docs/_static/mobile/mfa-{name}.png`

## JavaScript Dependencies

Two templates carry hard JS dependencies that must be preserved:

### `mfa/recovery_codes/index.html`

`id="recovery_codes"` on the `<textarea>` is required by
`mfa/recovery_codes/snippets/scripts.html` (copy-to-clipboard functionality).

### `mfa/webauthn/add_form.html`

`id="mfa_webauthn_add"` on the submit button is required by the
`allauth.webauthn.forms.addForm` onload handler. The JSON script block in
`{% block extra_js %}` must be preserved verbatim.
