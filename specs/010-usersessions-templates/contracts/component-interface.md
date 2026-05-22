# Component Interface: User Sessions Templates

**Feature**: 010-usersessions-templates
**Templates**: `usersessions/base_manage.html`, `usersessions/usersession_list.html`

## Template Block Contracts

### `usersessions/base_manage.html`

**Change**: One line — `extends` target changed from `allauth/layouts/manage.html` to `dac/base.html`.

```django
{% extends "dac/base.html" %}
```

No other changes. This file has no blocks of its own; it solely establishes the
inheritance chain for all usersession templates.

---

### `usersessions/usersession_list.html`

Extends `usersessions/base_manage.html` (unchanged). Overrides three blocks from `dac/base.html`:

#### `{% block title %}`

Renders the visible page heading inside `<c-mvp-toolbar>` → `<c-slot name="title">`.

```django
{% block title %}
  {% trans "Sessions" %}
{% endblock title %}
```

**i18n key**: Reuses allauth's existing `"Sessions"` translation string.

#### `{% block page.breadcrumbs %}`

Appends a "Sessions" leaf to the breadcrumb trail rooted at "Account Center".

```django
{% block page.breadcrumbs %}
  {{ block.super }}
  <c-breadcrumbs.item text="{% trans 'Sessions' %}" />
{% endblock page.breadcrumbs %}
```

`{{ block.super }}` preserves the "Account Center" root breadcrumb defined in `dac/base.html`.
The leaf item has no `href` attribute (it is the current page).

#### `{% block page.content %}`

Contains all session list content. Structure:

```django
{% block page.content %}
  {% if session_count > 1 %}
    {% url 'usersessions_list' as action_url %}
  {% else %}
    {% url 'account_logout' as action_url %}
  {% endif %}

  <c-card>
    <form method="post" action="{{ action_url }}">
      {% csrf_token %}
      <table class="table">
        <thead>
          <tr>
            <th>{% trans "Started At" %}</th>
            <th>{% trans "IP Address" %}</th>
            <th>{% trans "Browser" %}</th>
            {% if show_last_seen_at %}<th>{% trans "Last seen at" %}</th>{% endif %}
            <th></th>
          </tr>
        </thead>
        <tbody>
          {% for session in sessions %}
            <tr>
              <td><span title="{{ session.created_at }}">{{ session.created_at|naturaltime }}</span></td>
              <td>{{ session.ip }}</td>
              <td class="text-truncate" style="max-width: 200px;">{{ session.user_agent }}</td>
              {% if show_last_seen_at %}
                <td><span title="{{ session.last_seen_at }}">{{ session.last_seen_at|naturaltime }}</span></td>
              {% endif %}
              <td>
                {% if session.is_current %}
                  <c-badge variant="success" text="{% trans 'Current' %}" />
                {% endif %}
              </td>
            </tr>
          {% endfor %}
        </tbody>
      </table>
      {% if session_count > 1 %}
        <c-button type="submit" variant="primary" text="{% trans 'Sign Out Other Sessions' %}" />
      {% else %}
        <c-button type="submit" variant="primary" text="{% trans 'Sign Out' %}" />
      {% endif %}
    </form>
  </c-card>
{% endblock page.content %}
```

## Component API Reference

### `<c-breadcrumbs.item>`

| Attribute | Type | Required | Description |
|---|---|---|---|
| `text` | string | Yes | Display text for the breadcrumb item |
| `href` | string | No | URL; omit for the current (last) page item |

**Usage**: `<c-breadcrumbs.item text="{% trans 'Sessions' %}" />`

---

### `<c-card>`

| Attribute | Type | Required | Description |
|---|---|---|---|
| `title` | string | No | Card header title |
| `icon` | string | No | Bootstrap icon name |
| `fs` | string/int | No | Font-size modifier |
| Default slot | HTML | No | Card body content |

**Usage**: `<c-card>` wrapping the `<form>` + `<table>` block. No title attribute
required for the sessions card (the page title serves as the heading).

---

### `<c-badge>`

| Attribute | Type | Required | Description |
|---|---|---|---|
| `text` | string | Yes | Badge label text |
| `variant` | string | No | Bootstrap colour variant (`success`, `primary`, `secondary`, `danger`, …) |

**Usage**: `<c-badge variant="success" text="{% trans 'Current' %}" />`

Precedent: `account/email.html` uses `<c-badge variant="success" text="{% trans 'Verified' %}" />`.

---

### `<c-button>`

| Attribute | Type | Required | Description |
|---|---|---|---|
| `type` | string | No | HTML button type (`submit`, `button`) |
| `variant` | string | No | Bootstrap colour variant (`primary`, `danger`, `secondary`, …) |
| `text` | string | Yes | Button label text |
| `size` | string | No | Bootstrap size modifier (`sm`, `lg`) |
| `icon` | string | No | Bootstrap icon name |

**Usage**:
- Multiple sessions: `<c-button type="submit" variant="primary" text="{% trans 'Sign Out Other Sessions' %}" />`
- Single session: `<c-button type="submit" variant="primary" text="{% trans 'Sign Out' %}" />`

## Conditional Rendering Summary

| Condition | Rendered element |
|---|---|
| Always | `<table>` with Started At, IP Address, Browser columns |
| `show_last_seen_at=True` | "Last seen at" `<th>` and `<td>` in each row |
| `session.is_current=True` | `<c-badge variant="success">` in last column |
| `session.is_current=False` | Empty `<td>` in last column |
| `session_count > 1` | Form action = `usersessions_list`; button text = "Sign Out Other Sessions" |
| `session_count == 1` | Form action = `account_logout`; button text = "Sign Out" |
