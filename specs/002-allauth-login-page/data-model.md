# Data Model: Allauth Login Page

**Feature**: 002-allauth-login-page
**Phase**: 1 — Design artifacts
**Date**: 2026-05-08

---

## Overview

This feature introduces no new database models, migrations, or Python classes. It consists entirely of template overrides. The "data model" for this feature is the set of **runtime entities** — allauth-owned forms and context objects — that the Cotton templates receive and render.

All entities below are **read-only** from the template's perspective. Templates must not mutate them.

---

## Runtime Entity 1: `LoginForm`

**Source**: `allauth.account.forms.LoginForm`
**Present in**: `account/login.html`
**Context key**: `form`

### Fields (dynamic — depend on allauth settings)

| Field name | Type | Condition for presence |
|---|---|---|
| `login` | `CharField` | Always present; label changes with `ACCOUNT_AUTHENTICATION_METHOD` |
| `password` | `PasswordField` | Always present when password login is active |
| `remember` | `BooleanField` | Only when `ACCOUNT_SESSION_REMEMBER = None` |

### Rendering

`<c-form.crispy />` renders all fields via `{{ form|crispy }}`. The template does NOT introspect individual fields — `<c-form.crispy />` handles label rendering, validation feedback, and CSRF automatically.

---

## Runtime Entity 2: `RequestLoginCodeForm`

**Source**: `allauth.account.forms.RequestLoginCodeForm`
**Present in**: `account/request_login_code.html`
**Context key**: `form`

### Fields

| Field name | Type | Description |
|---|---|---|
| `email` | `EmailField` | Email address to receive the sign-in code |

### Rendering

`<c-form.crispy />` renders the single email field. No introspection needed.

---

## Runtime Entity 3: `VerifyCodeForm` / `ConfirmLoginCodeForm`

**Source**: `allauth.account.forms.ConfirmLoginCodeForm` (internal)
**Present in**: `account/confirm_login_code.html`
**Context key**: `verify_form`

> **Note**: This form uses the context key `verify_form`, not `form`. `<c-form>` must bind to this by setting the `form` attribute.

### Fields

| Field name | Type | Description |
|---|---|---|
| `code` | `CharField` | The 6-digit (or N-digit) numeric sign-in code |

### Rendering

The `<c-form.crispy />` component must be passed `form=verify_form` to render this form's fields with crispy layout. Use `<c-form.crispy form=verify_form />`.

---

## Runtime Entity 4: `SocialProvider`

**Source**: `allauth.socialaccount.providers.base.Provider` (abstract base)
**Present in**: `account/login.html` (via included snippet)
**Context key**: Retrieved via `{% get_providers as socialaccount_providers %}` template tag

### Relevant attributes (used in provider_list.html)

| Attribute | Type | Description |
|---|---|---|
| `id` | `str` | Provider identifier (e.g., `"google"`, `"github"`). Used to select Bootstrap Icon. |
| `name` | `str` | Human-readable name (e.g., `"Google"`, `"GitHub"`). Used as button label. |

### Rendering

Already handled by `socialaccount/snippets/provider_list.html` (implemented in spec 001). The login page only needs to `{% include %}` it with `process="login"`.

---

## Runtime Entity 5: Login Page Configuration Flags

These boolean flags drive conditional rendering in `account/login.html`. They are injected as template context by allauth's `LoginView`.

| Flag | Source | Effect on template |
|---|---|---|
| `SOCIALACCOUNT_ENABLED` | `allauth.socialaccount` in `INSTALLED_APPS` | Show/hide social provider section |
| `SOCIALACCOUNT_ONLY` | `SOCIALACCOUNT_ONLY` allauth setting | Hide email/password form and passkey/code alternatives |
| `LOGIN_BY_CODE_ENABLED` | `ACCOUNT_LOGIN_BY_CODE_ENABLED` setting | Show/hide "Send me a sign-in code" button |
| `PASSKEY_LOGIN_ENABLED` | MFA app + WebAuthn configuration | Show/hide "Sign in with a passkey" button; inject WebAuthn script |

---

## Runtime Entity 6: URL References

These string URL values are injected as context variables and used for navigation between login-flow templates.

| Context variable | Used in template | Description |
|---|---|---|
| `signup_url` | `account/login.html` | Cross-link to signup (shown when truthy) |
| `request_login_code_url` | `account/login.html`, `account/request_login_code.html` | URL for the login-by-code request form |
| `login_url` | `account/request_login_code.html` | Link back to main login page |
| `cancel_url` | `account/confirm_login_code.html` | Cancel sign-in code flow (may be `None`) |

URL `account_reset_password` is resolved inline via `{% url 'account_reset_password' %}` in `account/login.html` — no context variable is available for it from the login view.

---

## State Transitions

The login-by-code flow has three stages. The relevant templates cover all three states:

```
[account/login.html]
  ↓  (user clicks "Send me a sign-in code")
[account/request_login_code.html]
  ↓  (user submits email; code is emailed)
[account/confirm_login_code.html]
  ↓  (user enters code correctly)
[logged in → redirect]
```

For passkey login, the `account/login.html` template triggers the WebAuthn browser dialog directly via the injected script — no intermediate template is shown.

For social login, the `account/login.html` template links to the provider OAuth flow — no intermediate template is shown within this feature's scope.
