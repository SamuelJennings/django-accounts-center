# Template Context Contract: `account/signup.html`

**Feature**: 001-allauth-signup-page
**Template**: `dac/addons/allauth/templates/account/signup.html`
**Rendered by**: `allauth.account.views.SignupView`
**Template chain**: `account/signup.html → account/base_entrance.html → allauth/layouts/entrance.html → allauth/layouts/base.html → mvp/base.html`

---

## Guaranteed Context Variables

These variables are always injected by `allauth.account.internal.templatekit.get_entrance_context_data()` when `SignupView` renders `account/signup.html`.

| Variable | Type | Always Present | Description |
|---|---|---|---|
| `form` | `BaseSignupForm` | Yes | The signup form. Fields depend on allauth configuration. |
| `SOCIALACCOUNT_ENABLED` | `bool` | Yes | `True` when `allauth.socialaccount` is in `INSTALLED_APPS`. |
| `SOCIALACCOUNT_ONLY` | `bool` | Yes | `True` when password/email login is disabled. |
| `PASSKEY_SIGNUP_ENABLED` | `bool` | Yes | `True` when MFA passkeys are enabled. |
| `LOGIN_BY_CODE_ENABLED` | `bool` | Yes | `True` when email login codes are enabled. |
| `login_url` | `str \| None` | Yes | Resolved URL to the login page, or `None`. |
| `signup_url` | `str \| None` | Yes | Resolved URL to the signup page itself. |
| `signup_by_passkey_url` | `str \| None` | Yes | Resolved URL for passkey signup (only useful when `PASSKEY_SIGNUP_ENABLED`). |
| `redirect_field` | `str` | Yes | HTML `<input type="hidden">` string for next-redirect. Render with `{{ redirect_field }}`. |
| `redirect_field_name` | `str` | Yes | Name attribute of the redirect field (usually `"next"`). |
| `redirect_field_value` | `str` | Yes | Value of the redirect parameter. |
| `site` | `django.contrib.sites.models.Site` | Yes | Current site object from Sites framework. |

---

## Template Tag Requirements

The following template tags must be `{% load %}`ed to use the corresponding features:

| Tag Library | Load Statement | Used For |
|---|---|---|
| `allauth` | `{% load allauth %}` | Not used directly (no `{% element %}` tags) |
| `socialaccount` | `{% load socialaccount %}` | `{% get_providers %}`, `{% provider_login_url %}` |
| `i18n` | `{% load i18n %}` | `{% trans %}`, `{% blocktrans %}` |
| `crispy_forms_tags` | Loaded inside `<c-form.crispy>` | Not loaded in signup.html directly |

> **Warning**: `{% load socialaccount %}` must NOT appear unconditionally in `account/signup.html`. It must only be placed in templates that are included when `SOCIALACCOUNT_ENABLED` is `True`. Use `{% include "socialaccount/snippets/provider_list.html" %}` wrapped in `{% if SOCIALACCOUNT_ENABLED %}`.

---

## Blocks Provided

| Block Name | Purpose |
|---|---|
| `head_title` | Page `<title>` content — should be set to `{% trans "Sign Up" %}` |
| `content` | Main page body content — entire card and form |

---

## Form Field Contract

The `form` object exposes fields according to active allauth settings. The Cotton template must render ALL fields without introspection — `<c-form.crispy />` (which renders `{{ form|crispy }}`) satisfies this automatically.

| Field | Condition for Presence |
|---|---|
| `username` | `ACCOUNT_USERNAME_REQUIRED = True` |
| `email` | `ACCOUNT_EMAIL_REQUIRED = True` |
| `email2` | `ACCOUNT_EMAIL_CONFIRMATION_REQUIRED = True` |
| `password1` | Always (unless passkey-only) |
| `password2` | `ACCOUNT_SIGNUP_PASSWORD_ENTER_TWICE = True` |
| Custom fields | `ACCOUNT_SIGNUP_FORM_CLASS` defines additional fields |
