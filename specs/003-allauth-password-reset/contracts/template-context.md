# Template Context Contract: Password Reset Flow

**Feature**: 003-allauth-password-reset
**Date**: 2026-05-11

---

## Contract 1: `account/password_reset.html`

**Rendered by**: `allauth.account.views.PasswordResetView`
**Template chain**: `account/password_reset.html → account/base_entrance.html → allauth/layouts/entrance.html → allauth/layouts/base.html → mvp/base.html`

### Context Variables

| Variable | Type | Always Present | Description |
|---|---|---|---|
| `form` | `ResetPasswordForm` | Yes | Single email field |
| `redirect_field` | `str` | Yes | Raw HTML `<input type="hidden">` for next-redirect. Render with `{{ redirect_field }}`. |
| `user` | `AnonymousUser \| User` | Yes | Used only for `{% if user.is_authenticated %}` check |

### Blocks Used

| Block | Value |
|---|---|
| `head_title` | `{% trans "Password Reset" %}` |
| `title` | `{% trans "Password Reset" %}` |
| `content` | Full page body |

### Template Tag Libraries

| Library | Load Statement | Used For |
|---|---|---|
| `i18n` | `{% load i18n %}` | `{% trans %}`, `{% blocktrans %}` |
| `allauth` | `{% load allauth %}` | `{% url %}` tag alias (if needed) |
| `account` | `{% load account %}` | allauth account tags |

### Rendering Decisions

| Section | Condition | Output |
|---|---|---|
| Already-logged-in snippet | `user.is_authenticated` | `{% include "account/snippets/already_logged_in.html" %}` |
| Description paragraph | Always | `<c-text center>{% trans "Forgotten your password? Enter your email…" %}</c-text>` |
| Email form | Always | `<c-form action=reset_url>` + `<c-form.render form=form />` + `{{ redirect_field }}` + `<c-group><c-button text="Send email" icon="send" size="lg" type="submit" variant="primary" /></c-group>` |
| Contact-us paragraph | Always | `<c-text small text="..." />` |

---

## Contract 2: `account/password_reset_done.html`

**Rendered by**: `allauth.account.views.PasswordResetDoneView`
**Template chain**: same as above

### Context Variables

| Variable | Type | Always Present | Description |
|---|---|---|---|
| `user` | `AnonymousUser \| User` | Yes | Used only for `{% if user.is_authenticated %}` check |

### Blocks Used

| Block | Value |
|---|---|
| `title` | `{% trans "Password Reset" %}` |
| `content` | Informational body — no form |

*Note: no `head_title` block override in this template.*

### Rendering Decisions

| Section | Condition | Output |
|---|---|---|
| Already-logged-in snippet | `user.is_authenticated` | `{% include "account/snippets/already_logged_in.html" %}` |
| Confirmation paragraph | Always | `<c-text center>{% blocktrans %}We have sent you an email. If you have not received it…{% endblocktrans %}</c-text>` |

---

## Contract 3: `account/password_reset_from_key.html`

**Rendered by**: `allauth.account.views.PasswordResetFromKeyView`
**Template chain**: same as above

### Context Variables

| Variable | Type | Always Present | Description |
|---|---|---|---|
| `token_fail` | `bool` | Yes | Selects which branch to render |
| `form` | `SetPasswordForm` | `token_fail=False` | Two password fields |
| `action_url` | `str` | `token_fail=False` | Form POST target |
| `redirect_field` | `str` | `token_fail=False` | Hidden next-redirect input |
| `cancel_url` | `str \| None` | Always | Determines cancel button style |

### Blocks Used

| Block | Value |
|---|---|
| `head_title` | `{% trans "Change Password" %}` |
| `title` | Conditional: `{% trans "Bad Token" %}` or `{% trans "Change Password" %}` |
| `content` | Conditional two-branch body |

### Template Tag Libraries

| Library | Load Statement |
|---|---|
| `i18n` | `{% load i18n %}` |
| `allauth` | `{% load allauth %}` |

### Rendering Decision Table

| Branch | Condition | Output |
|---|---|---|
| Invalid-token | `token_fail=True` | `<c-text>{% blocktrans %}The password reset link was invalid…<a href="{{ passwd_reset_url }}">…{% endblocktrans %}</c-text>` |
| Valid form | `token_fail=False` | `<c-form action=action_url>` + `<c-form.render form=form />` + `{{ redirect_field }}` + `<c-button text="Confirm" icon="submit" variant="primary">` button + "Cancel" `icon="x-circle"` button |
| Cancel (with URL) | `cancel_url` truthy | `<c-button text="Cancel" href=cancel_url icon="x-circle" />` |
| Cancel (no URL) | `cancel_url` falsy | `<c-button text="Cancel" icon="x-circle" type="submit" form="logout-from-stage" />` + hidden `<form id="logout-from-stage">` |

---

## Contract 4: `account/password_reset_from_key_done.html`

**Rendered by**: `allauth.account.views.PasswordResetFromKeyDoneView`
**Template chain**: same as above

### Context Variables

No template-specific variables.

### Blocks Used

| Block | Value |
|---|---|
| `title` | `{% trans "Change Password" %}` |
| `content` | Single confirmation — no form, no button |

*Note: no `head_title` block override in this template.*

### Rendering Decisions

| Section | Condition | Output |
|---|---|---|
| Confirmation paragraph | Always | `<c-text center>{% trans 'Your password is now changed.' %}</c-text>` |

---

## Contract 5: `account/base_confirm_code.html` (shared base)

**Rendered by**: Multiple views — `ConfirmPasswordResetCodeView`, `ConfirmLoginCodeView` (bypassed by spec 002), `ConfirmEmailVerificationCodeView`, `ConfirmPhoneVerificationCodeView`
**Template chain**: `base_confirm_code.html → account/base_entrance.html → …`

### Context Variables

| Variable | Type | Always Present | Description |
|---|---|---|---|
| `verify_form` | form | Yes | Code entry form |
| `redirect_field` | `str` | Yes | Hidden next-redirect |
| `can_resend` | `bool` | Yes | Controls "Request new code" button visibility |
| `can_change` | `bool` | Yes | Controls collapsible change-address section |
| `change_form` | form | When `can_change` | Address change form |
| `cancel_url` | `str \| None` | Yes | Controls cancel button style |

### Blocks Consumed by Child Templates

| Block | Purpose |
|---|---|
| `head_title` | `<title>` text |
| `title` | Heading text (h1) |
| `recipient` | Inline display of the recipient (e.g., `<a href="mailto:…">email</a>`) |
| `action_url` | Form POST URL (also used for resend form action) |
| `extra_tags` | Comma-separated tags forwarded to form/button element tags |
| `change_title` | Summary label for the collapsible change-address section |

### Rendering Decision Table

| Section | Condition | Output |
|---|---|---|
| Heading | Always | `{{ title_ }}` via `<c-entrance>` `title` block |
| Recipient paragraph | Always | "We've sent a code to `{{ recipient }}`…" |
| Confirm form | Always | `<c-form>` wrapping `verify_form`, posted to `action_url` |
| Code input | Always | `<c-form.render form=verify_form unlabeled=True />` |
| `{{ redirect_field }}` | Always | Inside form body |
| "Confirm" button | Always | `type="submit"`, tags from `submit_button_tags` |
| "Request new code" button | `can_resend=True` | Submits `#resend` form |
| Cancel (with URL) | `cancel_url` truthy | `<c-button href=cancel_url>` |
| Cancel (no URL) | `cancel_url` falsy | `<c-button form="logout-from-stage">` |
| Hidden `#resend` form | Always | POSTs to `action_url` with `action=resend` |
| Hidden `#logout-from-stage` form | `cancel_url` falsy | POSTs to `account_logout`, next → `account_login` |
| `<details>` change section | `can_change=True` | Summary from `{% block change_title %}` + `change_form` |

---

## Contract 6: `account/confirm_password_reset_code.html` (child)

**Rendered by**: `allauth.account.views.ConfirmPasswordResetCodeView`
**Extends**: `account/base_confirm_code.html`

This template only sets block values. No Cotton component changes or new context variables.

| Block | Value |
|---|---|
| `head_title` | `{% trans "Password Reset" %}` |
| `title` | `{% trans "Enter Password Reset Code" %}` |
| `recipient` | `<a href="mailto:{{ email }}">{{ email }}</a>` |
| `action_url` | `{% url 'account_confirm_password_reset_code' %}` |
| `extra_tags` | `email,verification` |
