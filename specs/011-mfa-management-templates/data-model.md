# Data Model: MFA Management Templates

**Feature**: 011-mfa-management-templates
**Source**: `allauth.mfa`

## Context Variables by View

No Python changes are required. The templates consume context variables injected by
the existing allauth MFA views.

---

### `mfa/index.html` — `ManageTOTPView` / `IndexView`

| Variable | Type | Description |
|---|---|---|
| `authenticators` | `dict` | Keyed by MFA method type string; values are authenticator instances or empty/falsy |
| `authenticators.totp` | `TOTPAuthenticator \| None` | Active TOTP authenticator for the user, or falsy |
| `authenticators.recovery_codes` | `RecoveryCodesAuthenticator \| None` | Active recovery codes authenticator, or falsy |
| `authenticators.webauthn` | `list[Authenticator]` | List of registered WebAuthn security keys (may be empty) |
| `MFA_SUPPORTED_TYPES` | `list[str]` | Enabled MFA method names, e.g. `["totp", "webauthn", "recovery_codes"]` |
| `is_mfa_enabled` | `bool` | `True` when at least one MFA method is active |

### State Matrix: `mfa/index.html`

| State | `is_mfa_enabled` | `authenticators.totp` | `authenticators.recovery_codes` | `authenticators.webauthn` |
|---|---|---|---|---|
| MFA active (TOTP + RC) | `True` | truthy | truthy | `[]` or non-empty |
| MFA inactive (fresh) | `False` | falsy | falsy | `[]` |

---

### `mfa/totp/activate_form.html`

| Variable | Type | Description |
|---|---|---|
| `form` | `ActivateTOTPForm` | Bound/unbound form with `token` field and `secret` field |
| `form.secret` | `BoundField` | TOTP secret form field; in templates access the raw value via `{{ form.secret.value }}` (Django templates auto-call `.value()` on the BoundField) |
| `totp_svg_data_uri` | `str` | Base64-encoded SVG data URI for the QR code image |

---

### `mfa/totp/deactivate_form.html`

| Variable | Type | Description |
|---|---|---|
| `form` | `DeactivateTOTPForm` | Empty confirmation form (no visible fields) |

---

### `mfa/recovery_codes/index.html`

| Variable | Type | Description |
|---|---|---|
| `can_view_codes` | `bool` | `True` when the user may view their unused codes (requires `is_mfa_enabled=True` and recovery codes authenticator present) |
| `can_download_codes` | `bool` | `True` when the download action is permitted |
| `can_generate_codes` | `bool` | `True` when the generate action is permitted |
| `unused_codes` | `list[str]` | List of unused recovery code strings |
| `total_count` | `int` | Total number of recovery codes (used + unused) |
| `MFA_RECOVERY_CODES_SHOW_ONCE` | `bool` | When `True`, shows "I have saved my codes" checkbox |

---

### `mfa/recovery_codes/generate.html`

| Variable | Type | Description |
|---|---|---|
| `form` | `GenerateRecoveryCodesForm` | Empty confirmation form |
| `unused_code_count` | `int` | Number of existing unused codes (0 when no codes exist yet) |

### State Matrix: `mfa/recovery_codes/generate.html`

| State | `unused_code_count` | Submit button |
|---|---|---|
| No existing codes | 0 | `<c-button>` (default/no variant) |
| Existing codes present | > 0 | `<c-button variant="danger">` |

---

### `mfa/webauthn/authenticator_list.html`

| Variable | Type | Description |
|---|---|---|
| `authenticators` | `list[Authenticator]` | All registered WebAuthn security keys for the user |
| `is_mfa_enabled` | `bool` | `True` when user has at least one active MFA method |

### State Matrix: `mfa/webauthn/authenticator_list.html`

| State | `authenticators` | Rendered |
|---|---|---|
| Keys registered | non-empty list | Bootstrap table with rows; each row has Edit + Remove links |
| No keys registered | `[]` | Empty state message (no table rows) |

### Key Entity: `Authenticator` (WebAuthn)

Template-visible attributes:

| Attribute | Type | Description |
|---|---|---|
| `pk` | `int` | Primary key; used in edit/remove URL routing |
| `name` | `str` | User-supplied display name for the security key |
| `type` | `str` | Authenticator type string, e.g. `"webauthn"` |

---

### `mfa/webauthn/add_form.html`

| Variable | Type | Description |
|---|---|---|
| `form` | `AddWebAuthnAuthenticatorForm` | Form with `passwordless` and `credential` fields |
| `js_data` | `dict` | JSON payload for the WebAuthn onload script |

---

### `mfa/webauthn/edit_form.html`

| Variable | Type | Description |
|---|---|---|
| `form` | `EditWebAuthnAuthenticatorForm` | Form for renaming the security key |
| `authenticator` | `Authenticator` | The authenticator being edited |

---

### `mfa/webauthn/authenticator_confirm_delete.html`

| Variable | Type | Description |
|---|---|---|
| `form` | `DeleteWebAuthnAuthenticatorForm` | Empty confirmation form |
| `authenticator` | `Authenticator` | The authenticator to be removed |

---

## Template Inheritance Chain

```
mfa/index.html
  └── extends mfa/base_manage.html         ← FIXED by FR-001: now extends dac/base.html
        └── extends dac/base.html
              └── extends base.html

mfa/totp/activate_form.html
  └── extends mfa/totp/base.html           (untouched; inherits fix from base_manage)
        └── extends mfa/base_manage.html   ← FIXED

mfa/totp/deactivate_form.html
  └── extends mfa/totp/base.html           (untouched)
        └── extends mfa/base_manage.html   ← FIXED

mfa/recovery_codes/index.html
  └── extends mfa/recovery_codes/base.html (untouched)
        └── extends mfa/base_manage.html   ← FIXED

mfa/recovery_codes/generate.html
  └── extends mfa/recovery_codes/base.html (untouched)
        └── extends mfa/base_manage.html   ← FIXED

mfa/webauthn/authenticator_list.html
  └── extends mfa/webauthn/base.html       (untouched)
        └── extends mfa/base_manage.html   ← FIXED

mfa/webauthn/add_form.html
  └── extends mfa/webauthn/base.html       (untouched)
        └── extends mfa/base_manage.html   ← FIXED

mfa/webauthn/edit_form.html
  └── extends mfa/webauthn/base.html       (untouched)
        └── extends mfa/base_manage.html   ← FIXED

mfa/webauthn/authenticator_confirm_delete.html
  └── extends mfa/webauthn/base.html       (untouched)
        └── extends mfa/base_manage.html   ← FIXED
```

**Before fix**: `mfa/base_manage.html` extended `allauth/layouts/manage.html`,
bypassing `dac/base.html` entirely. All nine content templates rendered with
allauth's default layout — no sidebar, no breadcrumbs, no card-stack.

**After fix**: The full DAC layout chain is restored for all nine content templates
via the single one-line change in `mfa/base_manage.html`.

## URL Names (allauth MFA)

All URL names are registered automatically when `allauth.mfa` is in `INSTALLED_APPS`.
Templates may use them freely without any URL configuration changes.

| URL Name | Path (default) | Template(s) |
|---|---|---|
| `mfa_index` | `/accounts/2fa/` | `mfa/index.html` |
| `mfa_activate_totp` | `/accounts/2fa/totp/activate/` | `mfa/totp/activate_form.html` |
| `mfa_deactivate_totp` | `/accounts/2fa/totp/deactivate/` | `mfa/totp/deactivate_form.html` |
| `mfa_view_recovery_codes` | `/accounts/2fa/recovery-codes/` | `mfa/recovery_codes/index.html` |
| `mfa_generate_recovery_codes` | `/accounts/2fa/recovery-codes/generate/` | `mfa/recovery_codes/generate.html` |
| `mfa_list_webauthn` | `/accounts/2fa/webauthn/` | `mfa/webauthn/authenticator_list.html` |
| `mfa_add_webauthn` | `/accounts/2fa/webauthn/add/` | `mfa/webauthn/add_form.html` |
| `mfa_edit_webauthn` | `/accounts/2fa/webauthn/<pk>/edit/` | `mfa/webauthn/edit_form.html` |
| `mfa_remove_webauthn` | `/accounts/2fa/webauthn/<pk>/remove/` | `mfa/webauthn/authenticator_confirm_delete.html` |
