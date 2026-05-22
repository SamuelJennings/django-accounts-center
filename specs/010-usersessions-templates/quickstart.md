# Quickstart: User Sessions Management Templates

**Feature**: 010-usersessions-templates

## Overview

`dac.addons.allauth` ships template overrides for `allauth.usersessions` that render
the sessions management page inside the full DAC Account Center layout — sidebar,
breadcrumbs, card-stack, and consistent heading. This is an automatic override:
once `allauth.usersessions` is in `INSTALLED_APPS`, the DAC templates take effect
without any additional configuration.

## Prerequisites

- `dac` installed and wired (see `specs/005-dac-base-template/quickstart.md`)
- `dac.addons.allauth` in `INSTALLED_APPS`
- `allauth.usersessions` in `INSTALLED_APPS`
- `allauth.usersessions.urls` included in your URL configuration

## Setup

```python
# settings.py
INSTALLED_APPS = [
    ...
    "allauth",
    "allauth.account",
    "allauth.usersessions",   # ← enable user sessions tracking
    "dac",
    "dac.addons.allauth",     # ← DAC template overrides (includes usersessions/)
    ...
]
```

```python
# urls.py
from django.urls import path, include

urlpatterns = [
    ...
    path("accounts/", include("allauth.urls")),
    # allauth.usersessions.urls is included automatically via allauth.urls
    ...
]
```

No additional URL patterns are required. `allauth.usersessions` registers
`usersessions_list` at `/accounts/sessions/` automatically via `allauth.urls`.

## What Gets Overridden

| File | Location | Change |
|---|---|---|
| `usersessions/base_manage.html` | `dac/addons/allauth/templates/` | `extends` changed from `allauth/layouts/manage.html` to `dac/base.html` |
| `usersession_list.html` | `dac/addons/allauth/templates/usersessions/` | Full rewrite — Cotton components, Bootstrap table, DAC block structure |

## Template Context Reference

The DAC template overrides consume the same context variables as the stock allauth
template — no view changes are required:

| Variable | Type | Description |
|---|---|---|
| `sessions` | `QuerySet[UserSession]` | All active sessions for the current user |
| `session_count` | `int` | Number of active sessions |
| `show_last_seen_at` | `bool` | Enable the "Last Seen" column (off by default) |

To enable last-seen tracking, set in your Django settings:

```python
# settings.py
USERSESSIONS_TRACK_ACTIVITY = True   # enables last_seen_at tracking
```

When `USERSESSIONS_TRACK_ACTIVITY = True`, allauth's middleware sets `show_last_seen_at = True`
in the context and the "Last seen at" column becomes visible.

## Running the Tests

Integration tests (fast, no browser):

```bash
poetry run pytest tests/test_addons/test_allauth/test_usersessions_view.py --no-cov -v
```

Screenshot tests (requires Playwright browsers installed):

```bash
poetry run pytest screenshots/test_usersessions_screenshots.py -v
```

Regenerate all screenshots:

```bash
poetry run pytest screenshots/ -v
```

## Page States

The sessions page has two visible states based on `session_count`:

### Multiple sessions (`session_count > 1`)

- Sessions table with all columns (Last Seen visible only when `show_last_seen_at=True`)
- Current session row has a green "Current" badge
- "Sign Out Other Sessions" button (POSTs to `usersessions_list`)

### Single session (`session_count == 1`)

- Sessions table with one row (the current session)
- "Sign Out" button (POSTs to `account_logout`)
- Clicking sign-out logs the user out

## Screenshot Coverage

Six screenshots are generated automatically by `pytest screenshots/`:

```
docs/_static/desktop/sessions-multiple.png   (1440×900)
docs/_static/desktop/sessions-single.png     (1440×900)
docs/_static/tablet/sessions-multiple.png    (768×1024)
docs/_static/tablet/sessions-single.png      (768×1024)
docs/_static/mobile/sessions-multiple.png    (390×844)
docs/_static/mobile/sessions-single.png      (390×844)
```
