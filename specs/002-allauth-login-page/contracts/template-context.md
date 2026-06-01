# Template Context Contract: `account/login.html`

**Feature**: 002-allauth-login-page
**Template**: `dac/addons/allauth/templates/account/login.html`
**Rendered by**: `allauth.account.views.LoginView`
**Template chain**: `account/login.html → account/base_entrance.html → allauth/layouts/entrance.html → allauth/layouts/base.html → mvp/base.html`

---

## Guaranteed Context Variables

| Variable | Type | Always Present | Description |
|---|---|---|---|
| `form` | `LoginForm` | Yes | The login form. Fields vary by `ACCOUNT_AUTHENTICATION_METHOD` and `ACCOUNT_SESSION_REMEMBER`. |
| `SOCIALACCOUNT_ENABLED` | `bool` | Yes | `True` when `allauth.socialaccount` is in `INSTALLED_APPS`. |
| `SOCIALACCOUNT_ONLY` | `bool` | Yes | `True` when email/password login is disabled entirely. |
| `LOGIN_BY_CODE_ENABLED` | `bool` | Yes | `True` when `ACCOUNT_LOGIN_BY_CODE_ENABLED = True`. |
| `PASSKEY_LOGIN_ENABLED` | `bool` | Yes | `True` when passkey authentication is configured via `allauth.mfa`. |
| `signup_url` | `str \| None` | Yes | Resolved signup URL; `None` when signup is closed. |
| `request_login_code_url` | `str \| None` | Yes | Resolved URL to `account_request_login_code`. Non-null when `LOGIN_BY_CODE_ENABLED`. |
| `redirect_field` | `str` | Yes | HTML `<input type="hidden">` for post-login redirect. Render raw with `{{ redirect_field }}`. |
| `redirect_field_name` | `str` | Yes | Name of the redirect field (usually `"next"`). |
| `redirect_field_value` | `str` | Yes | Value of the redirect parameter. |
| `site` | `Site` | Yes | Current Django Sites framework object. |

---

## Template Tag Requirements

| Tag Library | Load Statement | Used For |
|---|---|---|
| `i18n` | `{% load i18n %}` | `{% trans %}`, `{% blocktrans %}` |
| `socialaccount` | Must NOT be loaded here | Social rendering is delegated to the `provider_list.html` snippet |

> **Warning**: `{% load socialaccount %}` must NOT appear in `account/login.html`. Social provider rendering lives in `socialaccount/snippets/provider_list.html` (conditionally included).

---

## Blocks Used

| Block Name | Purpose |
|---|---|
| `head_title` | Page `<title>` — set to `{% trans "Sign In" %}` |
| `title` | Heading inside `<c-entrance>` card — set to `{% trans "Sign in" %}` |
| `content` | Main page body — the entire login form and surrounding UI |
| `extra_js` | Injected after `{{ block.super }}` — used only when `PASSKEY_LOGIN_ENABLED` for WebAuthn script |

---

## Rendering Decision Table

| Section | Condition | Template code |
|---|---|---|
| Social providers | `SOCIALACCOUNT_ENABLED` | `{% include "socialaccount/snippets/provider_list.html" with process="login" %}` |
| "or" divider | Social shown AND `not SOCIALACCOUNT_ONLY` | `<c-card.divider text="or" />` |
| Login form + "Forgot password?" | `not SOCIALACCOUNT_ONLY` | `<c-form>` + `<c-form.render />` + `<c-button>` + `<c-text>` |
| Passkey/code section | `not SOCIALACCOUNT_ONLY` AND (`PASSKEY_LOGIN_ENABLED` OR `LOGIN_BY_CODE_ENABLED`) | `<c-card.divider>` + `<c-group>` |
| Sign-up cross-link | `signup_url` is truthy | `<c-text>` with blocktrans |
| WebAuthn script | `PASSKEY_LOGIN_ENABLED` | `{% include "mfa/webauthn/snippets/login_script.html" %}` |

---

# Template Context Contract: `account/request_login_code.html`

**Feature**: 002-allauth-login-page
**Template**: `dac/addons/allauth/templates/account/request_login_code.html`
**Rendered by**: `allauth.account.views.RequestLoginCodeView`
**Template chain**: same as `account/login.html` → `account/base_entrance.html → ...`

---

## Guaranteed Context Variables

| Variable | Type | Always Present | Description |
|---|---|---|---|
| `form` | `RequestLoginCodeForm` | Yes | Single email (or phone) field. |
| `request_login_code_url` | `str` | Yes | Form action URL for POSTing the code request. |
| `login_url` | `str \| None` | Yes | URL to return to the main login page. |
| `redirect_field` | `str` | Yes | Hidden next-redirect input. |

## Template Tag Requirements

| Tag Library | Load Statement | Used For |
|---|---|---|
| `i18n` | `{% load i18n %}` | `{% trans %}`, `{% blocktrans %}` |

## Blocks Used

| Block Name | Content |
|---|---|
| `head_title` | `{% trans "Request Sign-In Code" %}` |
| `title` | `{% trans "Send me a sign-in code" %}` |
| `content` | Description text + email form + "Other sign-in options" link |

---

# Template Context Contract: `account/confirm_login_code.html`

**Feature**: 002-allauth-login-page
**Template**: `dac/addons/allauth/templates/account/confirm_login_code.html`
**Rendered by**: allauth stage machinery (`LoginByCodeStage` / `ConfirmLoginCodeView`)
**Template chain**: extends `account/base_entrance.html` directly (NOT `base_confirm_code.html`)

---

## Guaranteed Context Variables

| Variable | Type | Always Present | Description |
|---|---|---|---|
| `verify_form` | `ConfirmLoginCodeForm` | Yes | Single code-entry field. **Key is `verify_form`, not `form`**. |
| `email` | `str \| None` | No | Email address the code was sent to. |
| `phone` | `str \| None` | No | Phone number the code was sent to (if phone auth enabled). |
| `can_resend` | `bool` | Yes | `True` when user is allowed to request a new code. |
| `redirect_field` | `str` | Yes | Hidden next-redirect input. |
| `cancel_url` | `str \| None` | No | URL to cancel the flow; `None` when not set. |

## Template Tag Requirements

| Tag Library | Load Statement | Used For |
|---|---|---|
| `i18n` | `{% load i18n %}` | `{% trans %}`, `{% blocktrans %}` |

## Blocks Used

| Block Name | Content |
|---|---|
| `head_title` | `{% trans "Enter Sign-In Code" %}` |
| `title` | `{% trans "Enter Sign-In Code" %}` |
| `content` | Recipient text + code form + "Resend" button + "Cancel" link |

## Special Forms

This template renders **three separate forms**:

| Form | Rendered with | Purpose |
|---|---|---|
| Code entry | `<c-form>` + `<c-form.render form=verify_form />` | Primary — enter the received code |
| Resend | Raw `<form id="resend" method="post">` with hidden `action=resend` | Secondary — request a new code |
| Cancel | Link to `cancel_url` OR raw `<form id="logout-from-stage" method="post">` | Tertiary — abort the flow |

> **Critical**: `<c-form.render>` must receive `form=verify_form` (not the default `form`) because the code-entry form is in `verify_form`, not `form`. The `form` context variable is not present on this page.
