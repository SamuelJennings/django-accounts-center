# Component Interface Contract: Allauth Password Change Templates

**Feature**: `007-allauth-password-change`
**Date**: 2026-05-12

## Scope

Four templates in `dac/addons/allauth/templates/account/` are rewritten.
`base_manage_password.html` is verified but not modified.

---

## `account/base_reauthenticate.html`

**Change type**: Full rewrite (replace all `{% element %}` tags with Cotton)
**Extends**: `account/base_entrance.html` (unchanged)

### Before (current)

```django
{% extends "account/base_entrance.html" %}
{% load allauth %}
{% load i18n %}

{% block title %}
  {% trans "Confirm Access" %}
{% endblock title %}

{% block content %}
  {% element h1 %}{% trans "Confirm Access" %}{% endelement %}
  {% element p %}{% blocktranslate %}Please reauthenticate...{% endblocktranslate %}{% endelement %}
  {% block reauthenticate_content %}{% endblock %}
  {% if reauthentication_alternatives %}
    {% element hr %}{% endelement %}
    {% element h2 %}{% trans "Alternative options" %}{% endelement %}
    {% element button_group %}
      {% for alt in reauthentication_alternatives %}
        {% element button href=alt.url tags="primary,outline" %}{{ alt.description }}{% endelement %}
      {% endfor %}
    {% endelement %}
  {% endif %}
{% endblock content %}
```

### After (target)

```django
{% extends "account/base_entrance.html" %}
{% load i18n %}

{% block title %}{% trans "Confirm Access" %}{% endblock title %}

{% block content %}
  <c-section text="{% trans "Please reauthenticate to safeguard your account." %}">
    {% block reauthenticate_content %}{% endblock %}
  </c-section>
  {% if reauthentication_alternatives %}
    <c-divider text="{% trans "Alternative options" %}" />
    <c-group>
      {% for alt in reauthentication_alternatives %}
        <c-button href="{{ alt.url }}" variant="outline-primary" text="{{ alt.description }}" />
      {% endfor %}
    </c-group>
  {% endif %}
{% endblock content %}
```

**Key changes**:

- Remove `{% load allauth %}` (no longer needed)
- `{% element h1 %}` → removed; heading produced by `<c-section>` implicitly or kept as `<c-text tag="h1">`
- `{% element p %}` → `<c-section text="…">` wrapper
- `{% element hr %}` → `<c-divider>`
- `{% element h2 %}` → removed; divider text serves as section label
- `{% element button_group %}` → `<c-group>`
- `{% element button href=… tags="primary,outline" %}` → `<c-button href=… variant="outline-primary">`
- `{% block reauthenticate_content %}` extension hook is preserved inside the section

---

## `account/reauthenticate.html`

**Change type**: Full rewrite of `{% block reauthenticate_content %}`
**Extends**: `account/base_reauthenticate.html`

### Before (current)

```django

{% load allauth %}
{% load i18n %}

{% block reauthenticate_content %}
  {% element p %}{% blocktranslate %}Enter your password:{% endblocktranslate %}{% endelement %}
  {% url 'account_reauthenticate' as action_url %}
  {% element form form=form method="post" action=action_url %}
    {% slot body %}
      {% csrf_token %}
      {% element fields form=form unlabeled=True %}{% endelement %}
      {{ redirect_field }}
    {% endslot %}
    {% slot actions %}
      {% element button type="submit" tags="primary,reauthenticate" %}{% trans "Confirm" %}{% endelement %}
    {% endslot %}
  {% endelement %}
{% endblock %}
```

### After (target)

```django

{% load i18n %}

{% block reauthenticate_content %}
  <c-form method="post"
          action="{% url 'account_reauthenticate' %}"
          :form-obj="form">
    {{ redirect_field }}
    <c-group>
      <c-button type="submit"
                variant="primary"
                text="{% trans "Confirm" %}" />
    </c-group>
  </c-form>
{% endblock %}
```

**Key changes**:

- Remove `{% load allauth %}` (no longer needed)
- `{% element p %}Enter your password:{% endelement %}` → removed; the `<c-form>` renders field labels
- `{% element form … %}` + `{% slot body %}` + `{% slot actions %}` → `<c-form>` with inline `<c-group>`
- `{% element fields form=form unlabeled=True %}` → `:form-obj="form"` attribute on `<c-form>` (renders all fields)
- `{% element button … %}{% trans "Confirm" %}{% endelement %}` → `<c-button type="submit" variant="primary" text="…">`

---

## `account/password_change.html`

**Change type**: Full rewrite
**Extends**: `account/base_manage_password.html`

### Before (current)

```django
{% extends "account/base_manage_password.html" %}
{% load allauth i18n %}

{% block title %}{% trans "Change Password" %}{% endblock title %}

{% block content %}
  {% element h1 %}{% trans "Change Password" %}{% endelement %}
  {% url 'account_change_password' as action_url %}
  {% element form form=form method="post" action=action_url %}
    {% slot body %}
      {% csrf_token %}
      {{ redirect_field }}
      {% element fields form=form %}{% endelement %}
    {% endslot %}
    {% slot actions %}
      {% element button type="submit" %}{% trans "Change Password" %}{% endelement %}
      <a href="{% url 'account_reset_password' %}">{% trans "Forgot Password?" %}</a>
    {% endslot %}
  {% endelement %}
{% endblock content %}
```

### After (target)

```django
{% extends "account/base_manage_password.html" %}
{% load i18n %}

{% block title %}{% trans "Change Password" %}{% endblock title %}

{% block page.breadcrumbs %}
  {{ block.super }}
  <c-navigation.breadcrumbs.item text="{% trans "Change Password" %}" />
{% endblock page.breadcrumbs %}

{% block page.content %}
  <c-form method="post"
               action="{% url 'account_change_password' %}"
               :form-obj="form">
    {{ redirect_field }}
    <c-slot name="actions">
      <c-group>
        <c-button type="submit"
                  variant="primary"
                  text="{% trans "Change Password" %}" />
        <a href="{% url 'account_reset_password' %}">{% trans "Forgot Password?" %}</a>
      </c-group>
    </c-slot>
  </c-form>
{% endblock page.content %}
```

**Key changes**:

- Remove `{% load allauth %}` (no longer needed)
- `{% block content %}` → `{% block page.content %}` (critical fix)
- Add `{% block page.breadcrumbs %}` with leaf item
- `{% element h1 %}` → removed (page title comes from `{% block title %}` in management shell)
- `{% element form … %}` + slots → `<c-form>` with `<c-slot name="actions">`
- `{% element fields form=form %}` → `:form-obj="form"` attribute on `<c-form>`
- `{% element button %}` → `<c-button type="submit" variant="primary" …>`

---

## `account/password_set.html`

**Change type**: Full rewrite
**Extends**: `account/base_manage_password.html`

### Before (current)

```django
{% extends "account/base_manage_password.html" %}
{% load i18n %}
{% load allauth %}

{% block title %}{% trans "Set Password" %}{% endblock title %}

{% block content %}
  {% element h1 %}{% trans "Set Password" %}{% endelement %}
  {% url 'account_set_password' as action_url %}
  {% element form method="post" action=action_url %}
    {% slot body %}
      {% csrf_token %}
      {{ redirect_field }}
      {% element fields form=form %}{% endelement %}
    {% endslot %}
    {% slot actions %}
      {% element button type="submit" name="action" %}{% trans 'Set Password' %}{% endelement %}
    {% endslot %}
  {% endelement %}
{% endblock content %}
```

### After (target)

```django
{% extends "account/base_manage_password.html" %}
{% load i18n %}

{% block title %}{% trans "Set Password" %}{% endblock title %}

{% block page.breadcrumbs %}
  {{ block.super }}
  <c-navigation.breadcrumbs.item text="{% trans "Set Password" %}" />
{% endblock page.breadcrumbs %}

{% block page.content %}
  <c-form method="post"
               action="{% url 'account_set_password' %}"
               :form-obj="form">
    {{ redirect_field }}
    <c-slot name="actions">
      <c-group>
        <c-button type="submit"
                  variant="primary"
                  text="{% trans "Set Password" %}" />
      </c-group>
    </c-slot>
  </c-form>
{% endblock page.content %}
```

**Key changes** (same as `password_change.html` minus the "Forgot Password?" link):

- Remove `{% load allauth %}` (no longer needed)
- `{% block content %}` → `{% block page.content %}` (critical fix)
- Add `{% block page.breadcrumbs %}` with leaf item
- `{% element h1 %}`, `{% element form %}`, slots → `<c-form>` with `<c-slot name="actions">`
- No "Forgot Password?" link (not present on set-password page)

---

## `account/base_manage_password.html`

**Change type**: No change (verified only)
**Current content**: `{% extends "account/base_manage.html" %}`
**Status**: Correct — inherits full DAC layout transitively. Verified by test.
