# Data Model: User Sessions Management Templates

**Feature**: 010-usersessions-templates
**Source**: `allauth.usersessions`

## Context Variables (from `ListUserSessionsView`)

These variables are injected into the template context by `allauth.usersessions.views.ListUserSessionsView`.
No Python changes are required; the templates consume them as-is.

| Variable | Type | Description |
|---|---|---|
| `sessions` | `QuerySet[UserSession]` or `list` | All active sessions for the current user, ordered by `created_at` descending |
| `session_count` | `int` | Total number of active sessions; drives form action URL and button label |
| `show_last_seen_at` | `bool` | When `True`, the "Last Seen" column is rendered; `False` by default |

## Key Entity: `UserSession`

**Module**: `allauth.usersessions.models.UserSession`

Template-visible attributes:

| Attribute | Type | Nullable | Description | Rendering |
|---|---|---|---|---|
| `pk` | `int` | No | Session identifier | Not rendered directly in the list; used in URL routing |
| `created_at` | `datetime` | No | Session start time | `<span title="{{ session.created_at }}">{{ session.created_at\|naturaltime }}</span>` — hover shows full timestamp |
| `ip` | `str` | Yes (empty string) | Originating IP address | Rendered as-is; empty string silently produces empty cell |
| `user_agent` | `str` | Yes (empty string) | Raw browser user-agent string | Rendered with `text-truncate` CSS to cap column width |
| `last_seen_at` | `datetime` | Yes | Last activity timestamp | Only rendered when `show_last_seen_at=True`; same pattern as `created_at` |
| `is_current` | `bool` | No | Whether this session is the one making the current request | Drives `<c-badge variant="success">` ("Current") vs. empty cell |

## Form: `ManageUserSessionsForm`

**Module**: `allauth.usersessions.forms.ManageUserSessionsForm`

The form requires only a CSRF token — no per-session fields. The view handles all
session termination logic.

| Aspect | Value |
|---|---|
| Method | `POST` |
| Action URL (when `session_count > 1`) | `{% url 'usersessions_list' %}` |
| Action URL (when `session_count == 1`) | `{% url 'account_logout' %}` |
| Required POST fields | CSRF token only |
| View handler | `ListUserSessionsView.form_valid()` — signs out all non-current sessions |

## State Matrix

| State | `session_count` | `show_last_seen_at` | Form Action | Button Label | "Last Seen" column |
|---|---|---|---|---|---|
| Multiple sessions | > 1 | `False` | `usersessions_list` | "Sign Out Other Sessions" | Hidden |
| Multiple sessions + last seen | > 1 | `True` | `usersessions_list` | "Sign Out Other Sessions" | Visible |
| Single session | 1 | `False` | `account_logout` | "Sign Out" | Hidden |
| Single session + last seen | 1 | `True` | `account_logout` | "Sign Out" | Visible |

## Template Inheritance Chain

```
usersession_list.html
  └── extends usersessions/base_manage.html
        └── extends dac/base.html          ← FIXED by FR-001
              └── extends base.html
```

**Before fix**: `usersessions/base_manage.html` extended `allauth/layouts/manage.html`,
bypassing `dac/base.html` entirely. The "Sessions" page rendered with allauth's default
layout — no sidebar, no Account Center breadcrumbs, no card-stack.

**After fix**: The full DAC layout chain is restored. All blocks defined in `dac/base.html`
(`breadcrumbs`, `page.breadcrumbs`, `page.content`, `title`) are available to
`usersession_list.html`.
