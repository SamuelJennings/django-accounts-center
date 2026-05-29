# Research: User Sessions Management Templates

**Feature**: 010-usersessions-templates
**Status**: Complete — all unknowns resolved

## Summary

All core implementation patterns are established in prior specs (001–009). Five
targeted research areas were resolved: the allauth `ListUserSessionsView` context API,
the `ManageUserSessionsForm` bulk sign-out mechanism, the Bootstrap table approach
(no `<c-table>` component), the user-agent truncation strategy, and the component
variant decisions confirmed from existing templates.

## Decisions

### Decision 1: Template inheritance fix strategy

**Decision**: Change only `usersessions/base_manage.html` extends line to `dac/base.html`;
leave `usersession_list.html` extends line untouched.
**Rationale**: The single-point fix propagates the DAC layout to all descendants
without requiring `usersession_list.html` to be changed independently for layout reasons.
Minimises diff surface area per Principle V (keep changes minimal and focused).
Identical approach to the `account/base_manage.html` fix in spec 006 and
`socialaccount/base_manage.html` fix in spec 009.
**Alternatives considered**: Flatten `usersession_list.html` to extend `dac/base.html`
directly — rejected as unnecessary when the base template fix achieves the same result.

### Decision 2: ManageUserSessionsForm bulk sign-out mechanism

**Decision**: The sign-out form POSTs with no session-specific fields — just CSRF.
When `session_count > 1`, the form action is `{% url 'usersessions_list' %}`;
`ListUserSessionsView.form_valid()` signs out all non-current sessions automatically.
When `session_count` is 1, the form action is `{% url 'account_logout' %}`, effectively
logging the user out of their only session.
**Rationale**: Confirmed by inspection of the existing allauth template: it has no
`name` attribute on the submit button and no hidden session PK fields in the body.
`ManageUserSessionsForm` accepts an empty POST (beyond CSRF) and handles all session
termination logic in the view. No per-session fields are needed in the template.
**Alternatives considered**: Per-session hidden PK fields — rejected because the
`ManageUserSessionsForm` does not require them for bulk sign-out, and per-session
selection was explicitly rejected in the spec clarification (Q1: bulk-only).

### Decision 3: Bootstrap table inside `<c-card>` (no `<c-table>` component)

**Decision**: Render the sessions list as a raw Bootstrap `<table class="table">` placed
directly inside a `<c-card>` wrapper. No `<c-table>` Cotton component exists in this project.
**Rationale**: No `<c-table>` component is available in django-mvp, django-cotton-bs5,
or the DAC custom component set. A Bootstrap table is the correct raw-HTML approach per
Principle IX's exemption for genuinely one-off, non-reusable markup. The sessions list
is the only table in the entire addon; there is no reuse case that would justify a
custom component.
**Alternatives considered**: Custom `<c-table>` Cotton component — rejected because
there is no other table in the addon; creating a component for a single use site would
violate Principle IX's guidance against custom components without strong reuse
justification.

### Decision 4: User-agent column truncation

**Decision**: Display `session.user_agent` as-is, wrapped in a `<span class="text-truncate d-inline-block">`
(or equivalent container with Bootstrap's `text-truncate` utility and a max-width constraint)
to cap the column width and prevent layout overflow. No parsing or extraction of browser
name is performed in the template.
**Rationale**: Parsing user-agent strings requires a third-party library or a custom
template filter, neither of which exists in the project. `text-truncate` is a built-in
Bootstrap utility that requires zero additional dependencies and is consistent with how
long strings are handled elsewhere in the project. Confirmed by user clarification (Q2).
**Alternatives considered**: Parse browser name with a template filter — rejected because
no such filter exists and introducing one would be out of scope. Full raw string without
truncation — rejected because raw user-agent strings cause horizontal overflow on mobile viewports.

### Decision 5: Component variants

**Decision**: Use `<c-badge variant="success">` for the "Current" session indicator and
`<c-button variant="primary">` for the sign-out form submit button.
**Rationale**:

- `success` (green) for the badge: signals the current session is active and healthy;
  consistent with `<c-badge variant="success">` already used in `account/email.html`
  for "Verified" email addresses. Confirmed by user clarification (Q5).
- `primary` (blue) for the button: standard call-to-action; no special severity signal.
  Sign-out of other sessions is moderately consequential but not irreversible at the
  account level; a primary button communicates a standard action. Confirmed by user
  clarification (Q3).
**Alternatives considered**: `danger` for button — rejected by user; `warning` for
button — rejected by user; `primary` for badge — rejected because `success` is already
the established convention for active/verified states in the addon.

### Decision 6: Page heading via `{% block title %}`, not `{% block breadcrumbs %}`

**Decision**: The visible "Sessions" page heading is rendered via `{% block title %}`.
`{% block breadcrumbs %}` is NOT overridden by `usersession_list.html`.
**Rationale**: Inspection of `dac/base.html` reveals that `{% block breadcrumbs %}`
wraps the entire breadcrumbs toolbar — it is not the heading slot. The actual page
title/heading appears in `{% block title %}`, which is rendered inside `<c-mvp.toolbar>` →
`<c-slot name="title">`. This is the same pattern used by `connections.html` (spec 009),
`email.html` (spec 006), and all other DAC management pages. The spec clarification (Q4)
confirmed that a visible heading is required; the mechanism is `{% block title %}`.
**Alternatives considered**: Overriding `{% block breadcrumbs %}` to add a heading —
rejected because `breadcrumbs` wraps the breadcrumbs region, not a heading slot. Adding
a heading there would produce a second toolbar-level element outside the expected structure.

## Prior Art (Established Patterns)

| Pattern | Established in |
|---|---|
| `{% extends "dac/base.html" %}` chain fix on base_manage | Spec 006 (`account/base_manage.html`) |
| `{% block title %}` for visible page heading | Spec 006 (`account/email.html`) |
| `{% block page.breadcrumbs %}` with `{{ block.super }}` + item | Spec 006 (`account/email.html`) |
| `{% block page.content %}` override | Spec 005 (`dac/base.html` contract) |
| `<c-badge variant="success">` for active/verified states | Spec 006 (`account/email.html`) |
| `<c-button variant="danger">` for destructive inline forms | Spec 009 (`socialaccount/connections.html`) |
| `<c-card>` as content section wrapper | Spec 006 (`account/email.html`) |
| Integration test pattern for allauth addon views | Spec 006 (`test_email_management_view.py`) |
| Screenshot test pattern (N states × 2 viewports: desktop + mobile) | Spec 006 (`test_email_management_screenshots.py`) |
| Bootstrap table inside `<c-card>` (no `<c-table>`) | N/A — first use; pattern established here |
