# Quickstart: Social Account Connections Templates

**Feature**: 009-socialaccount-connections

## Overview

This feature corrects the DAC allauth addon's social account connection templates so
they render inside the Account Center management layout (sidebar, breadcrumbs,
card-stack). The fix mirrors spec 006 (email management): one `extends` line change
in `base_manage.html` propagates the DAC layout to `connections.html`, which is also
fully rewritten with Cotton components and per-account inline remove forms.
`authentication_error.html` receives a minor correction to replace allauth `{% element %}`
tags with `<c-text>`.

## What Changed

| File | Change |
|---|---|
| `dac/addons/allauth/templates/socialaccount/base_manage.html` | One-line fix: extends `dac/base.html` instead of `allauth/layouts/manage.html` |
| `dac/addons/allauth/templates/socialaccount/connections.html` | Full rewrite: `{% block page.content %}`, `<c-list-group>` per-account forms, `<c-badge>` for provider |
| `dac/addons/allauth/templates/socialaccount/authentication_error.html` | Corrections only: drop `{% element h1 %}`, replace `{% element p %}` with `<c-text>` |

## Prerequisites

- `dac.addons.allauth` in `INSTALLED_APPS`
- `dac/base.html` available (Spec 005)
- `allauth.socialaccount` in `INSTALLED_APPS`
- `allauth.urls` (or `socialaccount.urls`) included in URL configuration

## Template Blocks Available

After `base_manage.html` is corrected, all socialaccount management pages inherit
the block contract from `dac/base.html`:

```django
{% extends "socialaccount/base_manage.html" %}
{% load i18n %}

{% block title %}{% trans "My Social Page" %}{% endblock %}

{% block page.breadcrumbs %}
  {{ block.super }}
  <c-breadcrumbs.item text="{% trans 'My Social Page' %}" />
{% endblock %}

{% block page.content %}
  {# Your page content here — already inside <c-card.stack> #}
{% endblock %}
```

## Disconnect Form Mechanics

Each connected account is shown in a `<c-list-group.item>`. Its remove button is
part of an individual inline form, **not** a shared radio-select form:

```django
{% for account in form.accounts %}
  {% with provider_account=account.get_provider_account %}
    {# Each account has its own independent POST form #}
    <form method="post" action="{% url 'socialaccount_connections' %}">
      {% csrf_token %}
      <input type="hidden" name="account" value="{{ account.pk }}" />
      {# submit → ConnectionsView.post() → DisconnectForm.clean() → form.save() #}
    </form>
  {% endwith %}
{% endfor %}
```

## Running the Tests

```bash
# Integration tests
poetry run pytest tests/test_addons/test_allauth/test_social_connections_view.py --no-cov -v

# Screenshot tests (regenerates docs/_static/{desktop,tablet,mobile}/*.png)
poetry run pytest screenshots/test_social_connections_screenshots.py -v
```

## Verifying No Element Tags Remain

```powershell
# Should return no output if all element tags are gone
Select-String `
  -Path "dac/addons/allauth/templates/socialaccount/base_manage.html",
        "dac/addons/allauth/templates/socialaccount/connections.html",
        "dac/addons/allauth/templates/socialaccount/authentication_error.html" `
  -Pattern "{% element|{% endelement"
```

## Screenshot States

Three page states × three viewports = 9 PNGs persisted under `docs/_static/`:

| State | File slug | Condition |
|---|---|---|
| Connected accounts present | `connections-has-accounts` | User has ≥1 social account |
| No connected accounts | `connections-no-accounts` | User has 0 social accounts |
| Authentication error | `authentication-error` | Static error page |

```
docs/_static/
├── desktop/
│   ├── connections-has-accounts.png
│   ├── connections-no-accounts.png
│   └── authentication-error.png
├── tablet/
│   └── (same 3 files)
└── mobile/
    └── (same 3 files)
```
