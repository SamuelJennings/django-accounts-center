# Data Model: Allauth Email Management Templates

**Feature**: 006-allauth-email-management
**Status**: N/A — no new models or migrations

## Overview

This feature introduces no new Python models, database tables, or Django settings.
All data is supplied by existing allauth views as template context variables.

## Template Context Entities

These are the runtime context objects consumed by the four templates being modified.
They are provided by allauth's `EmailView` and `VerifiedEmailRequiredView` — no
changes to views are required.

### EmailAddress (allauth model)

Represents one of a user's email addresses.

| Attribute | Type | Used in template |
|---|---|---|
| `email` | `str` | Display value, hidden input `value`, disabled input `value` |
| `primary` | `bool` | Controls "Primary" badge visibility and remove-button disabled state |
| `verified` | `bool` | Controls "Verified"/"Unverified" badge and "Re-send verification" action |

### EmailAddressRadio (allauth context object, `email.html` only)

Wraps an `EmailAddress` for radio-button rendering in the multi-email list.

| Attribute | Type | Used in template |
|---|---|---|
| `emailaddress` | `EmailAddress` | The wrapped address |
| `checked` | `bool` | Radio button initial state |
| `id` | `str` | Radio button `id` attribute |

### Template Context Variables

| Variable | Type | Present in | Description |
|---|---|---|---|
| `emailaddresses` | `QuerySet[EmailAddress]` | `email.html`, `email_change.html` | All addresses for the current user |
| `emailaddress_radios` | `list[EmailAddressRadio]` | `email.html` | Radio-wrapped list |
| `can_add_email` | `bool` | `email.html` | Whether user can add another address |
| `current_emailaddress` | `EmailAddress \| None` | `email_change.html` | Current primary address |
| `new_emailaddress` | `EmailAddress \| None` | `email_change.html` | Pending (unverified) new address |
| `form` | `AddEmailForm \| ChangeEmailForm` | `email.html`, `email_change.html` | The active form |

## Block Contract

All four templates consume the block hierarchy exposed by `dac/base.html`:

| Block name | Required override | Default in `dac/base.html` |
|---|---|---|
| `title` | Recommended | (empty string) |
| `page.breadcrumbs` | Recommended | Single "Account Center" item |
| `page.content` | Yes (content goes here) | "Coming soon…" |
| `extra_js` | Optional | (empty) |

## State Transitions

No state transitions (no workflow or FSM). Template rendering is conditional on
the presence/absence of context variables — pure read-only view rendering.
