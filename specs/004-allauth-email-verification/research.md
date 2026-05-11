# Research: Allauth Email Verification Flow

**Feature**: 004-allauth-email-verification  
**Date**: 2026-05-11  
**Status**: Complete — all unknowns resolved

---

## 1. Allauth Source Template Analysis

All four target templates were read from the `django-allauth` workspace at
`allauth/templates/account/`.

### 1.1 `account/verification_sent.html`

**Structure**: Extends `account/base_entrance.html`. Content block contains:

- `{% element h1 %}` with "Verify Your Email Address"
- `{% element p %}` with a single `{% blocktrans %}` paragraph

**Decision**: Replace `{% element h1 %}` with the `<c-entrance>` `title` attribute (set
to `{% trans "Verify Your Email Address" %}`), and replace `{% element p %}` with
`<c-entrance.text center>`.

**Alternatives considered**: Rendering the h1 inline as a `<c-entrance.text>` — rejected;
the page title must come via the `title` slot/attribute of `<c-entrance>` to match the
established pattern.

---

### 1.2 `account/email_confirm.html`

**Structure**: Extends `account/base_entrance.html`. Content block contains three branches:

| Branch | Condition | Content |
|--------|-----------|---------|
| A | `confirmation` and `can_confirm` | Descriptive paragraph + confirm form (`{% url 'account_confirm_email' confirmation.key %}`) + submit button |
| B | `confirmation` and `not can_confirm` | Error paragraph: "Unable to confirm … already confirmed by a different account." |
| C | No `confirmation` | Error paragraph + link to `{% url 'account_email' %}`: "This email confirmation link expired or is invalid. Please issue a new email confirmation request." |

**Context variables**: `confirmation`, `can_confirm`, `redirect_field`, and (via
`{% user_display %}` tag) `user_display`. The `email` variable is available as
`confirmation.email_address.email`.

**Decision**:

- Branch A: `<c-entrance>` shell with `<c-entrance.text>` descriptive paragraph (not `center`,
  since it contains inline content addressed to the specific user), `<c-form>` with
  `<c-form.crispy>` not needed (no Django form object — just `{% csrf_token %}` and
  `{{ redirect_field }}`), and a `<c-button.stack>` with
  `<c-button type="submit" icon="check-circle" variant="primary">Confirm</c-button>`.
- Branch B: `<c-entrance.text>` with the error prose.
- Branch C: `<c-entrance.text>` with the error prose + inline link.

**Note on Branch A form**: The allauth original uses a raw form with only CSRF + redirect
field, no Django form object. `<c-form>` wraps the CSRF and action; the inner `{% csrf_token %}`
and `{{ redirect_field }}` are placed inside. No `<c-form.crispy>` is needed because there
is no Django form object to render.

---

### 1.3 `account/confirm_email_verification_code.html`

**Structure**: Extends `account/base_confirm_code.html`. Block overrides in allauth original:

- `{% block head_title %}` — "Email Verification"
- `{% block title %}` — "Enter Email Verification Code"
- `{% block recipient %}` — `<a href="mailto:{{ email }}">{{ email }}</a>`
- `{% block action_url %}` — `{% url 'account_email_verification_sent' %}`
- `{% block extra_tags %}` — `email,verification`
- `{% block change_title %}` — "Use a different email address"

**DAC `base_confirm_code.html` block API** (verified from source):

- `{% block head_title_ %}` (inner block, inherited via `{% block head_title %}`→`{% block head_title_ %}`)
- `{% block title_ %}` (inner block, inherited via `{% block title %}`→`{% block title_ %}`)
- `{% block recipient %}`
- `{% block action_url %}` — used as `<c-form action="…">`
- `{% block action_url_resend %}` — used as `<form id="resend" action="…">`
- `{% block action_url_change %}` — used inside `<details>` change section (if `can_change`)
- `{% block extra_tags %}` — passed to `<c-button tags="…">`
- `{% block submit_button_tags %}` — wraps `extra_tags`
- `{% block change_title %}` — `<summary>` text

**Decision**: The DAC override must:

1. Use `{% block title_ %}` (not `{% block title %}`) to match `base_confirm_code.html`'s inner block
2. NOT override `head_title_` (per FR-004 and spec assumption)
3. Override `action_url` with fail-silent pattern: `{% url 'account_email_verification_sent' as u %}{{ u }}`
4. Override `action_url_resend` with the same fail-silent pattern (same URL)
5. Override `recipient`, `extra_tags`, and `change_title` as normal
6. The existing DAC file uses `{% block title %}` and direct URL — both must be corrected

**URL name confirmed**: `account_email_verification_sent` (from allauth source).

---

### 1.4 `account/account_inactive.html`

**Structure**: Extends `allauth/layouts/entrance.html` (not `account/base_entrance.html`).
Content block contains:

- `{% element h1 %}` with "Account Inactive"
- `{% element p %}` with "This account is inactive."

**Problem**: Extending `allauth/layouts/entrance.html` directly bypasses the Cotton
`<c-entrance>` component and falls back to allauth's raw HTML layout.

**Decision**:

- Change `{% extends "allauth/layouts/entrance.html" %}` → `{% extends "account/base_entrance.html" %}`
- Replace `{% element h1 %}` with the `title` attribute on `<c-entrance>`
- Replace `{% element p %}` with `<c-entrance.text center>`

---

## 2. Existing DAC Template State

All four target files already exist under
`dac/addons/allauth/templates/account/` but are currently near-verbatim copies
of the allauth originals (using `{% element %}` syntax). No Cotton conversion
has been applied. This means the implementation phase is a pure rewrite — no
new files need to be created, only existing files edited.

---

## 3. Pattern Alignment with Spec 003

| Spec 003 analog | Spec 004 target | Pattern |
|---|---|---|
| `password_reset_done.html` | `verification_sent.html` | `<c-entrance>` + `<c-entrance.text center>`, no form |
| `password_reset_from_key_done.html` | `account_inactive.html` | `<c-entrance>` + `<c-entrance.text center>`, no form |
| `confirm_password_reset_code.html` | `confirm_email_verification_code.html` | Block overrides on `base_confirm_code.html` |

`email_confirm.html` has no direct Spec 003 analog — it is the most complex template
in this feature, requiring three conditional branches, one of which contains a bare
form (no Django form object).

---

## 4. URL Names (Verified)

| Template | URL name | Notes |
|---|---|---|
| `email_confirm.html` form action | `account_confirm_email` | Takes `confirmation.key` kwarg |
| `email_confirm.html` invalid-key branch link | `account_email` | Links to email management |
| `confirm_email_verification_code.html` action | `account_email_verification_sent` | Used for both `action_url` and `action_url_resend` |
| `account_inactive.html` | `account_inactive` | No URL override needed in template |

---

## 5. Test Infrastructure

- Integration tests: `tests/test_addons/test_allauth/test_email_verification_view.py` (new file)
- Screenshot tests: `screenshots/test_email_verification_screenshots.py` (new file)
- Test settings: no new settings flags required; `ACCOUNT_EMAIL_VERIFICATION_BY_CODE_ENABLED`
  must be set `True` in the code-based test to register the `account_email_verification_sent` URL

---

## 6. No New Components Required

All Cotton components used in this feature are already available:
`<c-entrance>`, `<c-entrance.text>`, `<c-form>`, `<c-button>`, `<c-button.stack>`.
No new custom components need to be created.
