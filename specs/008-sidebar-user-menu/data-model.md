# Data Model: Sidebar User Menu Component

**Feature**: `008-sidebar-user-menu`
**Date**: 2026-05-18

---

## Component Identity

**Cotton tag**: `<c-dac.user-menu>`
**Template file**: `dac/templates/cotton/dac/user-menu.html`
**Scope**: Custom Cotton component (third priority per Constitution Principle IX)
**Reuse justification**: The component encapsulates a non-trivial combination of
trigger + dropup + avatar + CSRF logout form that appears in every host application
sidebar. Extracting it prevents duplication and ensures consistent behaviour across
all DAC-based projects.

---

## Props (c-vars)

**None.** The component is zero-configuration. All user data is sourced directly from
`request.user` at render time. There is no `<c-vars>` declaration in the template;
unknown attributes passed by a caller are ignored.

| Data Source | Template Expression | Description |
|---|---|---|
| `request.user` | `{{ request.user }}` | Username (Django's `User.__str__`) displayed in the trigger |
| `request.user.email` | `{{ request.user.email }}` | Email address displayed as a muted secondary line |
| (avatar) | `<c-avatar size="sm" />` | Avatar resolved internally by `<c-avatar>` via its `avatar_url` tag |

---

## Slots

| Slot | Named? | Description |
|---|---|---|
| Default (`{{ slot }}`) | No | Custom menu items injected by the developer. Renders between the Account Center link and the Logout button inside the dropup panel. Each item SHOULD use `<c-dropdown.item>` for visual consistency. |

---

## Internal Layout Structure

### Trigger Element (always visible)

```
┌────────────────────────────────────────┐
│ [Avatar]  {{ request.user }}           │
│           {{ request.user.email }}     │
└────────────────────────────────────────┘
↑ Sidebar footer — `<c-sidebar.footer>` wraps this
```

The trigger is a `<c-button>` rendered inside the `button` named slot of
`<c-dropdown direction="up">`. The button carries `data-bs-toggle="dropdown"`,
`aria-expanded="false"`, and `aria-haspopup="true"`. The avatar is rendered via
`<c-avatar size="sm" />` with no `src`; the avatar component resolves the URL
internally.

### Dropup Panel (opens on trigger click)

```
┌────────────────────────────────────────┐  ↑ opens upward
│  ⚙  Account Center                    │  ← FR-004 (always shown when URL registered)
├────────────────────────────────────────┤
│  [Developer's custom slot items]       │  ← FR-006 (default slot)
├────────────────────────────────────────┤
│  ↩  Log out                           │  ← FR-005 (POST form, always shown)
└────────────────────────────────────────┘
```

*Note*: There is no non-clickable user info header in the dropup panel. User
information (avatar, username, email) appears only in the trigger button.

---

## URL Dependencies

| URL Name | Source | Used For | Degradation |
|---|---|---|---|
| `account-center` | `dac.urls` | Account Center link in dropup | Hidden if not registered |
| `account_logout` | `allauth.urls` | Logout form action | Hidden if not registered |

Both URLs are resolved using `{% url '...' as var %}` (assignment form) to suppress
`NoReverseMatch` exceptions when the URL is not available in the host application.

---

## Rendering Guards

| Condition | Behaviour |
|---|---|
| `request.user.is_authenticated` is `False` | Component renders nothing |
| `account-center` URL not registered | Account Center `<c-dropdown.item>` is omitted |
| `account_logout` URL not registered | Logout form is omitted |
| Developer passes no custom slot content | `{{ slot }}` renders nothing; no empty spacers |

---

## Test Entities

| Test Class | Location | Coverage |
|---|---|---|
| `TestDacUserMenu` | `tests/test_components/test_dac_base.py` | Component rendering, props, slots, guards |
| Screenshot tests | `screenshots/test_user_menu_screenshots.py` | 3 states × 3 viewports = 9 PNGs |
