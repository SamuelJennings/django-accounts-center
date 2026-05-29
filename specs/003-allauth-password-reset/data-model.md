# Data Model: Allauth Password Reset Flow

**Feature**: 003-allauth-password-reset
**Phase**: 1 — Design artifacts
**Date**: 2026-05-11

---

## Overview

This feature introduces no new database models, migrations, or Python classes. It consists entirely of template rewrites. The "data model" is the set of **runtime entities** — allauth-owned forms and context objects — that the Cotton templates receive and render.

All entities below are **read-only** from the template's perspective. Templates MUST NOT mutate them.

---

## Runtime Entity 1: `ResetPasswordForm`

**Source**: `allauth.account.forms.ResetPasswordForm`
**Present in**: `account/password_reset.html`
**Context key**: `form`

### Fields

| Field name | Type | Description |
|---|---|---|
| `email` | `EmailField` | The email address to send the reset link to |

### Rendering

`<c-form.render form=form />` renders the email field with crispy layout. The template does not need to introspect individual fields.

---

## Runtime Entity 2: `SetPasswordForm`

**Source**: `allauth.account.forms.SetPasswordForm`
**Present in**: `account/password_reset_from_key.html` (valid-token branch only)
**Context key**: `form`

### Fields

| Field name | Type | Description |
|---|---|---|
| `password1` | `PasswordField` | New password |
| `password2` | `PasswordField` | New password confirmation |

### Rendering

`<c-form.render form=form />` renders both password fields. Validation errors (mismatched passwords, weak password) are rendered inline by crispy.

---

## Runtime Entity 3: `ConfirmPasswordResetCodeForm` (code-based flow)

**Source**: allauth internal — form rendered by `ConfirmPasswordResetCodeView`
**Present in**: `account/base_confirm_code.html` (via `confirm_password_reset_code.html`)
**Context key**: `verify_form`

### Fields

| Field name | Type | Description |
|---|---|---|
| `code` | `CharField` | Short-lived numeric reset code delivered by email |

### Rendering

`<c-form.render form=verify_form />` with `unlabeled=True` renders the code input. The template does not need to know the field name.

---

## Runtime Entity 4: `change_form` (code-based flow, optional)

**Source**: allauth internal — form rendered by `ConfirmPasswordResetCodeView` when `can_change=True`
**Present in**: `account/base_confirm_code.html`
**Context key**: `change_form`

### Fields

| Field name | Type | Description |
|---|---|---|
| `email` | `EmailField` | New email address to send the code to |

### Rendering

Rendered inside a `<details>` / `<summary>` collapsible section. Only present when `can_change=True`. `<c-form.render form=change_form />` renders the field.

---

## Runtime Context Variables by Template

### `account/password_reset.html`

| Variable | Type | Always Present | Description |
|---|---|---|---|
| `form` | `ResetPasswordForm` | Yes | Email-input form |
| `redirect_field` | `str` | Yes | HTML hidden `<input>` for next-redirect — render raw |
| `user` | `AnonymousUser \| User` | Yes | Checked for `user.is_authenticated` to conditionally include `already_logged_in.html` |

### `account/password_reset_done.html`

| Variable | Type | Always Present | Description |
|---|---|---|---|
| `user` | `AnonymousUser \| User` | Yes | Checked for `user.is_authenticated` |

### `account/password_reset_from_key.html`

| Variable | Type | Condition | Description |
|---|---|---|---|
| `token_fail` | `bool` | Always | `True` → show invalid-token branch; `False` → show form |
| `form` | `SetPasswordForm` | `token_fail=False` | New-password form |
| `action_url` | `str` | `token_fail=False` | Form POST target (keyed reset URL) |
| `redirect_field` | `str` | `token_fail=False` | Hidden next-redirect input |
| `cancel_url` | `str \| None` | Always | If truthy, Cancel is `<a href=cancel_url>`; if falsy, Cancel submits hidden logout form |

### `account/password_reset_from_key_done.html`

No template-specific context variables; inherits only standard Django context.

### `account/base_confirm_code.html` (shared base)

| Variable | Type | Always Present | Description |
|---|---|---|---|
| `verify_form` | form | Yes | Code entry form (unlabelled code input) |
| `redirect_field` | `str` | Yes | Hidden next-redirect |
| `can_resend` | `bool` | Yes | Show "Request new code" button when True |
| `can_change` | `bool` | Yes | Show collapsible change-address section when True |
| `change_form` | form | When `can_change` | Change-address form |
| `cancel_url` | `str \| None` | Yes | Cancel destination; if absent, hidden logout-from-stage form is rendered |

---

## Template State Machine: `password_reset_from_key.html`

```
Incoming request
  │
  ├─ token_fail = True
  │     → Render: heading ("Bad Token") + invalid-token paragraph with link to password_reset
  │
  └─ token_fail = False
        → Render: heading ("Change Password") + SetPasswordForm + Cancel
              │
              ├─ cancel_url truthy → Cancel = <a href=cancel_url>
              └─ cancel_url falsy  → Cancel submits #logout-from-stage form (POST to account_logout)
```

---

## Template State Machine: `base_confirm_code.html`

```
Always renders:
  - Heading (from {% block title %})
  - "We've sent a code to {{ recipient }}..." paragraph
  - Code entry form (verify_form) with Confirm button

Conditional:
  - can_resend=True → "Request new code" button → submits #resend form
  - cancel_url truthy → Cancel = <a href=cancel_url>
  - cancel_url falsy  → Cancel submits #logout-from-stage form
  - can_change=True → <details> with change_form
```
