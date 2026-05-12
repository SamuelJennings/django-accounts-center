# Component Interface: Allauth Email Management Templates

**Feature**: 006-allauth-email-management

## Overview

Four template files are modified. All inherit from the DAC management layout chain
after `base_manage.html` is corrected. The interface contract describes what each
template extends, which blocks it overrides, and which Cotton components it uses.

---

## 1. `account/base_manage.html`

**File**: `dac/addons/allauth/templates/account/base_manage.html`  
**Change type**: One-line extends correction

### Before

```django
{% extends "allauth/layouts/manage.html" %}
```

### After

```django
{% extends "dac/base.html" %}
```

**Downstream effect**: All templates that inherit through this file
(`base_manage_email.html`, `email.html`, `email_change.html`,
`verified_email_required.html`) now render inside the DAC management layout.

---

## 2. `account/email_change.html`

**File**: `dac/addons/allauth/templates/account/email_change.html`  
**Change type**: Full rewrite  
**Extends**: `account/base_manage_email.html` (unchanged — indirect chain preserved)

### Blocks overridden

| Block | Content |
|---|---|
| `title` | `{% trans "Email Address" %}` |
| `page.breadcrumbs` | `{{ block.super }}` + `<c-breadcrumbs.item text="Email Address" />` |
| `page.content` | All form content (see structure below) |

### Cotton component structure

```
{% block page.content %}
  [{% include "account/snippets/warn_no_email.html" %} if not emailaddresses]

  <c-form.card method="post" action="{{ action_url }}">
    [if current_emailaddress]
      <div class="mb-3">
        <label class="form-label">{% trans "Current email" %}:</label>
        <input type="email" class="form-control" id="current_email" disabled value="{{ current_emailaddress.email }}" />
      </div>
    [endif]

    [if new_emailaddress]
      <div class="mb-3">
        <label class="form-label">
          [if not current_emailaddress] "Current email" [else] "Changing to" [endif]:
        </label>
        <input type="email" class="form-control" id="new_email" disabled value="{{ new_emailaddress.email }}" />
        <div class="form-text">{% blocktrans %}Still pending verification.{% endblocktrans %}</div>
        <div class="mt-2">
          <c-button form="pending-email" type="submit" name="action_send" variant="secondary" size="sm"
                    text="{% trans 'Re-send Verification' %}" />
          [if current_emailaddress]
            <c-button form="pending-email" type="submit" name="action_remove" variant="danger" size="sm"
                      text="{% trans 'Cancel Change' %}" />
          [endif]
        </div>
      </div>
    [endif]

    {{ form.email|as_crispy_field }}

    <c-slot name="actions">
      <c-button name="action_add" type="submit" variant="primary" text="{% trans 'Change Email' %}" />
    </c-slot>
  </c-form.card>

  [if new_emailaddress]
    <form id="pending-email" method="post" action="{% url 'account_email' %}" style="display:none">
      {% csrf_token %}
      <input type="hidden" name="email" value="{{ new_emailaddress.email }}" />
    </form>
  [endif]
{% endblock page.content %}
```

---

## 3. `account/verified_email_required.html`

**File**: `dac/addons/allauth/templates/account/verified_email_required.html`  
**Change type**: Block rename + card wrapper  
**Extends**: `account/base_manage.html`

### Blocks overridden

| Block | Content |
|---|---|
| `title` | `{% trans "Verify Your Email Address" %}` |
| `page.content` | `<c-card>` with explanatory paragraphs and `account_email` link |

### Cotton component structure

```
{% block page.content %}
  <c-card>
    <p>{% blocktrans %}…verification required explanation…{% endblocktrans %}</p>
    <p>{% blocktrans %}…check spam folder…{% endblocktrans %}</p>
    <p>
      {% blocktrans %}
        <strong>Note:</strong> you can still <a href="{{ email_url }}">change your email address</a>.
      {% endblocktrans %}
    </p>
  </c-card>
{% endblock page.content %}
```

---

## 4. `account/email.html`

**File**: `dac/addons/allauth/templates/account/email.html`  
**Change type**: Functional-errors-only audit  
**Extends**: `dac/base.html` (already correct)

### Audit checklist

- [ ] All per-address `<form>` elements have `action="{% url "account_email" %}"`
- [ ] Button with `name="action_primary"` — Make Primary
- [ ] Button with `name="action_send"` — Re-send Verification
- [ ] Button with `name="action_remove"` — Remove (disabled class when primary)
- [ ] Button with `name="action_add"` — Add Email
- [ ] All content inside `{% block page.content %}` (not `{% block content %}`)
- [ ] `{% block extra_js %}` includes `account/js/account.js` and `account/js/onload.js`

Only items that fail the checklist are corrected. Cosmetic changes are out of scope.

---

## Inheritance Chain (after changes)

```
dac/base.html
└── account/base_manage.html          ← CORRECTED: now extends dac/base.html
    ├── account/base_manage_email.html  (unchanged)
    │   ├── account/email.html          (audited; corrections only)
    │   └── account/email_change.html   (full rewrite)
    └── account/verified_email_required.html  (block rename + card wrapper)
```
