# Implementation Plan: Allauth Signup Page

**Branch**: `001-allauth-signup-page` | **Date**: 2026-05-07 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/001-allauth-signup-page/spec.md`
**Propagated**: 2026-05-07 — Added Principle XIII (FR-011) multi-viewport screenshot coverage: Constitution Check table updated with Principle XIII row; Project Structure updated with `docs/_static/` directories and `test_signup_screenshots.py`.
**Propagated**: 2026-05-08 — Entrance layout architecture finalised. `<c-entrance>`, `<c-entrance.background>`, and `<c-entrance.logo>` Cotton components created in `dac/templates/cotton/entrance/`. The allauth layout template delegates entirely to `<c-entrance>`. Page templates (signup.html, signup_closed.html) are now content-only. Non-field error rendering moved into `<c-form.crispy>`. Submit button uses `<c-button.stack>` + `<c-button icon=...>`. Updated: Summary, Project Structure, Template Design sections, Constitution post-design check, Open Questions.
**Propagated**: 2026-05-08 — Passkey signup flow added (User Story 6, FR-012). `signup_by_passkey.html` template added to Project Structure and Template Design. Constitution Check Principle XIII updated to 6 permutations × 3 viewports = 18 screenshot files. Open Questions updated with passkey-specific risk.
**Propagated**: 2026-05-08 — Constitution v1.1.2 (Principle XIII PATCH): screenshot-only test modules MUST live in the root `screenshots/` directory, not inside `tests/`. `test_signup_screenshots.py` moved from `tests/test_addons/test_allauth/` to `screenshots/`. Structure Decision updated. Constitution Check Principle XIII note updated.

---

## Summary

Build a styled, modern allauth signup page for `django-accounts-center` by overriding allauth's template hierarchy to extend the `django-mvp` visual shell (AdminLTE4 + Bootstrap 5). The entrance page shell is owned by a first-class Cotton component family — `<c-entrance>` (layout), `<c-entrance.background>` (background style), `<c-entrance.logo>` (logo) — located in `dac/templates/cotton/entrance/`. The allauth layout template (`allauth/layouts/entrance.html`) delegates entirely to `<c-entrance>`; page templates (e.g. `signup.html`) are content-only. UI is composed from `django-mvp` Cotton components (`<c-card>`, `<c-card.divider>`, `<c-form.crispy>`, `<c-messages>`, `<c-button.stack>`) and `django-cotton-bs5` components (`<c-button>`, `<c-alert>`). Non-field form errors are rendered inside `<c-form.crispy>` and must not be duplicated in page templates. No new Python views, models, or forms are introduced.

---

## Technical Context

**Language/Version**: Python 3.12+
**Primary Dependencies**: Django 5.2+, django-allauth v65+, django-mvp ≥0.1.1, django-cotton, django-cotton-bs5, crispy-bootstrap5
**Storage**: N/A — no new database tables or models
**Testing**: pytest, pytest-django, pytest-playwright
**Target Platform**: Django web application (WSGI/ASGI)
**Project Type**: Reusable Django extension library
**Performance Goals**: No additional database queries beyond allauth's own signup view; page renders from templates only
**Constraints**: Must not patch allauth source; must degrade gracefully when `allauth.socialaccount` is absent; all UI via template overrides only
**Scale/Scope**: Single-page feature (signup page); 7 template files modified

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|---|---|---|
| I. Design-First, Verify Implementation | ✅ PASS | Plan follows design → verify (Playwright) → test workflow |
| II. Documentation-First | ✅ PASS | `quickstart.md` and `contracts/` authored in Phase 1 |
| III. Component Quality & Accessibility | ✅ PASS | Bootstrap 5 semantic HTML; custom entrance Cotton components (`<c-entrance>`, `<c-entrance.background>`, `<c-entrance.logo>`) are minimal wrappers with no accessibility regressions |
| IV. Compatibility & Config-Driven Design | ✅ PASS | Template overrides only; no Python-level configuration |
| V. Tooling & Consistency | ✅ PASS | Poetry + Ruff; djlint applied to all template changes |
| VI. UI Verification (playwright-mcp) | ✅ PASS | Each UI phase includes Playwright MCP verification task |
| VII. Documentation Retrieval (context7) | ✅ PASS | django-allauth, django-mvp, crispy-forms docs consulted via context7 during implementation |
| VIII. End-to-End Testing (pytest-playwright) | ✅ PASS | Full signup flow covered in tasks |
| IX. Template Component Reuse Discipline | ✅ PASS | django-mvp components used first; custom Cotton components created only where no existing component provides the entrance shell pattern |
| X. Third-Party Integration Strategy | ✅ PASS | Integration via template overrides; no view subclassing; addon-isolated in `dac/addons/allauth/` |
| XI. Dual-Audience User Stories | ✅ PASS | Spec covers developer (US1) and end-user (US2, US3, US4, US5) stories |
| XII. View Class Docstring Completeness | ✅ N/A | No new view classes introduced in this feature |
| XIII. Multi-Viewport Screenshot Coverage | ✅ PASS | FR-011 mandates pytest-playwright screenshot tests at 3 viewports × 6 settings permutations (18 files total); `docs/_static/` output directories added; `screenshots/test_signup_screenshots.py` placed in root `screenshots/` directory (excluded from plain `pytest` via `testpaths = ["tests"]`; run explicitly with `pytest screenshots/`) per constitution v1.1.2 |

**Post-design re-check** (after Phase 1 artifacts):

| Check | Status | Notes |
|---|---|---|
| Custom Cotton components are DAC-owned | ✅ PASS | `<c-entrance>`, `<c-entrance.background>`, `<c-entrance.logo>` are created in `dac/templates/cotton/entrance/` (not in the addon). All other UI uses django-mvp or cotton_bs5 components. |
| Template override isolates inside addon | ✅ PASS | All 7 templates live under `dac/addons/allauth/templates/` |
| Social provider loading is guarded | ✅ PASS | `{% load socialaccount %}` only in `socialaccount/snippets/provider_list.html` (conditionally included) |
| No monkey-patching | ✅ PASS | Pure template overrides |

---

## Project Structure

### Documentation (this feature)

```text
specs/001-allauth-signup-page/
├── plan.md              # This file
├── research.md          # Phase 0 output — unknowns resolved
├── data-model.md        # Phase 1 output — runtime entities
├── quickstart.md        # Phase 1 output — developer guide
├── contracts/
│   ├── template-context.md     # Phase 1 — context variable contract
│   └── component-interface.md  # Phase 1 — Cotton component usage
└── tasks.md             # Phase 2 output (/speckit.tasks — NOT created here)
```

### Source Code (repository root)

```text
dac/
└── addons/
    └── allauth/
        └── templates/
            ├── allauth/
            │   ├── layouts/
            │   │   ├── base.html          # MODIFY: extend mvp/base.html
            │   │   └── entrance.html      # MODIFY: entrance-style centered container
            │   └── elements/              # Unchanged for now (manage pages out of scope)
            ├── account/
            │   ├── signup.html            # MODIFY: full rewrite — cotton components only
            │   ├── signup_closed.html     # MODIFY: use <c-card> for message
            │   └── signup_by_passkey.html # CREATE: passkey signup page — <c-entrance> shell, Cotton components (FR-012)
            └── socialaccount/
                ├── signup.html            # MODIFY: social-only signup form
                └── snippets/
                    ├── login.html         # MODIFY: social section via get_providers
                    └── provider_list.html # MODIFY: <c-button> per provider

docs/
└── _static/
    ├── desktop/             # Signup screenshots at 1440×900 (auto-generated by tests)
    └── mobile/              # Signup screenshots at 390×844 (auto-generated by tests)

tests/
└── test_addons/
    └── test_allauth/
        ├── __init__.py
        ├── test_signup_view.py            # Integration tests for signup view/templates
        └── test_signup_e2e.py             # pytest-playwright E2E tests (full user flows)

screenshots/
└── test_signup_screenshots.py             # pytest-playwright viewport screenshot tests (FR-011) — run with: pytest screenshots/
```

**Structure Decision**: Tests mirror the `dac/addons/allauth/` source tree under `tests/test_addons/test_allauth/`. No `test_components/` module is needed as no custom Cotton components are introduced. All template tests are view-level integration tests (render → assert HTML structure) rather than Cotton component unit tests. Screenshot tests (`test_signup_screenshots.py`) live in the root `screenshots/` directory (NOT inside `tests/`) per constitution Principle XIII v1.1.2 — because `pyproject.toml` sets `testpaths = ["tests"]`, a plain `pytest` invocation never discovers `screenshots/`, keeping normal test runs fast. To regenerate screenshots explicitly, run `pytest screenshots/`. The parametrized tests cover 3 viewports × 6 settings permutations (18 files total), writing output to `docs/_static/{desktop,tablet,mobile}/`.

---

## Template Design

### `allauth/layouts/base.html`

**Role**: HTML shell for all allauth pages — wires in django-mvp's CSS, JS, fonts (AdminLTE4, Bootstrap 5, AlpineJS).

```html
{% extends "mvp/base.html" %}
{% load i18n %}
{% block title %}{% block title %}{% endblock %}{% endblock %}
```

**Key**: Only the `title`/`head_title` block mapping is added. The `{% block app %}` block (which controls `<body>` rendering) is left to `allauth/layouts/entrance.html` and future manage layout templates to override.

---

### `allauth/layouts/entrance.html`

**Role**: Centered entrance-style layout for login, signup, password reset, and other pre-auth pages. Delegates entirely to `<c-entrance>` — no layout markup here.

```html
{% extends "allauth/layouts/base.html" %}
{% load i18n %}
{% block app %}
  <body>
    <c-messages dismissible animate />
    <c-entrance cols="12" md="8" lg="5">
      <c-slot name="title">{% block title %}{% endblock title %}</c-slot>
      {% block content %}{% endblock content %}
    </c-entrance>
  </body>
{% endblock %}
```

### `dac/templates/cotton/entrance/index.html` (`<c-entrance>`)

**Role**: The entrance page shell component. Owns the full-viewport centred layout, responsive column sizing, the styled card (`shadow-lg rounded-4 border-0`), and renders `<c-entrance.logo>` + optional `title` above the page's `{{ slot }}`.

```html
<c-vars title />
<c-entrance.background>
  <c-container>
    <c-row class="min-vh-100 w-100 align-items-center justify-content-center">
      <c-col attrs="attrs">
        <c-card class="shadow-lg rounded-4 border-0" only>
          <div class="py-3 py-md-4 px-lg-3">
            <div class="text-center">
              <c-entrance.logo />
              {% if title %}<h4 class="fw-semibold mt-3">{{ title }}</h4>{% endif %}
            </div>
            {{ slot }}
          </div>
        </c-card>
      </c-col>
    </c-row>
  </c-container>
</c-entrance.background>
```

### `dac/templates/cotton/entrance/background.html` (`<c-entrance.background>`)

**Role**: Provides the full-page background style. Developers override this file to change the background (colour, gradient, image) without touching any other template.

```html
<div class="bg-primary-subtle bg-gradient">{{ slot }}</div>
```

### `dac/templates/cotton/entrance/logo.html` (`<c-entrance.logo>`)

**Role**: Renders the site logo inside the card header. No `src` prop — developers override the template file to change the logo.

```html
{% load static i18n %}
<c-vars height="120" alt="{% trans 'Site Logo' %}" class="d-block mx-auto img-fluid" />
<img src="{% static 'dac/logo/dac_bg_transparent.svg' %}"
     alt="{{ alt }}"
     style="height: {{ height }}px; width: auto"
     {{ attrs }} />
```

---

### `account/signup.html`

**Role**: Main signup page — content-only block. No card, no container, no logo markup (all owned by `<c-entrance>`). Title passed via `{% block title %}` to `<c-entrance>`'s named slot.

**Key design points**:

- `{% block title %}` provides the card heading text to `<c-entrance>` — no `<h4>` in the page template
- Social provider buttons rendered via `{% include "socialaccount/snippets/provider_list.html" %}` — uses Bootstrap Icon `<a>` tags, not `<c-button>`, for layout flexibility
- `<c-card.divider text="or">` separates social from email/password section (only when both present)
- `<c-form.crispy />` renders all fields **and** non-field errors (FR-005/FR-006) — no `{% if form.non_field_errors %}` in this template
- Submit button wrapped in `<c-button.stack>` for consistent full-width stacking
- Login link (`{% if login_url %}`) placed at the bottom of the content block, below the form

```html
{% extends "account/base_entrance.html" %}
{% load i18n socialaccount %}

{% block title %}{% trans "Create your account" %}{% endblock title %}

{% block content %}
  {% if SOCIALACCOUNT_ENABLED %}
    {% get_providers as socialaccount_providers %}
    {% if socialaccount_providers %}
      {% include "socialaccount/snippets/provider_list.html" with process="signup" %}
      {% if not SOCIALACCOUNT_ONLY %}
        <c-card.divider text="{% trans 'or' %}" />
      {% endif %}
    {% endif %}
  {% endif %}
  {% if not SOCIALACCOUNT_ONLY %}
    <c-form method="post" action="{% url 'account_signup' %}">
      <c-form.crispy />
      {{ redirect_field }}
      <c-button.stack class="mt-4">
        <c-button text="{% trans \"Let's go!\" }"
                  icon="login"
                  type="submit"
                  variant="primary"
                  reverse />
      </c-button.stack>
    </c-form>
  {% endif %}
  {% if PASSKEY_SIGNUP_ENABLED %}
    <c-card.divider />
    <c-button.stack class="mt-4">
      <c-button href="{{ signup_by_passkey_url }}"
                text="{% trans 'Sign up using a passkey' %}"
                variant="outline-secondary"
                class="w-100" />
    </c-button.stack>
  {% endif %}
  {% if login_url %}
    <p class="text-center text-muted small mt-4 mb-0">
      {% blocktrans with login_url=login_url %}
        Already have an account? <a href="{{ login_url }}">Sign in</a>.
      {% endblocktrans %}
    </p>
  {% endif %}
{% endblock content %}
```

---

### `account/signup_by_passkey.html`

**Role**: Dedicated passkey signup page rendered at `/account-center/signup/passkey/` when both `MFA_PASSKEY_SIGNUP_ENABLED` and `ACCOUNT_EMAIL_VERIFICATION_BY_CODE_ENABLED` are `True`. Uses the `<c-entrance>` shell identically to `signup.html` — no raw Bootstrap layout markup (FR-012).

**Key design points**:

- Extends `account/base_entrance.html` — inherits `<c-entrance>` shell from `entrance.html`
- `{% block title %}` provides the card heading text
- The passkey credential UI is rendered via allauth's template tags/context (the actual WebAuthn JS interaction is handled by allauth's bundled scripts)
- Submit button wrapped in `<c-button.stack>` consistent with `signup.html`
- Back link to main signup page at the bottom

```html
{% extends "account/base_entrance.html" %}
{% load i18n %}

{% block title %}{% trans "Sign up with a passkey" %}{% endblock title %}

{% block content %}
  <c-form method="post">
    <c-form.crispy />
    {{ redirect_field }}
    <c-button.stack class="mt-4">
      <c-button text="{% trans 'Create passkey' %}"
                icon="passkey"
                type="submit"
                size="lg"
                variant="primary"
                 />
    </c-button.stack>
  </c-form>
  {% if signup_url %}
    <p class="text-center text-muted small mt-4 mb-0">
      <a href="{{ signup_url }}">{% trans "Sign up with alternative method" %}</a>
    </p>
  {% endif %}
{% endblock content %}
```

---

### `account/signup_closed.html`

**Role**: Shown when signup is disabled via `is_open_for_signup()` returning `False`.

```html
{% extends "account/base_entrance.html" %}
{% load i18n %}
{% block title %}{% trans "Sign Up Closed" %}{% endblock %}
{% block content %}
  <c-card class="shadow text-center">
    <c-slot name="header">
      <div class="card-header py-3">
        <h4 class="mb-0">{% trans "Sign Up Closed" %}</h4>
      </div>
    </c-slot>
    <p class="mb-0">
      {% trans "We are sorry, but the sign up is currently closed." %}
    </p>
  </c-card>
{% endblock %}
```

---

### `socialaccount/snippets/provider_list.html`

**Role**: Renders one `<c-button>` per configured social provider. Only included when `SOCIALACCOUNT_ENABLED` is `True` (guard lives in `account/signup.html`).

```html
{% load i18n socialaccount %}
{% get_providers as socialaccount_providers %}
{% if socialaccount_providers %}
  <div class="mb-2">
    {% for provider in socialaccount_providers %}
      {% if provider.id == "openid" %}
        {% for brand in provider.get_brands %}
          {% provider_login_url provider openid=brand.openid_url process=process as href %}
          <c-button href="{{ href }}"
                    text="{{ brand.name }}"
                    variant="outline-secondary"
                    class="w-100 mb-2" />
        {% endfor %}
      {% else %}
        {% provider_login_url provider process=process as href %}
        <c-button href="{{ href }}"
                  text="{{ provider.name }}"
                  variant="outline-secondary"
                  class="w-100 mb-2" />
      {% endif %}
    {% endfor %}
  </div>
{% endif %}
```

---

### `socialaccount/snippets/login.html`

**Role**: Social section snippet included from signup (and login) pages; delegates button rendering to `provider_list.html`.

```html
{% load i18n %}
{% include "socialaccount/snippets/provider_list.html" with process=page_layout|default:"login" %}
{% include "socialaccount/snippets/login_extra.html" %}
```

---

### `socialaccount/signup.html`

**Role**: Social-account-only signup form (shown after OAuth callback when additional user details are needed).

```html
{% extends "socialaccount/base_entrance.html" %}
{% load i18n %}
{% block title %}{% trans "Sign Up" %}{% endblock %}
{% block content %}
  <c-card class="shadow">
    <c-slot name="header">
      <div class="card-header text-center py-3">
        <h4 class="mb-0">{% trans "Complete Sign Up" %}</h4>
        <p class="text-muted small mb-0 mt-1">
          {% blocktrans with provider_name=account.get_provider.name site_name=site.name %}
            You are about to use your {{ provider_name }} account to sign in to
            {{ site_name }}. Please complete the form below.
          {% endblocktrans %}
        </p>
      </div>
    </c-slot>
    <c-form method="post" action="{% url 'socialaccount_signup' %}">
      <c-form.crispy />
      {{ redirect_field }}
      <c-button.stack class="mt-3">
        <c-button type="submit"
                  text="{% trans 'Sign Up' %}"
                  variant="primary" />
      </c-button.stack>
    </c-form>
  </c-card>
{% endblock %}
```

---

## Complexity Tracking

No constitution violations. No complexity exceptions needed.

---

## Open Questions / Risks

| Risk | Mitigation |
|---|---|
| `allauth/layouts/base.html` is also inherited by manage-page templates (email, password, MFA, etc.) | These templates will inherit the `mvp/base.html` shell correctly via the base override; manage-specific layout (`allauth/layouts/manage.html`) is out of scope but will function as a plain unstyled page until a manage-layout spec is implemented |
| `{% load socialaccount %}` raises `TemplateSyntaxError` when app not installed | Guarded: tag is only in `socialaccount/snippets/provider_list.html`, which is `{% include %}`d only when `SOCIALACCOUNT_ENABLED` is `True` |
| `signup_by_passkey.html` requires WebAuthn JS from allauth's MFA bundle | allauth injects the required script tags when `MFA_PASSKEY_SIGNUP_ENABLED=True`; the template only needs the form + submit button; no additional JS wiring required in the template |
| `<c-form.crispy />` uses context `form` directly | Verified: allauth SignupView always injects `form` into context; this is guaranteed by the view |
| crispy forms renders a submit button when FormHelper is configured | Allauth's SignupForm does not configure a FormHelper; `{{ form|crispy }}` renders fields only, no auto-submit button |
| Non-field errors must not be duplicated | `<c-form.crispy>` renders a `<c-alert variant="danger">` for `form.non_field_errors` when no FormHelper is present; page templates must not add a second `{% if form.non_field_errors %}` block |
| djlint may flag Cotton template syntax | Use `{# djlint:off #}` / `{# djlint:on #}` around Cotton component tags where needed |
