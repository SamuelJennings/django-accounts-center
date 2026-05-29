# Quickstart: Base Management Page

## Overview

`dac/base.html` is the shared base template for all authenticated management pages in
`django-accounts-center`. It provides a consistent layout: Account Center Menu in the
sidebar, a breadcrumb trail rooted at "Account Center", a form-view width constraint,
and a card-stack content area.

## Using the base template

Extend `dac/base.html` from any management sub-page template:

```django
{% extends "dac/base.html" %}
{% load i18n %}

{% block title %}{% trans "Change Password" %}{% endblock title %}

{% block page.breadcrumbs %}
  {{ block.super }}
  <c-breadcrumbs.item text="{% trans "Change Password" %}" />
{% endblock page.breadcrumbs %}

{% block page.content %}
  <c-form method="post">
    {% csrf_token %}
    {{ form|crispy }}
    <c-button type="submit" text="{% trans "Change password" %}" />
  </c-form>
{% endblock page.content %}
```

## Available blocks

| Block | Default | When to override |
|---|---|---|
| `title` | *(empty)* | Always — provide the page heading string |
| `page.breadcrumbs` | "Account Center" breadcrumb item | Use `{{ block.super }}` and append items |
| `page.content` | `{% trans "Coming soon..." %}` | Always — provide the page's primary UI |
| `breadcrumbs` | Toolbar + breadcrumbs structure | Rarely — only to change header layout |
| `page.content-wrapper` | `<c-page.content>` + `layouts.form-view` | Rarely — only for full-width layouts |
| `app.sidebar` | Account Center Menu | Almost never — override to inject a different menu |
| `content` | Full management page structure | Never — override `page.content` instead |

## Running the tests

```bash
# Cotton rendering tests (block and component assertions)
poetry run pytest tests/test_components/test_dac_base.py --no-cov -v

# All component tests
poetry run pytest tests/test_components/ --no-cov -v
```

## Template location

```
dac/templates/dac/base.html
```

This path is resolvable by any Django project that includes `dac` in `INSTALLED_APPS`
and uses the standard `APP_DIRS = True` template backend.
