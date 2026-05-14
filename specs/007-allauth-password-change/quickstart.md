# Quickstart: Allauth Password Change Templates

**Feature**: `007-allauth-password-change`
**Date**: 2026-05-12

## What This Feature Does

Rewrites four `account/` template overrides in `dac/addons/allauth/` so that:

1. `password_change.html` and `password_set.html` render inside the DAC management
   layout (sidebar, breadcrumbs, card-stack) using Cotton components.
2. `base_reauthenticate.html` and `reauthenticate.html` replace all allauth
   `{% element %}` tags with Cotton equivalents, consistent with every other
   DAC entrance-style template.

No Python changes, no model changes, no settings changes.

## Files Changed

| File | Change |
|---|---|
| `dac/addons/allauth/templates/account/base_reauthenticate.html` | Full Cotton rewrite |
| `dac/addons/allauth/templates/account/reauthenticate.html` | Full Cotton rewrite |
| `dac/addons/allauth/templates/account/password_change.html` | Full Cotton rewrite |
| `dac/addons/allauth/templates/account/password_set.html` | Full Cotton rewrite |

## Files Added

| File | Purpose |
|---|---|
| `tests/test_addons/test_allauth/test_password_change_view.py` | Integration tests |
| `screenshots/test_password_change_screenshots.py` | Playwright screenshot tests |

## Running the Tests

**Integration tests** (fast, no browser):

```sh
poetry run pytest tests/test_addons/test_allauth/test_password_change_view.py --no-cov -v
```

**Screenshot tests** (requires Playwright + running server):

```sh
poetry run pytest screenshots/test_password_change_screenshots.py -v
```

**All allauth tests**:

```sh
poetry run pytest tests/test_addons/test_allauth/ --no-cov -q
```

## Template Block Reference

### `password_change.html` and `password_set.html`

These templates extend `account/base_manage_password.html` which chains to
`dac/base.html`. They use the following blocks:

```django
{% block title %}{% trans "Change Password" %}{% endblock title %}

{% block page.breadcrumbs %}
  {{ block.super }}
  <c-breadcrumbs.item text="{% trans "Change Password" %}" />
{% endblock page.breadcrumbs %}

{% block page.content %}
  <c-form.card method="post" action="{% url 'account_change_password' %}" :form-obj="form">
    {{ redirect_field }}
    <c-slot name="actions">
      <c-button.stack>
        <c-button type="submit" variant="primary" text="{% trans "Change Password" %}" />
        <a href="{% url 'account_reset_password' %}">{% trans "Forgot Password?" %}</a>
      </c-button.stack>
    </c-slot>
  </c-form.card>
{% endblock page.content %}
```

> **Important**: Use `{% block page.content %}` — NOT `{% block content %}`.
> Using `{% block content %}` bypasses the DAC card-stack entirely.

### `base_reauthenticate.html`

This template extends `account/base_entrance.html` and exposes
`{% block reauthenticate_content %}` for child templates:

```django
{% block content %}
  <c-entrance.section text="{% trans "Please reauthenticate to safeguard your account." %}">
    {% block reauthenticate_content %}{% endblock %}
  </c-entrance.section>
  {% if reauthentication_alternatives %}
    <c-card.divider text="{% trans "Alternative options" %}" />
    <c-button.stack>
      {% for alt in reauthentication_alternatives %}
        <c-button href="{{ alt.url }}" variant="outline-primary" text="{{ alt.description }}" />
      {% endfor %}
    </c-button.stack>
  {% endif %}
{% endblock content %}
```

### `reauthenticate.html`

Fills `{% block reauthenticate_content %}` with the password form:

```django
{% block reauthenticate_content %}
  <c-form method="post" action="{% url 'account_reauthenticate' %}" :form-obj="form">
    {{ redirect_field }}
    <c-button.stack>
      <c-button type="submit" variant="primary" text="{% trans "Confirm" %}" />
    </c-button.stack>
  </c-form>
{% endblock %}
```

## MFA Reauthentication (Out of Scope)

`mfa/reauthenticate.html` and `mfa/webauthn/reauthenticate.html` both extend
`account/base_reauthenticate.html` and only override `{% block reauthenticate_content %}`.
The base template rewrite does not touch that block, so both MFA templates continue
to work correctly without modification.

## Verification

After implementation, verify that no `{% element %}` tags remain in any of the four
rewritten templates:

```sh
Select-String -Path "dac\addons\allauth\templates\account\password_change.html",
                    "dac\addons\allauth\templates\account\password_set.html",
                    "dac\addons\allauth\templates\account\base_reauthenticate.html",
                    "dac\addons\allauth\templates\account\reauthenticate.html" `
              -Pattern "element" | Select-Object Filename, Line
```

Expected output: no matches.
