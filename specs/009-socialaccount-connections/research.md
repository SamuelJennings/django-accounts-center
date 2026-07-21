# Research: Social Account Connections Templates

**Feature**: 009-socialaccount-connections
**Status**: Complete — all unknowns resolved

## Summary

All core implementation patterns are established in prior specs (001–008). Three
targeted research areas were resolved: the allauth `DisconnectForm` context API,
the correct iteration approach for per-account forms, and the entrance-layout heading
convention used by `authentication_error.html`.

## Decisions

### Decision 1: Template inheritance fix strategy

**Decision**: Change only `socialaccount/base_manage.html` extends line; leave
`connections.html` extends line untouched.
**Rationale**: The single-point fix propagates the DAC layout to all descendants
without requiring `connections.html` to be changed independently for layout reasons.
Minimises diff surface area per Principle V (keep changes minimal and focused).
Identical approach to the `account/base_manage.html` fix in spec 006.
**Alternatives considered**: Flatten `connections.html` to extend `dac/base.html`
directly — rejected as unnecessary when the base template fix achieves the same result.

### Decision 2: Per-account form iteration via `form.accounts`

**Decision**: Iterate over `form.accounts` (the `QuerySet[SocialAccount]` set
directly on the `DisconnectForm` instance) rather than `form.fields.account.choices`
(the radio-button choice tuples used by the original allauth template).
**Rationale**: `form.accounts` is a first-class queryset attribute exposing
`SocialAccount` objects directly. Iterating it avoids the tuple-unpacking pattern
(`acc.0.instance`) required by choice-based iteration and gives cleaner access to
`account.pk` and `account.get_provider_account()`. The `DisconnectForm.clean()` only
requires the `account` field POST value (the PK) to be present; it does not require
radio-button submission specifically.
**Alternatives considered**: `form.fields.account.choices` iteration (original allauth
pattern) — rejected because it requires `acc.0.instance` tuple navigation and was
designed for a radio-select UI, which is replaced by per-account inline forms.

### Decision 3: Per-account form hidden field

**Decision**: Each per-account remove form POSTs `name="account" value="{{ account.pk }}"`
as a hidden `<input>` field to `{% url 'socialaccount_connections' %}`.
**Rationale**: `DisconnectForm` validates the `account` field (a `ModelChoiceField`)
by PK. Any POST with a valid `account` PK for the current user will be accepted by
`form.clean()` and processed by `form.save()` → `flows.connect.disconnect()`.
Submitting a hidden field with the PK is functionally equivalent to submitting a
radio selection and is the correct mechanism for per-item forms.
**Alternatives considered**: Separate delete-style URL with the PK in the path —
rejected because `ConnectionsView` is the canonical disconnect endpoint and
no additional URL is needed.

### Decision 4: `authentication_error.html` — heading handling

**Decision**: Drop the `{% element h1 %}` from `authentication_error.html`'s
`{% block content %}`. Replace only `{% element p %}` with `<c-text>`.
**Rationale**: The `allauth/layouts/entrance.html` override in the DAC addon
(`dac/addons/allauth/templates/allauth/layouts/entrance.html`) uses `<c-entrance>`
which renders the `{% block title %}` content in its `name="title"` slot — the
entrance component handles heading display automatically. The `{% element h1 %}` in
the original `connections.html` duplicated this heading inside the content area. All
other entrance-style templates in the DAC addon (`login_cancelled.html`, `login.html`,
`signup.html`) omit the duplicate h1. Dropping it is consistent with the established
pattern.
**Alternatives considered**: Replace `{% element h1 %}` with a Cotton heading
component — rejected because the entrance layout already renders the title as a
heading; a second heading would be semantically wrong (two h1s on one page).

### Decision 5: List-group structure for `connections.html`

**Decision**: Use `<c-card>` (with title and icon) wrapping a `<c-list flush>`
for the connected-accounts section. Each item is a `<c-list.item>` containing
the account display name, a `<c-badge>` for the provider brand, and an inline `<c-form>`
with a "Remove" `<c-button>`. The "Add a Third-Party Account" section is a separate
`<c-card>` below, including the `provider_list.html` and `login_extra.html` includes.
**Rationale**: Matches the structure established by `email.html` in spec 006 — a card
wrapping a list-group with per-item inline actions. Consistent visual pattern across
all DAC management pages that display lists of associated items.
**Alternatives considered**: Stacked `<c-card>` per account — rejected per spec
clarification (Q2).

## Prior Art (Established Patterns)

| Pattern | Established in |
|---|---|
| `{% extends "dac/base.html" %}` chain fix on base_manage | Spec 006 (`account/base_manage.html`) |
| `<c-list>` + per-item inline form | Spec 006 (`account/email.html`) |
| `<c-badge>` for status/provider labels | Spec 006 (`account/email.html`) |
| `{% block page.content %}` override | Spec 005 (`dac/base.html` contract) |
| `<c-text>` for entrance-page paragraphs | Spec 002 (`login_cancelled.html`) |
| Dropping `{% element h1 %}` (handled by entrance layout) | Spec 002 (`login_cancelled.html`) |
| `<c-form>` for inline forms without card wrapper | Spec 006 (`email.html` per-address forms) |
| Integration test pattern for allauth addon views | Spec 006 (`test_email_management_view.py`) |
| Screenshot test pattern (3 states × 3 viewports) | Spec 006 (`test_email_management_screenshots.py`) |
