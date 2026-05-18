# Component Interface Contract: `<c-dac.user-menu>`

**Feature**: `008-sidebar-user-menu`
**Date**: 2026-05-18
**Refined**: 2026-05-18 — Zero-config redesign: all props removed; data sourced from `request.user`.

---

## Template Source

**File**: `dac/templates/cotton/dac/user_menu.html`

---

## Full Component Template

```django
{# ================================================================= #}
{# <c-dac.user-menu> — Sidebar user menu (dropup)                    #}
{#                                                                   #}
{# Zero-configuration drop-in component. No props required.         #}
{# All user data is read directly from request.user.                #}
{#                                                                   #}
{# Slots:                                                            #}
{#   default – Custom menu items (placed between Account             #}
{#             Center link and Logout button)                        #}
{#                                                                   #}
{# Examples:                                                         #}
{#   Minimal (no configuration needed):                              #}
{#     <c-dac.user-menu />                                           #}
{#                                                                   #}
{#   With custom slot item:                                          #}
{#     <c-dac.user-menu>                                             #}
{#       <c-dropdown.item href="{% url 'settings' %}"               #}
{#                        text="Settings" icon="gear" />             #}
{#     </c-dac.user-menu>                                            #}
{# ================================================================= #}
{% load i18n mvp %}

{% if request.user.is_authenticated %}
  <c-dropdown direction="up"
              min_width="100%"
              dropdown_class="dac-user-menu w-100">
    <c-slot name="button">
      <c-button type="button"
                class="w-100"
                data-bs-toggle="dropdown"
                aria-expanded="false"
                aria-haspopup="true">
        <c-avatar size="sm" />
        <span class="flex-grow-1 overflow-hidden text-start">
          <span class="d-block fw-semibold text-truncate lh-sm">{{ request.user }}</span>
          <span class="d-block small text-muted text-truncate">{{ request.user.email }}</span>
        </span>
      </c-button>
    </c-slot>
    <c-dropdown.item href="{% url "account-center" %}"
                     text="{% trans "Account Center" %}"
                     icon="grid" />
    {{ slot }}
    <c-dropdown.divider />
    <c-dropdown.item text="{% trans "Log out" %}"
                     icon="logout"
                     type="submit"
                     form="logoutForm"
                     class="dropdown-item text-start w-100" />
    {% url 'account_logout' as logout_url %}
    {% if logout_url %}
      <form method="post"
            id="logoutForm"
            action="{{ logout_url }}"
            class="d-block m-0">
        {% csrf_token %}
      </form>
    {% endif %}
  </c-dropdown>
{% endif %}
```

---

## Props

**None.** The component accepts no configuration props. There is no `<c-vars>` block.
Any attributes passed by the caller are silently ignored.

---

## Slots

| Slot | Named? | Description |
|---|---|---|
| Default (`{{ slot }}`) | No | Custom menu items. Placed after the Account Center link and before the Logout button. Use `<c-dropdown.item>` for visual consistency. |

---

## Rendered HTML Contract

### Trigger element

```html
<div class="dropup dac-user-menu w-100">
  <button type="button"
          class="btn ... w-100"
          data-bs-toggle="dropdown"
          aria-expanded="false"
          aria-haspopup="true">

    <!-- Avatar resolved internally by <c-avatar> -->
    <span class="avatar avatar-sm">
      <!-- Photo (if user has a profile photo via avatar_url tag): -->
      <img class="avatar-img" src="..." alt="..." />
      <!-- OR SVG fallback when no photo URL is found: -->
      <svg class="avatar-svg" ...>...</svg>
    </span>

    <span class="flex-grow-1 overflow-hidden text-start">
      <span class="d-block fw-semibold text-truncate lh-sm">username</span>
      <span class="d-block small text-muted text-truncate">user@example.com</span>
    </span>
  </button>

  <!-- Dropup panel -->
  <ul class="dropdown-menu" style="--bs-dropdown-min-width: 100%">
    <!-- Account Center link -->
    <li><a class="dropdown-item ..." href="/account-center/">Account Center</a></li>

    <!-- [Custom slot items rendered here] -->

    <!-- Divider -->
    <li><hr class="dropdown-divider" /></li>

    <!-- Logout button (linked to the form below via form="logoutForm") -->
    <li>
      <button type="submit" form="logoutForm" class="dropdown-item text-start w-100">
        Log out
      </button>
    </li>
  </ul>

  <!-- Logout POST form (outside the <ul>, linked by id="logoutForm") -->
  <form method="post" id="logoutForm" action="/account-center/logout/" class="d-block m-0">
    <input type="hidden" name="csrfmiddlewaretoken" value="...">
  </form>
</div>
```

---

## URL Degradation

- `account-center` URL is resolved inline (not via `as`), so it requires the URL to be registered. This URL is always present when `dac.urls` is included.
- `account_logout` is resolved via `{% url 'account_logout' as logout_url %}`. If not registered, `logout_url` is `""` and the logout form is omitted.

---

## Integration Test Assertions

| Scenario | DOM assertion |
|---|---|
| Anonymous user | No `div.dac-user-menu`; no `button[data-bs-toggle="dropdown"]` |
| Authenticated user | `div.dac-user-menu` exists |
| Username in trigger | `button[data-bs-toggle="dropdown"]` contains `str(request.user)` text |
| Email in trigger | Trigger contains `<span class="text-muted">` with `request.user.email` |
| Trigger aria attrs | `aria-expanded="false"` and `aria-haspopup="true"` on trigger button |
| Username truncate | Trigger contains `<span class="text-truncate">` with username text |
| Avatar element | Trigger contains `<span class="avatar">` |
| Account Center link | Dropup `<ul>` contains `<a>` with href to `/account-center/` |
| Logout present | Dropup contains `<form method="post">` with logout action |
| Account Center absent (no URL) | No Account Center `<a>` when URL conf is minimal |
| Logout absent (no URL) | No logout `<form>` when URL conf is minimal |
| Custom slot item | Custom `<a>` appears before the logout `<form>` in rendered HTML |
