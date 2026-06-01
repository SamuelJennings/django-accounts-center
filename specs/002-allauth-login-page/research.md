# Research: Allauth Login Page — Template Integration

**Phase**: 0 — Unknowns resolved before design
**Feature**: 002-allauth-login-page
**Date**: 2026-05-08

---

## Decision 1: Template Inheritance Strategy (existing work from spec 001)

**Decision**: Reuse the template inheritance hierarchy established by spec 001. No new base templates are needed; the login page only introduces page-level template overrides.

**Rationale**: Spec 001 already established the full layout chain:

```
account/login.html
  → account/base_entrance.html  (DAC override: extends allauth/layouts/entrance.html)
  → allauth/layouts/entrance.html  (DAC override: delegates to <c-entrance> Cotton component)
  → allauth/layouts/base.html  (DAC override: extends mvp/base.html)
  → mvp/base.html  (AdminLTE4 + Bootstrap 5 shell)
```

The `<c-entrance>` Cotton component and its sub-components (`<c-entrance.background>`, `<c-entrance.logo>`, `<c-text>`) are already implemented and available. This spec only needs to rewrite the page-level content blocks.

**Alternatives considered**: Creating separate base templates per page — rejected for the same reasons as spec 001 (duplication, drift risk).

---

## Decision 2: Current State of Login Templates (pre-existing overrides)

**Decision**: All four login-related templates already exist as DAC overrides but still use allauth's `{% element %}` / `{% endelement %}` syntax. All four must be rewritten to use Cotton components.

**Current state analysis**:

| Template | Location | Current State | Action |
|---|---|---|---|
| `account/login.html` | `dac/addons/allauth/templates/account/login.html` | Overridden; uses `{% element %}` syntax | **Full rewrite** to Cotton |
| `account/request_login_code.html` | `dac/addons/allauth/templates/account/request_login_code.html` | Overridden; uses `{% element %}` syntax | **Full rewrite** to Cotton |
| `account/confirm_login_code.html` | `dac/addons/allauth/templates/account/confirm_login_code.html` | Overridden; extends `base_confirm_code.html` via blocks only | **Full rewrite** — extend `base_entrance.html` directly |
| `account/base_confirm_code.html` | `dac/addons/allauth/templates/account/base_confirm_code.html` | Overridden; uses `{% element %}` syntax throughout | **Out of scope** — not touched by this spec. `confirm_login_code.html` will bypass it by extending `base_entrance.html` directly. |

**Rationale for `confirm_login_code.html` approach**: `base_confirm_code.html` is shared by email verification, password reset, and phone verification confirmation pages. Rewriting it would be a broader change outside this spec's scope. Instead, `confirm_login_code.html` is rewritten as a standalone template extending `account/base_entrance.html` directly, containing its own Cotton-based form rendering. This isolates the change and avoids any risk to the other confirmation templates.

---

## Decision 3: Allauth v65+ Context Variables (Login Views)

**Decision**: Use context variables injected by allauth's `LoginView`, `RequestLoginCodeView`, and `ConfirmLoginCodeView` directly in templates. No custom context processor or view override needed.

### `account/login.html` context (via `allauth.account.views.LoginView`)

| Variable | Type | Always Present | Description |
|---|---|---|---|
| `form` | `LoginForm` | Yes | The login form. Fields depend on `ACCOUNT_AUTHENTICATION_METHOD` and `ACCOUNT_SESSION_REMEMBER`. |
| `SOCIALACCOUNT_ENABLED` | `bool` | Yes | `True` when `allauth.socialaccount` is in `INSTALLED_APPS`. |
| `SOCIALACCOUNT_ONLY` | `bool` | Yes | `True` when email/password login is disabled entirely. |
| `LOGIN_BY_CODE_ENABLED` | `bool` | Yes | `True` when `ACCOUNT_LOGIN_BY_CODE_ENABLED = True`. |
| `PASSKEY_LOGIN_ENABLED` | `bool` | Yes | `True` when `allauth.mfa` is installed and WebAuthn passkey authentication is configured. |
| `signup_url` | `str \| None` | Yes | Resolved URL to the signup page, or `None` when signup is closed. `None` check is the correct way to test `is_open_for_signup()`. |
| `request_login_code_url` | `str \| None` | Yes | Resolved URL for `account_request_login_code`. Present when `LOGIN_BY_CODE_ENABLED`. |
| `redirect_field` | `str` | Yes | HTML `<input type="hidden">` for next-redirect. |
| `redirect_field_name` | `str` | Yes | Name attribute of the redirect field (usually `"next"`). |
| `redirect_field_value` | `str` | Yes | Value of the redirect parameter. |
| `site` | `Site` | Yes | Current Django Sites framework object. |

**`ACCOUNT_AUTHENTICATION_METHOD` and form fields**:

| Setting value | Form field | Label |
|---|---|---|
| `"email"` | `login` | "Email address" |
| `"username"` | `login` | "Username" |
| `"username_email"` | `login` | "Username or Email" |

The label adaptation is handled by allauth's `LoginForm` — the Cotton template does not need to read the setting directly. `<c-form.render />` renders the correct label automatically.

**`ACCOUNT_SESSION_REMEMBER` and the "Remember me" checkbox**:

| Setting value | `remember` field in form | Result |
|---|---|---|
| `None` (default) | Present | `<c-form.render />` renders a "Remember me" checkbox |
| `True` | Absent | No checkbox rendered |
| `False` | Absent | No checkbox rendered |

### `account/request_login_code.html` context (via `RequestLoginCodeView`)

| Variable | Type | Description |
|---|---|---|
| `form` | `RequestLoginCodeForm` | Single email/phone field |
| `request_login_code_url` | `str` | Form action URL |
| `login_url` | `str \| None` | Link back to the main login page |
| `redirect_field` | `str` | Hidden next-redirect input |

### `account/confirm_login_code.html` context (via `ConfirmLoginCodeView` / stage machinery)

| Variable | Type | Description |
|---|---|---|
| `verify_form` | `ConfirmLoginCodeForm` | Single code-entry field |
| `email` | `str \| None` | Email address code was sent to |
| `phone` | `str \| None` | Phone number code was sent to (if phone auth enabled) |
| `can_resend` | `bool` | Whether user can request a new code |
| `redirect_field` | `str` | Hidden next-redirect input |
| `cancel_url` | `str \| None` | URL to cancel and return to login |

**Resend form**: Rendered as a separate `<form id="resend">` with a POST to the same action URL and a hidden `action=resend` field. This is allauth internal machinery.

**Cancel form**: When `cancel_url` is `None`, allauth provides a `<form id="logout-from-stage">` for cancellation. When `cancel_url` is set, it is rendered as a link.

---

## Decision 4: "Forgot Password?" Link Strategy

**Decision**: Render the "Forgot password?" link using `{% url 'account_reset_password' %}` directly in the template. No context variable is provided for this URL.

**Rationale**: Allauth does not inject a `password_reset_url` context variable into the login template. The URL must be resolved inline. This is consistent with how allauth's own default `login.html` handles it (it does not show this link by default, but DAC must add it per FR-005).

**Implementation**:

```html
<c-text class="mt-2 mb-0">
  <a href="{% url 'account_reset_password' %}">{% trans "Forgot your password?" %}</a>
</c-text>
```

The "Forgot password?" link must only appear when the password form is visible (i.e., when `not SOCIALACCOUNT_ONLY`).

---

## Decision 5: Social Provider Rendering — Reuse spec 001 Snippets

**Decision**: Reuse `socialaccount/snippets/provider_list.html` (already using Cotton `<c-group>`) unchanged. Pass `process="login"` (not `"signup"`) when including it from `account/login.html`.

**Rationale**: The `provider_list.html` snippet is already fully Cotton-based from spec 001. The `process` parameter controls the OAuth redirect behaviour on the provider side. For login, use `process="login"`; the template is otherwise identical.

**Guard**: `{% load socialaccount %}` must NOT appear in `account/login.html`. Social rendering continues to live in the isolated snippet, conditionally included via `{% if SOCIALACCOUNT_ENABLED %}`.

---

## Decision 6: Layout Order for `account/login.html`

**Decision**: Social provider buttons → "or" divider → email/password form → "Forgot password?" → passwordless alternatives (passkey, code) → "Don't have an account?" at the bottom.

**Rationale**: Confirmed by clarification Q1 (mirrors signup page). This differs from allauth's own login.html (which places social at the bottom) but is intentional per the spec decision.

| Block | Condition |
|---|---|
| Social provider buttons (via `provider_list.html`) | `SOCIALACCOUNT_ENABLED` and providers exist |
| "or" divider (`<c-card.divider>`) | Social buttons shown AND `not SOCIALACCOUNT_ONLY` |
| Email/password form + "Forgot password?" | `not SOCIALACCOUNT_ONLY` |
| "or" divider + passkey/code buttons | `not SOCIALACCOUNT_ONLY` AND (`PASSKEY_LOGIN_ENABLED` OR `LOGIN_BY_CODE_ENABLED`) |
| "Don't have an account? Sign up" | `signup_url` is truthy |

---

## Decision 7: WebAuthn Script Injection for Passkey Login

**Decision**: Inject `mfa/webauthn/snippets/login_script.html` into the `extra_js` block of `account/login.html` when `PASSKEY_LOGIN_ENABLED` is `True`, passing `button_id="passkey_login"` to match the passkey button's `id` attribute.

**Rationale**: This is the same pattern used in allauth's own `account/login.html`. The script wires the browser's WebAuthn API to the passkey button's click event. Without it, the button renders but clicking does nothing. The script must be conditional to avoid loading unnecessary JavaScript when passkeys are not configured (per FR-015).

**Implementation**:

```html
{% block extra_js %}
  {{ block.super }}
  {% if PASSKEY_LOGIN_ENABLED %}
    {% include "mfa/webauthn/snippets/login_script.html" with button_id="passkey_login" %}
  {% endif %}
{% endblock %}
```

The passkey button in the template must carry `id="passkey_login"` to match this script binding.

---

## Decision 8: `confirm_login_code.html` — Resend and Cancel Form Rendering

**Decision**: Render the resend form as a raw HTML `<form id="resend">` (inline in the template), and the cancel action as either a `<c-text>` link (when `cancel_url` is set) or a hidden form (when it is not). The `<c-form>` component is NOT used for the resend/cancel forms because they are auxiliary controls, not the primary submission form.

**Rationale**: The resend and cancel forms are allauth internal mechanism forms that POST to the same URL with a hidden discriminator field. They are secondary to the code-entry form and should be rendered as compact, visually secondary controls. Using `<c-button>` for their submit triggers and wrapping in `<c-group>` maintains visual consistency without needing `<c-form.render>` (which would incorrectly try to render crispy fields for a form with no visible fields).

**Primary form** (code entry): use `<c-form>` + `<c-form.render />`.
**Resend form**: raw `<form id="resend" method="post">` with a `<c-button type="submit" form="resend">`.
**Cancel**: `<c-text>` link to `cancel_url` when available; otherwise a `<form id="logout-from-stage">` submit via `<c-button>`.
