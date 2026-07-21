# Component Interface: Social Account Connections Templates

**Feature**: 009-socialaccount-connections

## Overview

Three template files are modified. Two are in the management layout path
(`base_manage.html`, `connections.html`) and one is in the entrance layout path
(`authentication_error.html`). All inherit from the correct layout chain after
`base_manage.html` is corrected.

---

## 1. `socialaccount/base_manage.html`

**File**: `dac/addons/allauth/templates/socialaccount/base_manage.html`
**Change type**: One-line extends correction

### Before

```django
{% extends "allauth/layouts/manage.html" %}
```

### After

```django
{% extends "dac/base.html" %}
```

**Downstream effect**: `connections.html` (which extends `socialaccount/base_manage.html`)
now renders inside the DAC Account Center sidebar/breadcrumb/card-stack shell.

---

## 2. `socialaccount/connections.html`

**File**: `dac/addons/allauth/templates/socialaccount/connections.html`
**Change type**: Full rewrite
**Extends**: `socialaccount/base_manage.html` (unchanged — chain now resolves to `dac/base.html`)

### Blocks overridden

| Block | Content |
|---|---|
| `title` | `{% trans "Account Connections" %}` (reuses allauth i18n key) |
| `page.breadcrumbs` | `{{ block.super }}` + `<c-navigation.breadcrumbs.item text="Account Connections" />` |
| `page.content` | Connected-accounts card + add-connections card (see structure below) |

### Cotton component structure

```
{% block page.content %}

  {# --- Connected accounts section --- #}
  {% if form.accounts %}
    <c-card title="{% trans 'Account Connections' %}" icon="person" fs="3">
      <c-list flush :border="False">
        {% for account in form.accounts %}
          {% with provider_account=account.get_provider_account %}
            <c-list.item>
              <div class="d-flex align-items-center w-100 gap-2">
                <span>{{ provider_account }}</span>
                <c-badge text="{{ provider_account.get_brand.name }}" />
                <form method="post"
                      action="{% url 'socialaccount_connections' %}"
                      class="ms-auto">
                  {% csrf_token %}
                  <input type="hidden" name="account" value="{{ account.pk }}" />
                  <c-button type="submit"
                            text="{% trans 'Remove' %}"
                            variant="danger"
                            size="sm"
                            icon="delete" />
                </form>
              </div>
            </c-list.item>
          {% endwith %}
        {% endfor %}
      </c-list>
    </c-card>
  {% else %}
    <c-card>
      <c-text>
        {% trans "You currently have no third-party accounts connected to this account." %}
      </c-text>
    </c-card>
  {% endif %}

  {# --- Add connections section --- #}
  <c-card title="{% trans 'Add a Third-Party Account' %}">
    {% include "socialaccount/snippets/provider_list.html" with process="connect" %}
    {% include "socialaccount/snippets/login_extra.html" %}
  </c-card>

{% endblock page.content %}
```

### Form mechanics

Each per-account remove form:

- **Method**: `POST` to `{% url 'socialaccount_connections' %}`
- **CSRF**: `{% csrf_token %}` required
- **Payload**: `account=<pk>` as a hidden input
- **Processing**: `ConnectionsView.post()` → `DisconnectForm.clean()` validates the
  PK against `SocialAccount.objects.filter(user=request.user)` → `form.save()` →
  `flows.connect.disconnect(request, account)`

No shared radio-select form is present. Each item submits independently.

---

## 3. `socialaccount/authentication_error.html`

**File**: `dac/addons/allauth/templates/socialaccount/authentication_error.html`
**Change type**: Corrections only (replace `{% element %}` tags)
**Extends**: `socialaccount/base_entrance.html` (unchanged)

### Before

```django
{% extends "socialaccount/base_entrance.html" %}
{% load i18n %}
{% load allauth %}

{% block title %}
  {% trans "Third-Party Login Failure" %}
{% endblock title %}

{% block content %}
  {% element h1 %}
    {% trans "Third-Party Login Failure" %}
  {% endelement %}
  {% element p %}
    {% trans "An error occurred while attempting to login via your third-party account." %}
  {% endelement %}
{% endblock content %}
```

### After

```django
{% extends "socialaccount/base_entrance.html" %}
{% load i18n %}

{% block title %}
  {% trans "Third-Party Login Failure" %}
{% endblock title %}

{% block content %}
  <c-text>
    {% trans "An error occurred while attempting to login via your third-party account." %}
  </c-text>
{% endblock content %}
```

**Changes**:

1. `{% load allauth %}` removed (no allauth tags used)
2. `{% element h1 %}...{% endelement %}` dropped — the DAC entrance layout
   (`allauth/layouts/entrance.html`) renders the `{% block title %}` content as a
   heading via `<c-entrance name="title">`, making the inline `h1` redundant (and
   semantically wrong — two `h1` elements on one page)
3. `{% element p %}...{% endelement %}` replaced with `<c-text>`

---

## Unchanged Files

| File | Status | Reason |
|---|---|---|
| `socialaccount/base_entrance.html` | No change | Already correctly extends `allauth/layouts/entrance.html` |
| `socialaccount/login.html` | No change | Already uses Cotton components |
| `socialaccount/signup.html` | No change | Already uses Cotton components |
| `socialaccount/login_cancelled.html` | No change | Already uses Cotton components |
| `socialaccount/login_redirect.html` | No change | Standalone redirect page, no layout dependency |
