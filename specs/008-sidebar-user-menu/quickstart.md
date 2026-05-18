# Quickstart: Sidebar User Menu Component

**Feature**: `008-sidebar-user-menu`
**Tag**: `<c-dac.user-menu>`
**File**: `dac/templates/cotton/dac/user-menu.html`

---

## Overview

`<c-dac.user-menu>` renders a dropup user menu at the bottom of the application
sidebar. It displays the logged-in user's avatar, name, and an optional subtitle
line as the always-visible trigger. Clicking the trigger opens a panel upward,
showing the user info again at the top, followed by a link to the Account Center
dashboard and a logout button.

The component is only rendered for authenticated users. For anonymous users it
produces no HTML output.

---

## Prerequisites

- `dac` must be in `INSTALLED_APPS`
- `allauth.urls` must be included in the host application's URL configuration
  (provides `account_logout`)
- `dac.urls` must be included (provides `account-center`)
- The host application must use `django-mvp` for the sidebar layout

---

## Minimal Usage

Override the `app.sidebar.footer` block in your base template (or in a child template
that inherits from `dac/base.html`):

```django
{% block app.sidebar.footer %}
  <c-sidebar.footer>
    <c-dac.user-menu
      display_name="{{ request.user.get_full_name|default:request.user.username }}"
      subtitle="{{ request.user.email }}" />
  </c-sidebar.footer>
{% endblock app.sidebar.footer %}
```

This produces:

- A trigger button at the sidebar bottom showing the user's avatar,
  display name, and email
- A dropup with the Account Center link and a Logout button

---

## With a Profile Photo

Pass the `avatar_url` prop to display a profile image instead of the default SVG icon:

```django
<c-dac.user-menu
  display_name="{{ request.user.get_full_name|default:request.user.username }}"
  subtitle="{{ request.user.email }}"
  avatar_url="{{ request.user.profile.photo.url }}" />
```

---

## Adding Custom Menu Items

Pass custom items as slot content. They appear between the Account Center link and the
Logout button. Use `<c-dropdown.item>` for consistent styling:

```django
<c-dac.user-menu
  display_name="{{ request.user.get_full_name|default:request.user.username }}"
  subtitle="{{ request.user.email }}">

  <c-dropdown.item href="{% url 'settings' %}"
                   text="Settings"
                   icon="gear" />
  <c-dropdown.item href="{% url 'billing' %}"
                   text="Billing"
                   icon="credit-card" />

</c-dac.user-menu>
```

---

## Suppressing Default Items

### Hide the Account Center link

```django
<c-dac.user-menu
  display_name="..."
  :show_account_center="False" />
```

### Hide the Logout button

```django
<c-dac.user-menu
  display_name="..."
  :show_logout="False" />
```

### Show only custom items (no defaults)

```django
<c-dac.user-menu
  display_name="..."
  :show_account_center="False"
  :show_logout="False">
  <c-dropdown.item href="{% url 'my-logout' %}" text="Sign out" />
</c-dac.user-menu>
```

---

## Full Prop Reference

| Prop | Type | Default | Notes |
|---|---|---|---|
| `display_name` | string | `""` | Pass `request.user.get_full_name\|default:request.user.username` |
| `subtitle` | string | `""` | Optional. Email, role, plan name, company, etc. |
| `avatar_url` | string | `""` | URL to profile photo. Empty → SVG icon shown |
| `avatar_size` | string | `"sm"` | Size token: `xs`, `sm`, `md`, `lg`, `xl`, `xxl` |
| `show_account_center` | boolean | `True` | Set `:show_account_center="False"` to hide |
| `show_logout` | boolean | `True` | Set `:show_logout="False"` to hide |
| `class` | string | `""` | Extra CSS classes on the outermost wrapper |

---

## Running Tests

```bash
# Component rendering tests
poetry run pytest tests/test_components/test_dac_base.py -k "UserMenu" -v

# Full test suite
poetry run pytest tests/

# Screenshot tests (requires running dev server)
poetry run pytest screenshots/test_user_menu_screenshots.py -v
```

---

## Implementation Files

| File | Status | Description |
|---|---|---|
| `dac/templates/cotton/dac/user-menu.html` | NEW | Cotton component template |
| `tests/test_components/test_dac_base.py` | EDIT | Add `TestDacUserMenu` test class |
| `screenshots/test_user_menu_screenshots.py` | NEW | Multi-viewport screenshot tests |
