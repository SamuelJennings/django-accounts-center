# Component Interface Contract: Allauth Signup Page Cotton Components

**Feature**: 001-allauth-signup-page
**Date**: 2026-05-07
**Updated**: 2026-05-08 — Added DAC-owned entrance Cotton components (`<c-entrance>`, `<c-entrance.background>`, `<c-entrance.logo>`, `<c-group>`). Updated `<c-card>`, `<c-button>`, `<c-form>`, `<c-form.render>`, and `<c-alert>` sections to reflect finalised implementation (card owned by `<c-entrance>`; non-field errors handled in `<c-form.render>`; social providers use Bootstrap Icon `<a>` tags; submit wrapped in `<c-group>`).

This document specifies how the django-accounts-center allauth addon composes its signup page UI from Cotton components. Components are grouped by origin: DAC-owned (created in this package) and library components (from django-mvp or django-cotton-bs5).

---

## DAC-Owned Cotton Components

These components are created and maintained by `django-accounts-center` in `dac/templates/cotton/entrance/`. Developers may override them by creating the same path in their project's `templates/` directory.

### `<c-entrance>` — Entrance Page Shell

**Source**: `dac/templates/cotton/entrance/index.html`

**Usage** (in `allauth/layouts/entrance.html`):

```html
<c-entrance cols="12" md="8" lg="5">
  <c-slot name="title">{% block title %}{% endblock title %}</c-slot>
  {% block content %}{% endblock content %}
</c-entrance>
```

**What it renders**: Full-viewport centred layout (`<c-entrance.background>` → container → responsive column (`<c-col attrs="attrs">`) → card (`shadow-lg rounded-4 border-0`) → `<c-entrance.logo>` → optional `title` heading → `{{ slot }}`.

| Attr/Slot | Type | Purpose |
|---|---|---|
| `cols`, `md`, `lg`, etc. | `str` | Responsive width attrs forwarded to `<c-col>` |
| `title` (slot) | HTML | Rendered as `<h4 class="fw-semibold mt-3">` inside the card header |
| default slot | HTML | Page content rendered below the logo/title area |

**Override**: Override the template file to change the entire entrance shell structure.

---

### `<c-entrance.background>` — Page Background Wrapper

**Source**: `dac/templates/cotton/entrance/background.html`

**What it renders**: A wrapping `<div>` with background styling. Default: `bg-primary-subtle bg-gradient`.

**Override**: Create `templates/cotton/entrance/background.html` in your project to change the page background (colour, gradient, image) without touching any other component.

```html
{# Example override: dark background #}
<div class="bg-dark">{{ slot }}</div>
```

---

### `<c-entrance.logo>` — Site Logo

**Source**: `dac/templates/cotton/entrance/logo.html`

**What it renders**: An `<img>` with the DAC SVG logo at 120px height by default.

| Var | Default | Purpose |
|---|---|---|
| `height` | `120` | Logo display height in px |
| `alt` | `"Site Logo"` | `alt` attribute text |
| `class` | `"d-block mx-auto img-fluid"` | CSS classes on the `<img>` |

**Override**: There is **no `src` prop**. To change the logo, create `templates/cotton/entrance/logo.html` in your project:

```html
{% load static %}
<img src="{% static 'myapp/logo.svg' %}" alt="My Company" style="height: 80px; width: auto" class="d-block mx-auto" />
```

---

## Library Components (django-mvp and django-cotton-bs5)

These components are consumed by the signup templates. They are defined in django-mvp or django-cotton-bs5 and must not be recreated in `dac/`.

### `<c-card>` — Entrance Card

**Source**: `django-mvp` (`mvp/templates/cotton/card/index.html`)

**Usage**: Rendered internally by `<c-entrance>` — page templates do NOT use `<c-card>` directly. The card receives `class="shadow-lg rounded-4 border-0"` and the `only` attribute (suppresses default padding).

**Override**: Override `<c-entrance>` to change card styling.

---

### `<c-card.divider>` — "or" Separator

**Source**: `django-mvp` (`mvp/templates/cotton/card/divider.html`)

**Usage**:

```html
{# Separator between social buttons and email/password form #}
<c-card.divider text="{% trans 'or' %}" />

{# Plain separator before passkey button #}
<c-card.divider />
```

**Attributes**:

| Attribute | Value | Purpose |
|---|---|---|
| `text` | `"or"` (translated) | Centred label text on the divider line |

---

### `<c-group>` — Vertical Button Stack

**Source**: `django-mvp` (`mvp/templates/cotton/button/stack.html`)

**Usage** (wraps submit and passkey buttons):

```html
<c-group class="mt-4">
  <c-button text="{% trans \"Let's go!\" %}" icon="login" type="submit" variant="primary" reverse />
</c-group>
```

**Attributes**:

| Attribute | Default | Purpose |
|---|---|---|
| `gap` | `2` | Bootstrap gap between stacked buttons |
| `class` | — | Additional CSS classes on the `vstack` wrapper |

**Behaviour**: Renders `<div class="vstack gap-{gap} {class}">{{ slot }}</div>`. Makes enclosed buttons full-width and vertically stacked.

---

### `<c-button>` — Submit and Passkey Buttons

**Source**: `django-cotton-bs5` (`cotton_bs5/templates/cotton/button/index.html`)

**Submit button usage** (inside `<c-group>`):

```html
<c-button text="{% trans \"Let's go!\" %}"
          icon="login"
          type="submit"
          variant="primary"
          reverse />
```

**Passkey signup button usage** (inside `<c-group>`):

```html
<c-button href="{{ signup_by_passkey_url }}"
          text="{% trans 'Sign up using a passkey' %}"
          variant="outline-secondary" />
```

**Key attributes** (`<c-button>`):

| Attribute | Type | Description |
|---|---|---|
| `href` | `str` | Renders as `<a>` link button when set |
| `type` | `str` | HTML button type (e.g., `"submit"`) — renders as `<button>` when no href |
| `text` | `str` | Button label text |
| `icon` | `str` | Bootstrap Icon name (e.g., `"login"`) rendered as `<i class="bi bi-{icon}">` |
| `variant` | `str` | Bootstrap colour variant (e.g., `"primary"`, `"outline-secondary"`) |
| `reverse` | `bool` | When set, renders icon after text |

**Note**: Social provider links are rendered as raw Bootstrap Icon `<a>` tags in `socialaccount/snippets/provider_list.html` — NOT as `<c-button>` — because the icon+label flex layout is simpler as plain HTML.

---

### `<c-form>` — Form Element

**Source**: `django-mvp` (`mvp/templates/cotton/form/index.html`)

**Usage** (inside `<c-form>`, no non-field errors block needed):

```html
<c-form method="post" action="{% url 'account_signup' %}">
  <c-form.render />
  {{ redirect_field }}
  <c-group class="mt-4">
    <c-button text="{% trans \"Let's go!\" %}" icon="login" type="submit" variant="primary" reverse />
  </c-group>
</c-form>
```

| Attribute | Type | Description |
|---|---|---|
| `method` | `str` | Form method; when `"post"`, `{% csrf_token %}` is auto-injected |
| `action` | `str` | Form action URL |
| `form_attrs` | `str` | Additional HTML attributes forwarded to the `<form>` element |

**Behaviour**: Renders a `<form>` element and auto-injects `{% csrf_token %}` when `method` is `"post"`. The default slot is the form body content.

---

### `<c-form.render>` — Form Field Renderer

**Source**: `django-mvp` (`mvp/templates/cotton/form/crispy.html`)

**Usage** (inside `<c-form>`):

```html
<c-form.render />
```

**Behaviour**: Renders `{{ form|crispy }}` using the `form` context variable from allauth's SignupView. Applies `crispy-bootstrap5` styling to all form fields (labels, inputs, help text, per-field errors). When the form has no `helper` attribute, also renders a `<c-alert variant="danger">` for `form.non_field_errors` above the fields. Page templates must NOT add a separate `{% if form.non_field_errors %}` block.

**Constraint**: Uses the `form` context variable directly. The `form` in context must be the allauth SignupForm at render time.

---

### `<c-messages>` — Flash Message Display

**Source**: `django-mvp` (`mvp/templates/cotton/messages.html`)

**Usage** (in `allauth/layouts/entrance.html`):

```html
<c-messages dismissible animate />
```

**Placement**: Rendered inside the centered entrance container, ABOVE the signup card — so it is always visible regardless of card scroll position.

---

### `<c-alert>` — Non-Field Error Display

**Source**: `django-cotton-bs5` (`cotton_bs5/templates/cotton/alert.html`)

**Usage**: Rendered automatically by `<c-form.render>` when `form.non_field_errors` is non-empty. Page templates must NOT render this directly.

```html
{# Inside c-form.render — do NOT duplicate in page templates #}
{% if form.non_field_errors %}
  <c-alert variant="danger" class="mb-3">{{ form.non_field_errors }}</c-alert>
{% endif %}
```

---

## Developer Override Points (FR-009)

A developer consuming `django-accounts-center` can override any of the following template files in their own project's `templates/` directory. Django's template loading order ensures the project's template takes precedence over the addon's.

| Template Path | What It Controls |
|---|---|
| `cotton/entrance/background.html` | Full-page background style (colour, gradient, image) — override without touching any other template |
| `cotton/entrance/logo.html` | Site logo rendered inside the entrance card — override to change logo (no `src` prop) |
| `account/signup.html` | Entire signup page content block |
| `account/signup_closed.html` | "Signup is closed" message content |
| `socialaccount/signup.html` | Social-account-only signup form (after OAuth callback) |
| `socialaccount/snippets/provider_list.html` | Social provider link/button list |
| `allauth/layouts/entrance.html` | Entrance-page layout — override only if replacing `<c-entrance>` entirely |
| `allauth/layouts/base.html` | HTML shell — override only if replacing django-mvp entirely |

**To override the background only**: Create `templates/cotton/entrance/background.html` in your project.
**To override the logo only**: Create `templates/cotton/entrance/logo.html` in your project.
**To override a single sub-section** (e.g., just the social provider buttons): Create `templates/socialaccount/snippets/provider_list.html` in your project.
