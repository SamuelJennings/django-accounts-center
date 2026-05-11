# Research: Allauth Password Reset Flow — Template Integration

**Phase**: 0 — Unknowns resolved before design
**Feature**: 003-allauth-password-reset
**Date**: 2026-05-11

---

## Decision 1: Template Inheritance Strategy (inherited from specs 001 & 002)

**Decision**: Reuse the existing template inheritance hierarchy. All five password-reset templates extend `account/base_entrance.html` (DAC override), which delegates to `<c-entrance>`. No new base templates are required.

**Rationale**: The full layout chain is already established and tested:

```
account/password_reset.html          ┐
account/password_reset_done.html     │   all extend account/base_entrance.html
account/password_reset_from_key.html │   (DAC override, verified by specs 001 & 002)
account/password_reset_from_key_done │
account/confirm_password_reset_code  ┘   extends account/base_confirm_code.html
  → account/base_confirm_code.html   (DAC override — MUST be rewritten this spec)
    → account/base_entrance.html     (DAC override: extends allauth/layouts/entrance.html)
      → allauth/layouts/entrance.html (DAC override: delegates to <c-entrance>)
        → allauth/layouts/base.html  (DAC override: extends mvp/base.html)
          → mvp/base.html            (AdminLTE4 + Bootstrap 5)
```

**Alternatives considered**: Creating a dedicated base for the password-reset flow — rejected; unnecessary indirection and no UI benefit.

---

## Decision 2: Current State of Password-Reset Templates

**Decision**: All five templates already exist as DAC overrides in `dac/addons/allauth/templates/account/`, but all still use allauth's `{% element %}` syntax. All must be rewritten.

**Current state analysis**:

| Template | Current State | Action |
|---|---|---|
| `account/password_reset.html` | Overridden; `{% element %}` syntax | **Full rewrite** to Cotton |
| `account/password_reset_done.html` | Overridden; `{% element %}` syntax | **Full rewrite** to Cotton |
| `account/password_reset_from_key.html` | Overridden; `{% element %}` syntax | **Full rewrite** to Cotton (2 branches) |
| `account/password_reset_from_key_done.html` | Overridden; `{% element %}` syntax | **Full rewrite** to Cotton |
| `account/confirm_password_reset_code.html` | Overridden; block-only (extends `base_confirm_code`) | **Validate & update** blocks only |
| `account/base_confirm_code.html` | Overridden; **still uses `{% element %}`** throughout | **Full rewrite** to Cotton (in scope this spec) |

---

## Decision 3: base_confirm_code.html Rewrite Scope

**Decision**: `base_confirm_code.html` must be fully rewritten from `{% element %}` to Cotton components in this spec. `confirm_password_reset_code.html` requires only block-level customisation; no changes to block definitions expected.

**Rationale**: The existing DAC override was a faithful copy of the allauth original but was never converted. All three code-confirmation flows (login code: `confirm_login_code.html`, email verification: `confirm_email_verification_code.html`, password reset: `confirm_password_reset_code.html`) rely on this base. Converting it here benefits all three flows simultaneously. The child templates (`confirm_password_reset_code.html`, `confirm_email_verification_code.html`, `confirm_phone_verification_code.html`) only customise named blocks and require no changes unless a defect is found.

**Alternatives considered**: Bypassing `base_confirm_code.html` for the password-reset code template (as was done for `confirm_login_code.html` in spec 002) — rejected because the password-reset code template has no reason to avoid the shared base, and rewriting the base is lower risk now that the structure is well understood.

**Full structure of base_confirm_code.html** (to be replicated faithfully in Cotton):

- Heading from `{% block title %}`
- "We've sent a code to `{{ recipient }}`..." paragraph
- `<c-form>` wrapping `verify_form` (posted to `{% block action_url %}`)
  - Unlabelled code input fields via `<c-form.crispy form=verify_form />`
  - `{{ redirect_field }}`
  - "Confirm" submit button (`tags=submit_button_tags`)
  - "Request new code" button (shown when `can_resend`) — submits hidden `#resend` form
  - "Cancel" button: `href=cancel_url` if available, else submits hidden `#logout-from-stage` form
- Hidden `<form id="resend">` (POSTs to `action_url` with `action=resend`)
- Hidden `<form id="logout-from-stage">` (POSTs to `account_logout`, next → `account_login`; only when `cancel_url` is absent)
- Collapsible `{% block change_title %}` / `change_form` section (when `can_change`)

---

## Decision 4: Context Variables for Password-Reset Views

**Decision**: Use allauth's built-in context variables directly. No custom context processors or view overrides.

### `account/password_reset.html` — rendered by `PasswordResetView`

| Variable | Type | Always Present | Description |
|---|---|---|---|
| `form` | `ResetPasswordForm` | Yes | Single email field |
| `redirect_field` | `str` | Yes | Hidden `<input>` for next-redirect |
| `user` | `AnonymousUser \| User` | Yes | Used to check `user.is_authenticated` for the already-logged-in snippet |

### `account/password_reset_done.html` — rendered by `PasswordResetDoneView`

| Variable | Type | Always Present | Description |
|---|---|---|---|
| `user` | `AnonymousUser \| User` | Yes | Used to check `user.is_authenticated` |

### `account/password_reset_from_key.html` — rendered by `PasswordResetFromKeyView`

| Variable | Type | Always Present | Description |
|---|---|---|---|
| `form` | `SetPasswordForm` | When `token_fail=False` | Two-field form: new password + confirmation |
| `token_fail` | `bool` | Yes | `True` when the reset token is invalid or expired |
| `action_url` | `str` | When `token_fail=False` | Form POST target (keyed URL) |
| `redirect_field` | `str` | When `token_fail=False` | Hidden next-redirect input |
| `cancel_url` | `str \| None` | Yes | If set, Cancel button uses `href`; if absent, a hidden logout form is rendered |

### `account/password_reset_from_key_done.html` — rendered by `PasswordResetFromKeyDoneView`

No template-specific context variables; inherits only base context.

### `account/confirm_password_reset_code.html` — rendered by `ConfirmPasswordResetCodeView`

Context delegated to `base_confirm_code.html`:

| Variable | Type | Always Present | Description |
|---|---|---|---|
| `verify_form` | `ResetPasswordByCodeForm` (or similar) | Yes | Code entry form |
| `redirect_field` | `str` | Yes | Hidden next-redirect |
| `can_resend` | `bool` | Yes | Whether "Request new code" is offered |
| `can_change` | `bool` | Yes | Whether the collapsible change-address form is shown |
| `change_form` | `Form` | When `can_change` | Form for changing the recipient email |
| `email` | `str` | Yes | Email address displayed in `{% block recipient %}` |
| `cancel_url` | `str \| None` | Yes | URL for cancel button (or absent → logout-from-stage) |

Block overrides in `confirm_password_reset_code.html`:

| Block | Value |
|---|---|
| `head_title` | `{% translate "Password Reset" %}` |
| `title` | `{% translate "Enter Password Reset Code" %}` |
| `recipient` | `<a href="mailto:{{ email }}">{{ email }}</a>` |
| `action_url` | `{% url 'account_confirm_password_reset_code' %}` |
| `extra_tags` | `email,verification` |

---

## Decision 5: Cotton Component Mapping

**Decision**: Use the same Cotton component vocabulary established by specs 001 and 002. No new DAC-owned components needed.

| Allauth `{% element %}` | Cotton equivalent |
|---|---|
| `{% element h1 %}` | `{% block title %}...{% endblock %}` (inside `<c-entrance>`) |
| `{% element p %}` | `<p>` with `{% blocktrans %}` / `{% trans %}` |
| `{% element form %}` with `{% slot body/actions %}` | `<c-form>` with `<c-form.crispy />` + `<c-button>` |
| `{% element button type="submit" %}` | `<c-button type="submit">` |
| `{% element button type="submit" form="..." tags="link,cancel" %}` | `<c-button type="submit" form="logout-from-stage">` |
| `{% element button_group %}` | `<c-button.stack>` |
| `{% element fields form=... %}` | `<c-form.crispy form=... />` |
| `{% element details %}` | `<details>` / `<summary>` |

---

## Decision 6: `password_reset_from_key.html` — Cancel Mechanism

**Decision**: Replicate the allauth original cancel mechanism exactly. A hidden `<form id="logout-from-stage">` is rendered (when `cancel_url` is absent) and the Cancel `<c-button>` submits it via `form="logout-from-stage"`.

**Rationale**: The mid-reset session must be terminated cleanly on cancel. Allauth uses a POST to `account_logout` with `next` pointing to `account_login`. The template must not change this behaviour.

---

## Decision 7: `password_reset.html` — "Contact Us" Paragraph

**Decision**: Include the trailing "Please contact us if you have any trouble resetting your password." paragraph from the allauth original. It is a `{% element p %}` in allauth; in Cotton it becomes a plain `<p>` with `{% blocktrans %}`.

**Rationale**: Allauth-fidelity principle — if the original has it, the Cotton override must have it.

---

## Decision 8: Screenshot Coverage

**Decision**: 5 page states × 3 viewports = 15 screenshots. File naming follows existing conventions.

| State | Screenshot slug |
|---|---|
| `password_reset.html` | `password-reset` |
| `password_reset_done.html` | `password-reset-done` |
| `password_reset_from_key.html` (valid form) | `password-reset-from-key` |
| `password_reset_from_key.html` (invalid token) | `password-reset-from-key-invalid` |
| `password_reset_from_key_done.html` | `password-reset-from-key-done` |

Stored under `docs/_static/{desktop,tablet,mobile}/`.

No settings-permutation screenshots are required: the only configurable variant (code-based reset) routes to a different template (`confirm_password_reset_code.html`) and is covered by integration tests only (not screenshot-tested, as allauth's code-dispatch mechanism is not easily fixtured for Playwright).

---

## Unknowns Resolved

All NEEDS CLARIFICATION items from the spec are resolved. No open questions remain.
