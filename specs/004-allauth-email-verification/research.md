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
`<c-text center>`.

**Alternatives considered**: Rendering the h1 inline as a `<c-text>` — rejected;
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

- Branch A: `<c-entrance>` shell with `<c-text>` descriptive paragraph (not `center`,
  since it contains inline content addressed to the specific user), `<c-form>` with
  `<c-form.render>` not needed (no Django form object — just `{% csrf_token %}` and
  `{{ redirect_field }}`), and a `<c-button.stack>` with
  `<c-button type="submit" icon="check-circle" variant="primary">Confirm</c-button>`.
- Branch B: `<c-text>` with the error prose.
- Branch C: `<c-text>` with the error prose + inline link.

**Note on Branch A form**: The allauth original uses a raw form with only CSRF + redirect
field, no Django form object. `<c-form>` wraps the CSRF and action; the inner `{% csrf_token %}`
and `{{ redirect_field }}` are placed inside. No `<c-form.render>` is needed because there
is no Django form object to render.

---

### 1.3 `account/confirm_email_verification_code.html`

**Allauth original structure**: Extends `account/base_confirm_code.html` with block overrides.

**DAC implementation**: Uses `<c-allauth.confirm-code>` Cotton component directly (the same component used by `confirm_login_code.html` and `confirm_password_reset_code.html`). `base_confirm_code.html` no longer exists — it was replaced by the `cotton/allauth/confirm_code.html` component.

**Allauth resend model** (verified from source):

- `EmailVerificationProcess.can_resend` — overrides base; returns `not is_resend_quota_reached(EMAIL_VERIFICATION_MAX_RESEND_COUNT)`. Starts `True`, becomes `False` after quota hit.
- `PasswordResetVerificationProcess.can_resend` — does NOT override base; always `False`. No `resend()` method.
- `LoginCodeVerificationProcess.can_resend` — same quota pattern as email verification.

**Two-variable resend model**:

- `resend-supported` (Cotton component attribute, set by the parent template) — declares that the flow has a resend mechanism. Must be explicitly set on `<c-allauth.confirm-code>` for flows that support resend.
- `can_resend` (Django view context variable) — quota-based flag. When `resend-supported` is set: `True` → button enabled; `False` → button present but `disabled`.

**Decision**: `confirm_email_verification_code.html` must declare `resend-supported` (email verification supports resend). `confirm_password_reset_code.html` must NOT declare it.

**Component usage**:

```django
<c-allauth.confirm-code recipient="{{ email }}"
                        action="{% url 'account_email_verification_sent' as u %}{{ u }}"
                        resend-url="{% url 'account_email_verification_sent' as u %}{{ u }}"
                        change-title="{% trans 'Use a different email address' %}"
                        resend-supported />
```

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
- Replace `{% element p %}` with `<c-text center>`

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
| `password_reset_done.html` | `verification_sent.html` | `<c-entrance>` + `<c-text center>`, no form |
| `password_reset_from_key_done.html` | `account_inactive.html` | `<c-entrance>` + `<c-text center>`, no form |
| `confirm_password_reset_code.html` | `confirm_email_verification_code.html` | `<c-allauth.confirm-code>` with `resend-supported` |

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
`<c-entrance>`, `<c-text>`, `<c-form>`, `<c-button>`, `<c-button.stack>`.
No new custom components need to be created.
