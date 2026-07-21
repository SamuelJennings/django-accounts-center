# Data Model: Allauth Password Change Templates

**Feature**: `007-allauth-password-change`
**Date**: 2026-05-12

## Overview

This feature involves no Django model changes. The data model section describes the
template block hierarchy and the allauth context variables consumed by each template.

## Template Inheritance Chain

```
dac/base.html                          ← DAC management shell (sidebar, breadcrumbs, card-stack)
  └── account/base_manage.html         ← one-line extends (already correct)
        └── account/base_manage_password.html  ← one-line extends (already correct)
              ├── account/password_change.html  ← REWRITE
              └── account/password_set.html     ← REWRITE

allauth/layouts/entrance.html          ← allauth entrance shell
  └── account/base_entrance.html       ← one-line extends (unchanged)
        └── account/base_reauthenticate.html   ← REWRITE (Cotton)
              ├── account/reauthenticate.html   ← REWRITE (Cotton)
              ├── mfa/reauthenticate.html        ← NOT IN SCOPE (unchanged)
              └── mfa/webauthn/reauthenticate.html  ← NOT IN SCOPE (unchanged)
```

## Context Variables by Template

### `password_change.html`

| Variable | Type | Source | Notes |
|---|---|---|---|
| `form` | `ChangePasswordForm` | `PasswordChangeView` | Fields: `oldpassword`, `password1`, `password2` |
| `redirect_field` | HTML string | allauth mixin | Hidden `<input>` for next-URL redirect |

### `password_set.html`

| Variable | Type | Source | Notes |
|---|---|---|---|
| `form` | `SetPasswordForm` | `PasswordSetView` | Fields: `password1`, `password2` |
| `redirect_field` | HTML string | allauth mixin | Hidden `<input>` for next-URL redirect |

### `base_reauthenticate.html` / `reauthenticate.html`

| Variable | Type | Source | Notes |
|---|---|---|---|
| `form` | `ReauthenticateForm` | `ReauthenticateView` | Single password field |
| `redirect_field` | HTML string | allauth mixin | Hidden `<input>` for next-URL redirect |
| `reauthentication_alternatives` | list | `ReauthenticateView` | Each item has `.url` and `.description`; may be empty |

## Block Contracts

### Management templates (via `dac/base.html`)

| Block name | Required? | Content |
|---|---|---|
| `title` | Yes | Localised page title string |
| `page.breadcrumbs` | Yes | `{{ block.super }}` + `<c-navigation.breadcrumbs.item>` leaf |
| `page.content` | Yes | `<c-form>` wrapping form fields and actions |

### Entrance templates (via `base_entrance.html`)

| Block name | Required? | Content |
|---|---|---|
| `title` | Yes | Localised page title ("Confirm Access") |
| `content` | Yes (in base) | Heading, intro paragraph, `{% block reauthenticate_content %}`, alternatives |
| `reauthenticate_content` | Yes (child) | `<c-form>` with form fields and submit button |

## URL Names Used

| URL name | Used by | Notes |
|---|---|---|
| `account_change_password` | `password_change.html` | Standard allauth URL |
| `account_set_password` | `password_set.html` | Standard allauth URL |
| `account_reset_password` | `password_change.html` | "Forgot Password?" link |
| `account_reauthenticate` | `reauthenticate.html` | Standard allauth URL |
