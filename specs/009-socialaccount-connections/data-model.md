# Data Model: Social Account Connections Templates

**Feature**: 009-socialaccount-connections
**Status**: N/A — no new models or migrations

## Overview

This feature introduces no new Python models, database tables, or Django settings.
All data is supplied by existing allauth views as template context variables.

## Template Context Entities

These are the runtime context objects consumed by the templates being modified.
They are provided by allauth's `ConnectionsView` — no changes to views are required.

### SocialAccount (allauth model)

Represents a user's connected third-party social account.

| Attribute | Type | Used in template |
|---|---|---|
| `pk` | `int` | Hidden form field `value` for disconnect POST |
| `provider` | `str` | Provider identifier (e.g., `"google"`, `"github"`) |
| `get_provider_account()` | `ProviderAccount` | Returns the provider account object for display |

### ProviderAccount (allauth object, returned by `SocialAccount.get_provider_account()`)

Wraps a `SocialAccount` with provider-specific display methods.

| Method/Attribute | Type | Used in template |
|---|---|---|
| `__str__()` / `.to_str()` | `str` | Display name shown in the list item |
| `get_brand()` | `Brand` | Returns brand metadata for the provider |
| `get_brand().name` | `str` | Provider display label shown in the `<c-badge>` |

### DisconnectForm (allauth form, `allauth.socialaccount.forms.DisconnectForm`)

The form passed as `form` by `ConnectionsView`.

| Attribute | Type | Used in template |
|---|---|---|
| `form.accounts` | `QuerySet[SocialAccount]` | Iterated directly to render per-account list items |

**Note**: The form's `account` field (a `ModelChoiceField` with radio widget) is
**not** rendered as a radio group. Instead, `form.accounts` is iterated and each
item's `pk` is submitted as a hidden field in a per-account inline form. The view's
`form.clean()` validates the submitted `account` PK against the user's accounts
queryset, so a hidden PK value is functionally equivalent to a radio selection.

### Template Context Variables

| Variable | Type | Present in | Description |
|---|---|---|---|
| `form` | `DisconnectForm` | `connections.html` | The disconnect form; `form.accounts` is the iterable |
| `form.accounts` | `QuerySet[SocialAccount]` | `connections.html` | Queryset of the user's connected social accounts |

## Block Contract

All management-path templates consume the block hierarchy exposed by `dac/base.html`
(via `socialaccount/base_manage.html` after the extends-line correction):

| Block | Purpose | Default |
|---|---|---|
| `title` | Page title in the toolbar | (empty) |
| `page.breadcrumbs` | Breadcrumb items appended after "Account Center" root | (root only) |
| `page.content` | Main content area inside `card.stack` | "Coming soon…" |

The `authentication_error.html` template uses the entrance layout block hierarchy
(via `socialaccount/base_entrance.html` → `allauth/layouts/entrance.html` → DAC override):

| Block | Purpose |
|---|---|
| `title` | Rendered as the heading inside `<c-entrance name="title">` slot |
| `content` | Body content area below the entrance heading |

## Screenshot States

| State slug | Template | Condition | Viewports |
|---|---|---|---|
| `connections-has-accounts` | `connections.html` | `form.accounts` non-empty | desktop, tablet, mobile |
| `connections-no-accounts` | `connections.html` | `form.accounts` empty | desktop, tablet, mobile |
| `authentication-error` | `authentication_error.html` | N/A (static content) | desktop, tablet, mobile |
