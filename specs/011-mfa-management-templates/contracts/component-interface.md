# Component Interface: MFA Management Templates

**Feature**: 011-mfa-management-templates
**Templates**: 10 files in `dac/addons/allauth/templates/mfa/`

---

## Template Block Contracts

### `mfa/base_manage.html`

**Change**: One line — `extends` target changed from `allauth/layouts/manage.html` to `dac/base.html`.

```django
{% extends "dac/base.html" %}
```

No other changes. This file has no blocks of its own. The single-line fix propagates
the full DAC layout chain to all nine content templates.

---

### `mfa/index.html`

Extends `mfa/base_manage.html`. Overrides three blocks from `dac/base.html`:

#### `{% block title %}`

```django
{% block title %}{% trans "Two-Factor Authentication" %}{% endblock title %}
```

#### `{% block page.breadcrumbs %}`

```django
{% block page.breadcrumbs %}
  {{ block.super }}
  <c-breadcrumbs.item text="{% trans 'Two-Factor Authentication' %}" />
{% endblock page.breadcrumbs %}
```

#### `{% block page.content %}`

Three `<c-card>` panels (TOTP, Recovery Codes, WebAuthn) each using
`<c-slot name="actions">` for action links in the card-header toolbar.

**TOTP panel** (always shown when `"totp"` in `MFA_SUPPORTED_TYPES`):

- Actions: Deactivate link (when `authenticators.totp`) OR Activate link

**Recovery codes panel** (when `"recovery_codes"` in `MFA_SUPPORTED_TYPES`):

- Actions: View/Download/Generate links (when `authenticators.recovery_codes`) OR Generate link

**WebAuthn panel** (when `"webauthn"` in `MFA_SUPPORTED_TYPES`):

- Actions: Manage keys link (`mfa_list_webauthn`)

---

### `mfa/totp/activate_form.html`

Extends `mfa/totp/base.html` (unchanged). Overrides `{% block page.content %}`.

Uses `<c-form.card>` without `form-obj` (custom content in default slot):

```django
{% block page.content %}
  <c-form.card title="{% trans 'Activate TOTP' %}" method="post">
    {% csrf_token %}
    <c-slot name="actions">
      <c-button type="submit" variant="primary" text="{% trans 'Activate' %}" />
    </c-slot>

    {# QR code #}
    <img src="{{ totp_svg_data_uri }}" alt="{% trans 'TOTP QR Code' %}" />
    <p class="mt-2">
      {% blocktrans with secret=form.secret.value %}
        Or enter this secret manually: <code>{{ secret }}</code>
      {% endblocktrans %}
    </p>

    {# Token input field #}
    {{ form.token }}
  </c-form.card>
{% endblock page.content %}
```

---

### `mfa/totp/deactivate_form.html`

Extends `mfa/totp/base.html` (unchanged). Overrides `{% block page.content %}`.

```django
{% block page.content %}
  <c-form.card title="{% trans 'Deactivate TOTP' %}" method="post" :form-obj="form">
    <c-slot name="actions">
      <c-button type="submit" variant="danger" text="{% trans 'Deactivate' %}" />
    </c-slot>
  </c-form.card>
{% endblock page.content %}
```

---

### `mfa/recovery_codes/index.html`

Extends `mfa/recovery_codes/base.html` (unchanged). Overrides `{% block page.content %}`.

Uses raw Bootstrap HTML textarea (Decision 3 — `<c-form.field>` cannot render
textarea with text content). Download and Generate action buttons are inside the card
body, below the textarea.

```django
{% block page.content %}
  <c-card title="{% trans 'Recovery Codes' %}">
    <div class="mb-3">
      <label class="form-label" for="recovery_codes">{% trans "Unused codes" %}</label>
      <textarea class="form-control" id="recovery_codes" readonly
                rows="{{ unused_codes|length }}">{# djlint:off #}{% for code in unused_codes %}{% if forloop.counter0 %}
{% endif %}{{ code }}{% endfor %}{# djlint:on #}</textarea>
    </div>
    <c-button href="{% url 'mfa_download_recovery_codes' %}" text="{% trans 'Download' %}" />
    <c-button href="{% url 'mfa_generate_recovery_codes' %}" text="{% trans 'Generate New Codes' %}" />
  </c-card>
{% endblock page.content %}

{% block extra_js %}{{ block.super }}
  {# Recovery codes JS (copy-to-clipboard) — bound to id="recovery_codes" #}
  {% include "mfa/recovery_codes/snippets/scripts.html" %}
{% endblock extra_js %}
```

**Hard dependency**: `id="recovery_codes"` must be preserved — used by
`mfa/recovery_codes/snippets/scripts.html`.

---

### `mfa/recovery_codes/generate.html`

Extends `mfa/recovery_codes/base.html` (unchanged). Overrides `{% block page.content %}`.

Submit button uses `variant="danger"` only when `unused_code_count > 0`.

```django
{% block page.content %}
  <c-form.card title="{% trans 'Generate Recovery Codes' %}" method="post" :form-obj="form">
    <c-slot name="actions">
      {% if unused_code_count > 0 %}
        <c-button type="submit" variant="danger" text="{% trans 'Generate New Codes' %}" />
      {% else %}
        <c-button type="submit" text="{% trans 'Generate New Codes' %}" />
      {% endif %}
    </c-slot>
  </c-form.card>
{% endblock page.content %}
```

---

### `mfa/webauthn/authenticator_list.html`

Extends `mfa/webauthn/base.html` (unchanged). Overrides `{% block page.content %}`.

Uses raw Bootstrap `<table class="table">` inside `<c-card>` (Decision 6 — no
`<c-table>` component exists). `<c-badge>` provides type indicator.

```django
{% block page.content %}
  <c-card title="{% trans 'Security Keys' %}">
    <c-slot name="actions">
      <c-button href="{% url 'mfa_add_webauthn' %}" text="{% trans 'Add Security Key' %}" />
    </c-slot>

    {% if authenticators %}
      <table class="table">
        <thead>
          <tr>
            <th>{% trans "Name" %}</th>
            <th>{% trans "Type" %}</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          {% for authenticator in authenticators %}
            <tr>
              <td>{{ authenticator.name }}</td>
              <td>
                <c-badge variant="primary" text="{{ authenticator.type }}" />
              </td>
              <td>
                <a href="{% url 'mfa_edit_webauthn' authenticator.pk %}">{% trans "Edit" %}</a>
                <a href="{% url 'mfa_remove_webauthn' authenticator.pk %}">{% trans "Remove" %}</a>
              </td>
            </tr>
          {% endfor %}
        </tbody>
      </table>
    {% else %}
      <p>{% trans "No security keys registered." %}</p>
    {% endif %}
  </c-card>
{% endblock page.content %}
```

---

### `mfa/webauthn/add_form.html`

Extends `mfa/webauthn/base.html` (unchanged). Overrides `{% block page.content %}`.

WebAuthn JS block preserved **verbatim** (Decision 5). `id="mfa_webauthn_add"` on the
submit button is a hard JS dependency.

```django
{% block page.content %}
  <c-form.card title="{% trans 'Add Security Key' %}" method="post">
    {% csrf_token %}
    <c-slot name="actions">
      <c-button type="submit" id="mfa_webauthn_add" text="{% trans 'Register Key' %}" />
    </c-slot>
    {{ form.passwordless }}
    {{ form.credential }}
  </c-form.card>
{% endblock page.content %}

{% block extra_js %}{{ block.super }}
  {% include "mfa/webauthn/snippets/scripts.html" %}
  {{ js_data|json_script:"js_data" }}
  <script data-allauth-onload="allauth.webauthn.forms.addForm" type="application/json">
    {
      "ids": {
        "add": "mfa_webauthn_add",
        "passwordless": "{{ form.passwordless.auto_id }}",
        "credential": "{{ form.credential.auto_id }}",
        "data": "js_data"
      }
    }
  </script>
{% endblock extra_js %}
```

**Hard dependency**: `id="mfa_webauthn_add"` must be preserved on the submit button.

---

### `mfa/webauthn/edit_form.html`

Extends `mfa/webauthn/base.html` (unchanged). Overrides `{% block page.content %}`.

```django
{% block page.content %}
  <c-form.card title="{% trans 'Edit Security Key' %}" method="post" :form-obj="form">
    <c-slot name="actions">
      <c-button type="submit" variant="primary" text="{% trans 'Save' %}" />
    </c-slot>
  </c-form.card>
{% endblock page.content %}
```

---

### `mfa/webauthn/authenticator_confirm_delete.html`

Extends `mfa/webauthn/base.html` (unchanged). Overrides `{% block page.content %}`.

```django
{% block page.content %}
  <c-form.card title="{% trans 'Remove Security Key' %}" method="post" :form-obj="form">
    <c-slot name="actions">
      <c-button type="submit" variant="danger" text="{% trans 'Remove' %}" />
    </c-slot>
  </c-form.card>
{% endblock page.content %}
```

---

## Component API Reference

### `<c-breadcrumbs.item>`

| Attribute | Required | Description |
|---|---|---|
| `text` | Yes | Display text |
| `href` | No | URL; omit for current-page leaf |

---

### `<c-card>`

| Attribute/Slot | Required | Description |
|---|---|---|
| `title` | No | Renders `<c-mvp.toolbar>` as `card-header` |
| `<c-slot name="actions">` | No | Rendered inside card-header toolbar (requires `title`) |
| Default slot | No | Card body content |

---

### `<c-form.card>`

| Attribute/Slot | Required | Description |
|---|---|---|
| `title` | Yes (for heading) | Forwarded to inner `<c-card>` |
| `method` | No | Form method; defaults to `post` |
| `:form-obj` | No | When provided with `renderer="crispy"`, renders form fields automatically |
| `<c-slot name="actions">` | No | Placed in card-header toolbar (rendered inside `<c-card>`'s `actions` slot) |
| `<c-slot name="form_actions">` | No | Placed in card footer |
| Default slot | No | Rendered in card body when `form-obj` is falsy |

`<c-form>` inside `<c-form.card>` handles CSRF automatically. When `method="post"`,
no explicit `{% csrf_token %}` is needed in the default slot unless the template
manually constructs its own `<form>` tag.

---

### `<c-button>`

| Attribute | Required | Description |
|---|---|---|
| `text` | Yes | Button label |
| `type` | No | `"submit"`, `"button"`, `"reset"`; omit for `<a>` element |
| `href` | No | When provided, renders an `<a>` tag instead of `<button>` |
| `variant` | No | Bootstrap variant: `"primary"`, `"danger"`, `"secondary"`, etc. |
| `id` | No | DOM id (required for `id="mfa_webauthn_add"` JS dependency) |

---

### `<c-badge>`

| Attribute | Required | Description |
|---|---|---|
| `text` | Yes | Badge label text |
| `variant` | No | Bootstrap variant: `"primary"`, `"secondary"`, `"warning"`, `"success"` |
