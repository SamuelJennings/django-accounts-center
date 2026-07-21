# Research: Allauth Signup Page — Template Integration

**Phase**: 0 — Unknowns resolved before design
**Feature**: 001-allauth-signup-page
**Date**: 2026-05-07

---

## Decision 1: Template Inheritance Strategy

**Decision**: Override `allauth/layouts/base.html` to extend `mvp/base.html`, and `allauth/layouts/entrance.html` to extend `mvp/entrance.html`. Do not change any Python view code.

**Rationale**: Allauth v65+ supports template overrides at every level of the layout hierarchy. Overriding the layout base templates is the most surgical change — it wires django-mvp's CSS/JS shell (AdminLTE4, Bootstrap 5, AlpineJS, django-compress) into all allauth templates without touching Python. All downstream templates (`account/signup.html`, `account/signup_closed.html`, `socialaccount/signup.html`, etc.) inherit the new shell automatically.

**Alternatives considered**:

- **Providing a custom base template per-page** (e.g., only override `account/signup.html` to extend `mvp/entrance.html` directly): Rejected — each new template would need to re-establish the base, leading to duplication and drift from future allauth template updates.
- **Custom view subclass**: Rejected — a template override is sufficient (Principle X: template overrides primary).

---

## Decision 2: Allauth v65+ Context Variables (Signup View)

**Decision**: Use context variables injected by allauth's `SignupView` and `get_entrance_context_data()` directly in templates. No custom context processor or view override needed.

**Rationale**: The following variables are always present in the signup template context:

| Variable | Type | Purpose |
|---|---|---|
| `form` | `SignupForm` | The signup form (field set determined by allauth settings) |
| `SOCIALACCOUNT_ENABLED` | `bool` | `True` when `allauth.socialaccount` is in `INSTALLED_APPS` |
| `SOCIALACCOUNT_ONLY` | `bool` | `True` when password login is disabled entirely |
| `PASSKEY_SIGNUP_ENABLED` | `bool` | `True` when MFA passkeys are enabled |
| `login_url` | `str` | Resolved URL to the login page |
| `signup_by_passkey_url` | `str` | Resolved URL for passkey signup |
| `redirect_field` | `str` | Hidden `<input>` HTML for post-signup redirect |
| `redirect_field_name` | `str` | Usually `"next"` |
| `redirect_field_value` | `str` | Value of the redirect parameter |
| `site` | `Site` | Current Django Sites framework object |

**Source**: `allauth.account.internal.templatekit.get_entrance_context_data()` and `allauth.account.views.SignupView`.

**Signup disabled detection**: Allauth has no `ACCOUNT_ALLOW_SIGNUPS` setting. Instead, `CloseableSignupMixin.dispatch()` calls `get_adapter(request).is_open_for_signup(request)`. If `False`, the view renders `account/signup_closed.html` — there is no extra context variable for this. The `signup_closed.html` template is simply rendered in place of `signup.html`.

**Alternatives considered**:

- Adding a custom context processor to inject extra variables: Not needed — allauth provides everything required.

---

## Decision 3: Social Provider Detection in Templates

**Decision**: Use `{% load socialaccount %}{% get_providers as socialaccount_providers %}` to enumerate available social providers, then render a `<c-button>` per provider using `{% provider_login_url provider process="signup" as href %}`.

**Rationale**: The `{% get_providers %}` template tag is the documented public API for listing active social providers in templates. It returns a sorted list of non-hidden provider objects. This avoids any dependency on allauth's `{% element %}` / `{% endelement %}` system, which we must not use (FR-008).

**Template tag API**:

```django
{% load socialaccount %}

{# Get list of configured providers #}
{% get_providers as socialaccount_providers %}

{# Get the login/signup URL for a provider #}
{% provider_login_url provider process="signup" as provider_url %}

{# Iterate and render provider links with Bootstrap Icons #}
{% for provider in socialaccount_providers %}
  {% provider_login_url provider process="signup" as provider_url %}
  <a href="{{ provider_url }}"
     class="btn btn-outline-secondary d-flex align-items-center justify-content-center gap-2 py-2 fw-medium">
    <i class="bi bi-{{ provider.id }}"></i>
    {{ provider.name }}
  </a>
{% endfor %}
```

**Guard condition**: The `{% get_providers %}` tag should only be loaded/called when `SOCIALACCOUNT_ENABLED` is `True`. When `allauth.socialaccount` is not in `INSTALLED_APPS`, the `{% load socialaccount %}` tag itself will raise a `TemplateSyntaxError`. Therefore, social provider rendering must be placed in a separate included template (e.g., `socialaccount/snippets/provider_list.html`) that is only `{% include %}`d when `SOCIALACCOUNT_ENABLED` is `True`.

**Alternatives considered**:

- Using allauth's `{% element provider_list %}` and `{% element provider %}`: Explicitly prohibited (FR-008).
- Rendering provider data from a custom context processor: Over-engineering for what template tags already provide.

---

## Decision 4: Form Field Rendering Strategy

**Decision**: Use `<c-card>` (django-mvp) as the outer container and `<c-form>` (django-mvp) as the form element, with explicit markup inside the card body. Form fields are rendered via `<c-form.render />`. No modifications to any django-mvp component are required.

**Rationale**:

- The card + form structure involves conditional sections (social buttons, `SOCIALACCOUNT_ONLY` guard, passkey button) that make `<c-form>`'s slot system more complex than explicit markup.
- `<c-form>` handles the `<form>` tag and auto-injects `{% csrf_token %}` for POST requests — the only boilerplate saved.
- `<c-form.render />` renders `{{ form|crispy }}` which applies crispy-bootstrap5 styling to all fields (FR-006 satisfied automatically).
- Social provider buttons (which are `<a>` links, not inputs) sit as direct card body children **above** the `<c-form>` element — cleanly outside the HTML form.
- No django-mvp component modifications required (Principle IX: use components as-is).

**Form structure skeleton** (in `account/signup.html` — content-only, no card markup):

```html
{# --- Social provider links (above form) --- #}
{% if SOCIALACCOUNT_ENABLED %}
  {% get_providers as socialaccount_providers %}
  {% if socialaccount_providers %}
    {% include "socialaccount/snippets/provider_list.html" with process="signup" %}
    {% if not SOCIALACCOUNT_ONLY %}
      <c-divider text="{% trans 'or' %}" />
    {% endif %}
  {% endif %}
{% endif %}

{# Password form #}
{% if not SOCIALACCOUNT_ONLY %}
  <c-form method="post" action="{% url 'account_signup' %}">
    <c-form.render />
    {{ redirect_field }}
    <c-group class="mt-4">
      <c-button text="{% trans \"Let's go!\" %}"
                icon="login"
                type="submit"
                variant="primary"
                reverse />
    </c-group>
  </c-form>
{% endif %}

{# Passkey option #}
{% if PASSKEY_SIGNUP_ENABLED %}
  <c-divider />
  <c-group class="mt-4">
    <c-button href="{{ signup_by_passkey_url }}"
              text="{% trans 'Sign up using a passkey' %}"
              variant="outline-secondary" />
  </c-group>
{% endif %}
```

**Alternatives considered**:

- **`<c-form>`**: Cleaner for simple forms but its slot system becomes unwieldy with the social/SOCIALACCOUNT_ONLY/passkey conditionals present on the signup page.
- **Manual `<form>` tag**: No advantage over `<c-form>` — `<c-form>` saves the `{% csrf_token %}` line and is a django-mvp component.
- **`{% crispy form %}`** (tag, not filter): Renders a full `<form>` tag, preventing control over the form action, redirect field injection, and submit button placement.

---

## Decision 5: Cotton Component Stack for the Signup UI

**Decision**: Use `<c-entrance>` (DAC Cotton component, `dac/templates/cotton/entrance/index.html`) as the entrance page shell, `<c-entrance.background>` for background styling, `<c-entrance.logo>` for the logo, `<c-divider>` for the "or" separator, `<c-group>` (django-mvp) + `<c-button>` (django-cotton-bs5) for submit and passkey buttons, and `<c-messages>` (django-mvp) for flash messages. Non-field errors are rendered inside `<c-form.render>` via `<c-alert variant="danger">` — not as a standalone block in page templates.

**Rationale**: The entrance shell pattern (full-viewport layout, card, logo, title) is shared across all entrance pages. Extracting it into `<c-entrance>` removes duplication and gives developers a clean, single-file override for background and logo without touching any page template. Social provider buttons use Bootstrap Icon `<a>` tags rather than `<c-button>` because the icon+label flex layout is simpler as raw HTML.

| UI Element | Component | Source |
|---|---|
| Entrance page shell | `<c-entrance>` | DAC (`dac/templates/cotton/entrance/`) |
| Page background style | `<c-entrance.background>` | DAC (`dac/templates/cotton/entrance/`) |
| Site logo | `<c-entrance.logo>` | DAC (`dac/templates/cotton/entrance/`) |
| Form field "or" divider | `<c-divider text="or">` | django-mvp |
| Social provider button | Bootstrap Icon `<a>` tag (raw HTML) | N/A |
| Submit button stack | `<c-group>` | django-mvp |
| Submit / passkey button | `<c-button>` | django-cotton-bs5 |
| Flash messages | `<c-messages dismissible animate>` | django-mvp |
| Non-field error alert | `<c-alert variant="danger">` inside `<c-form.render>` | django-cotton-bs5 |

**Alternatives considered**:

- Creating a custom `<c-dac-provider-button>` Cotton component: Rejected — Bootstrap Icon `<a>` tags give the necessary icon+label layout without a custom component.
- Using raw HTML `<div class="card">` for the container: N/A — the card is now owned by `<c-entrance>`; page templates are content-only.

---

## Decision 6: Template File Scope — What Changes

**Decision**: Modify the following templates already copied into `dac/addons/allauth/templates/`. No new Python files required.

| Template | Change |
|---|---|
| `allauth/layouts/base.html` | Replace to extend `mvp/base.html`; wire title block |
| `allauth/layouts/entrance.html` | Delegate to `<c-entrance>` Cotton component; pass `title` slot and responsive-width attrs |
| `account/signup.html` | Full rewrite — content-only block; no card/logo markup; social guards; `<c-form.render />`; `<c-group>` submit; login link at bottom |
| `account/signup_closed.html` | Rewrite — content-only closed message |
| `socialaccount/signup.html` | Rewrite — social-only signup form without `{% element %}` tags |
| `socialaccount/snippets/provider_list.html` | Rewrite — Bootstrap Icon `<a>` tags per provider |
| `socialaccount/snippets/login.html` | Rewrite — render social section via `{% get_providers %}` without `{% element %}` |

**Templates NOT changed** (yet): All `account/base_manage*.html`, `allauth/layouts/manage.html`, and all manage-page templates — those are out of scope for this spec.

**Alternatives considered**:

- Also rewriting all manage templates now: Out of scope (spec is signup-only). The layout chain for manage pages will be addressed in a future spec once the entrance pattern is validated.

---

## Decision 7: Passkey Signup Support

**Decision**: Render the "Sign up using a passkey" button conditionally using the `PASSKEY_SIGNUP_ENABLED` context variable, separated by a `<c-divider>` from the rest of the form.

**Rationale**: `PASSKEY_SIGNUP_ENABLED` is a boolean already injected by allauth's `get_entrance_context_data()`. When `True`, the passkey signup URL is available in `signup_by_passkey_url`. No additional work is needed.

---

## Decision 8: Testing Strategy

**Decision**: Use pytest + pytest-django for unit/integration tests; pytest-playwright for E2E and screenshot tests. Cotton component tests for the new `<c-entrance>` family would use `cotton_render_soup` from `django-cotton-bs5` if needed, but view-level integration tests are sufficient because the components have no conditional logic of their own.

1. **View/template integration tests** — assert rendered HTML structure for each allauth configuration permutation (email-only, username+email, social enabled/disabled, signup closed).
2. **E2E tests** — full user signup flow through a real browser.

**Alternatives considered**:

- Visual snapshot tests: Rejected per SC-006 and FR-010 (no automated visual regression required).
