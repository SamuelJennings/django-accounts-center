# Component Interface Contract: Allauth Login Page Cotton Components

**Feature**: 002-allauth-login-page
**Date**: 2026-05-08

This document specifies how the django-accounts-center allauth addon composes its login page UI from Cotton components. No new Cotton components are introduced by this feature — all components were either created in spec 001 (the DAC-owned entrance family) or are consumed from django-mvp and django-cotton-bs5.

---

## DAC-Owned Cotton Components (from spec 001, consumed unchanged)

### `<c-entrance>` — Entrance Page Shell

**Source**: `dac/templates/cotton/entrance/index.html`
**Used in**: `allauth/layouts/entrance.html` (already wired, no change needed)

The login page benefits from `<c-entrance>` automatically via template inheritance. No changes to this component for spec 002.

| Attr/Slot | Type | Purpose |
|---|---|---|
| `cols`, `md`, `lg`, etc. | `str` | Responsive width passed to `<c-col>` |
| `title` (slot) | HTML | Card heading rendered as `<h4 class="fw-semibold mt-3">` |
| default slot | HTML | Card body content |

---

### `<c-entrance.text>` — Subtitle / Cross-Link Text

**Source**: `dac/templates/cotton/entrance/text.html`
**Used in**:

- `account/login.html` — description text (not needed unless social subtitle added), "Forgot password?" link, signup cross-link
- `account/request_login_code.html` — intro description text, "Other sign-in options" link
- `account/confirm_login_code.html` — recipient description text, cancel link

**Interface**:

```html
<c-entrance.text [lead] [class="..."]>
  Content text or inline HTML (links, etc.)
</c-entrance.text>
```

| Attr | Default | Purpose |
|---|---|---|
| `lead` | absent | If present, adds `lead` font sizing |
| `class` | `""` | Additional CSS classes (e.g., `mt-4 mb-0`) |
| default slot | — | Text or HTML content to display |

**Usage examples**:

```html
{# Intro description #}
<c-entrance.text class="mb-3">
  {% trans "You will receive a special code for a password-free sign-in." %}
</c-entrance.text>

{# Forgot password link #}
<c-entrance.text class="mt-2 mb-0">
  <a href="{% url 'account_reset_password' %}">{% trans "Forgot your password?" %}</a>
</c-entrance.text>

{# Sign-up cross-link #}
<c-entrance.text class="mt-4 mb-0">
  {% blocktrans with signup_url=signup_url %}
    Don't have an account? <a href="{{ signup_url }}">Sign up</a>.
  {% endblocktrans %}
</c-entrance.text>
```

---

## Library Components (django-mvp)

### `<c-form>` — Form Wrapper

**Source**: django-mvp (`mvp/templates/cotton/form/index.html`)
**Used in**: `account/login.html`, `account/request_login_code.html`, `account/confirm_login_code.html`

```html
<c-form method="post" action="URL">
  <c-form.crispy />        {# or <c-form.crispy form=verify_form /> #}
  {{ redirect_field }}
  <c-button.stack class="mt-4">
    <c-button ... />
  </c-button.stack>
</c-form>
```

**Renders**: `<form method="post" action="URL" ...>{% csrf_token %} ... </form>`.
`<c-form>` inserts the CSRF token automatically — do NOT add `{% csrf_token %}` separately.

---

### `<c-form.crispy>` — Crispy Form Field Renderer

**Source**: django-mvp (`mvp/templates/cotton/form/crispy.html`)
**Used in**: all three primary forms in this feature

```html
{# Standard usage (renders context variable 'form') #}
<c-form.crispy />

{# Custom form object (required for confirm_login_code.html) #}
<c-form.crispy form=verify_form />
```

**Critical**: On the code-entry page (`confirm_login_code.html`), the form is `verify_form`, not `form`. Pass it explicitly as `form=verify_form`.

**What it handles automatically**:

- All form fields with labels, widgets, and validation state
- Non-field errors (do NOT duplicate with `{% if form.non_field_errors %}`)
- Crispy Bootstrap 5 layout

---

### `<c-card.divider>` — Visual Separator Between Sections

**Source**: django-mvp (`mvp/templates/cotton/card/divider.html`)
**Used in**: `account/login.html` — between social and form, and before passwordless options

```html
<c-card.divider text="or" />
```

| Attr | Default | Purpose |
|---|---|---|
| `text` | `""` | Label text shown centred in the divider line |

---

### `<c-button.stack>` — Vertical Button Container

**Source**: django-mvp (`mvp/templates/cotton/button/stack.html`)
**Used in**: `account/login.html`, `account/request_login_code.html`, `account/confirm_login_code.html`

```html
<c-button.stack [class="..."]>
  <c-button ... />
  <c-button ... />  {# additional buttons if needed #}
</c-button.stack>
```

Renders buttons stacked vertically with consistent spacing.

---

## Library Components (django-cotton-bs5)

### `<c-button>` — Individual Button or Link

**Source**: django-cotton-bs5 (`cotton_bs5/templates/cotton/button.html`)
**Used in**: all login templates for both submit buttons and navigation links

**Interface**:

```html
{# Primary submit button (with icon on left) #}
<c-button text="Sign in"
          icon="login"
          size="lg"
          type="submit"
          variant="primary"
          reverse />

{# Passkey button (with id for WebAuthn script binding) #}
<c-button type="submit"
          form="mfa_login"
          id="passkey_login"
          text="Sign in with a passkey"
          icon="key-fill"
          class="border-light-subtle" />

{# Login-by-code link button #}
<c-button href="{{ request_login_code_url }}"
          text="Send me a sign-in code"
          icon="key"
          class="border-light-subtle" />
```

| Attr | Purpose |
|---|---|
| `text` | Button label |
| `icon` | Bootstrap Icons icon name (without `bi-` prefix) |
| `variant` | Bootstrap colour variant (`primary`, `outline-secondary`, etc.) |
| `size` | Bootstrap button size (`sm`, `lg`) |
| `type` | HTML `type` attribute (`submit`, `button`) |
| `href` | If set, renders as `<a>` instead of `<button>` |
| `form` | Associates button with a named form (for `form="mfa_login"`) |
| `id` | HTML `id` attribute — required for passkey button WebAuthn binding |
| `reverse` | If present, puts icon on the right |
| `class` | Additional CSS classes |

**Pattern for secondary (outline) buttons** (social-alternative controls):

- No `variant` attr → uses default (outline-secondary)
- Add `class="border-light-subtle"` for softer border

**Pattern for primary submit button**:

- `variant="primary"`, `icon="login"`, `size="lg"`, `reverse` (icon right)

---

## Component Dependency Graph

```
account/login.html
  ├─ (via base chain) <c-entrance> ← allauth/layouts/entrance.html
  │   ├─ <c-entrance.background>
  │   ├─ <c-entrance.logo>
  │   ├─ <c-messages>
  │   ├─ <c-container> / <c-row> / <c-col>
  │   └─ <c-card>
  ├─ (included) socialaccount/snippets/provider_list.html
  │   └─ <c-button.stack> + <c-button> per provider
  ├─ <c-card.divider>
  ├─ <c-form>
  │   └─ <c-form.crispy>
  ├─ <c-button.stack>
  │   └─ <c-button> (submit)
  ├─ <c-entrance.text> (forgot password, signup cross-link)
  ├─ <c-card.divider> (before passkey/code section)
  └─ <c-button.stack> (passkey + code buttons)
      └─ <c-button> (×2 if both enabled)

account/request_login_code.html
  ├─ (via base chain) <c-entrance> ← allauth/layouts/entrance.html
  ├─ <c-entrance.text> (intro description)
  ├─ <c-form>
  │   └─ <c-form.crispy>
  ├─ <c-button.stack>
  │   └─ <c-button> (submit)
  └─ <c-entrance.text> (back to login link)

account/confirm_login_code.html
  ├─ (via base chain) <c-entrance> ← allauth/layouts/entrance.html
  ├─ <c-entrance.text> (recipient description)
  ├─ <c-form>  [primary: code entry]
  │   └─ <c-form.crispy form=verify_form>
  ├─ <c-button.stack> (confirm submit, resend, cancel)
  │   ├─ <c-button type="submit"> (confirm)
  │   ├─ <c-button type="submit" form="resend"> (resend, conditional)
  │   └─ <c-button href=cancel_url> OR <c-button type="submit" form="logout-from-stage">
  └─ (raw HTML) <form id="resend"> and <form id="logout-from-stage">
```
