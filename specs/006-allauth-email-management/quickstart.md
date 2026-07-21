# Quickstart: Allauth Email Management Templates

**Feature**: 006-allauth-email-management

## Overview

This feature corrects the DAC allauth addon's email management templates so they
render inside the Account Center management layout (sidebar, breadcrumbs, card-stack).

## What Changed

| File | Change |
|---|---|
| `dac/addons/allauth/templates/account/base_manage.html` | One-line fix: extends `dac/base.html` instead of `allauth/layouts/manage.html` |
| `dac/addons/allauth/templates/account/email_change.html` | Full rewrite to Cotton + `{% block page.content %}` |
| `dac/addons/allauth/templates/account/verified_email_required.html` | Block rename + `<c-card>` wrapper |
| `dac/addons/allauth/templates/account/email.html` | Functional corrections only |

## Prerequisites

- `dac.addons.allauth` in `INSTALLED_APPS`
- `dac/base.html` available (Spec 005)
- `allauth.urls` included in URL configuration

## Template Blocks Available

All email management pages inherit the block contract from `dac/base.html`:

```django
{% extends "account/base_manage_email.html" %}
{% load i18n %}

{% block title %}{% trans "My Email Page" %}{% endblock %}

{% block page.breadcrumbs %}
  {{ block.super }}
  <c-navigation.breadcrumbs.item text="{% trans 'My Email Page' %}" />
{% endblock %}

{% block page.content %}
  {# Your page content here — already inside <c-card.stack> #}
{% endblock %}
```

## Running the Tests

```bash
# Integration tests
poetry run pytest tests/test_addons/test_allauth/test_email_management_view.py --no-cov -v

# Screenshot tests (regenerates docs/_static/{desktop,tablet,mobile}/*.png)
poetry run pytest screenshots/test_email_management_screenshots.py -v
```

## Verifying No Element Tags Remain

```bash
# Should return no output if all element tags are gone
Select-String -Path "dac/addons/allauth/templates/account/base_manage.html","dac/addons/allauth/templates/account/email_change.html","dac/addons/allauth/templates/account/verified_email_required.html","dac/addons/allauth/templates/account/email.html" -Pattern "{% element|{% endelement"
```
