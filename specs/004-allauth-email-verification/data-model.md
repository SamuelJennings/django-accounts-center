# Data Model: Allauth Email Verification Flow

**Feature**: 004-allauth-email-verification  
**Date**: 2026-05-11

---

## Overview

This feature is a pure template-override feature. No new Django models, database
migrations, or Python-level data structures are introduced. All data entities are
owned by django-allauth and are consumed as read-only context variables in templates.

---

## Existing Entities (allauth-owned, consumed read-only)

### EmailAddress

Represents a user's email address in allauth's multi-email system.

| Field | Type | Notes |
|---|---|---|
| `user` | FK → User | The account owner |
| `email` | str | The email address string |
| `verified` | bool | Whether verification has been confirmed |
| `primary` | bool | Whether this is the primary address |

Used in `email_confirm.html` via `confirmation.email_address.email` and
`confirmation.email_address.user`.

### EmailConfirmation

An in-flight email verification record, keyed by a signed token.

| Field | Type | Notes |
|---|---|---|
| `email_address` | FK → EmailAddress | The address being confirmed |
| `key` | str | The signed token embedded in the verification URL |

Used in `email_confirm.html` as the `confirmation` context variable.

**Template-visible properties**:

- `confirmation.email_address.email` — the address string
- `confirmation.email_address.user` — the user object (for `{% user_display %}`)
- `confirmation.key` — the token for the form action URL

### Template Context Variables (per template)

#### `account/verification_sent.html`

*(No allauth-specific context — page is purely informational)*

#### `account/email_confirm.html`

| Variable | Type | Source |
|---|---|---|
| `confirmation` | EmailConfirmation \| None | allauth view |
| `can_confirm` | bool | allauth view (False if key reused/expired or already confirmed by another account) |
| `redirect_field` | HTML | allauth |

#### `account/confirm_email_verification_code.html`

*(Inherits from `base_confirm_code.html`)*

| Variable | Type | Source |
|---|---|---|
| `email` | str | allauth view |
| `verify_form` | Django Form | allauth view |
| `can_resend` | bool | allauth view |
| `cancel_url` | str \| None | allauth view |
| `can_change` | bool | allauth view |
| `change_form` | Django Form \| None | allauth view |
| `redirect_field` | HTML | allauth |

#### `account/account_inactive.html`

*(No allauth-specific context — page is purely informational)*

---

## State Transitions

```
[signup] → ACCOUNT_EMAIL_VERIFICATION="mandatory"
              └→ verification_sent.html (informational, no action)

[click link in email] → email_confirm.html
    ├── can_confirm=True  → confirm form → [verified]
    └── can_confirm=False / no confirmation → invalid-key branch

[ACCOUNT_EMAIL_VERIFICATION_BY_CODE_ENABLED=True, signup]
              └→ confirm_email_verification_code.html
                    ├── valid code → [verified]
                    └── invalid code → inline error (same page)

[login attempt with deactivated account]
              └→ account_inactive.html (terminal, no action)
```
