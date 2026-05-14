# Research: Allauth Password Change Templates

**Feature**: `007-allauth-password-change`  
**Date**: 2026-05-12  
**Status**: N/A — No unknowns requiring research

## Summary

All patterns needed for this feature are established in prior specs. No new
technologies, APIs, or allauth internals are introduced. All decisions are
inherited from the existing DAC addon template architecture.

## Prior Art (by pattern)

### `{% block page.content %}` in management templates

- **Established in**: Spec 005 (`dac/base.html` design)
- **Applied in**: Spec 006 (`email_change.html`, `verified_email_required.html`)
- **Conclusion**: `password_change.html` and `password_set.html` must use
  `{% block page.content %}` (not `{% block content %}`).

### `<c-form.card>` as the preferred management-page form wrapper

- **Established in**: Spec 003 (`password_reset_from_key.html`)
- **Confirmed in**: Spec 006 (`email_change.html`)
- **Conclusion**: Both `password_change.html` and `password_set.html` use
  `<c-form.card>`. Nested `<c-form>` + `<c-card>` is only acceptable when
  `<c-form.card>` cannot provide the required functionality.

### Cotton rewrite replacing `{% element %}` / `{% endelement %}` tags

- **Established in**: Specs 001–004 (signup, login, password-reset, email-verification)
- **Conclusion**: `base_reauthenticate.html` and `reauthenticate.html` are rewritten
  the same way — direct Cotton component substitution, no Python changes needed.

### `<c-entrance.section>` as introductory text wrapper on entrance pages

- **Established in**: Spec 001 (`signup.html`), Spec 002 (`login.html`)
- **Conclusion**: `base_reauthenticate.html` uses `<c-entrance.section>` for the
  "Please reauthenticate…" introductory paragraph.

### Reauthenticate URL availability in tests

- **Question**: Does `account_reauthenticate` require a test-only helper view
  (like `_verified_email_required_view` in Spec 006)?
- **Finding**: `allauth.urls` registers `account_reauthenticate` as a standard URL.
  `tests/urls.py` already includes `allauth.urls`. No helper view is needed.
- **Conclusion**: Tests drive reauthentication via `reverse("account_reauthenticate")`
  with `client.force_login(user)`.

### MFA reauthenticate templates

- **Question**: Does rewriting `base_reauthenticate.html` break `mfa/reauthenticate.html`
  and `mfa/webauthn/reauthenticate.html` (which extend it)?
- **Finding**: Both MFA templates only override `{% block reauthenticate_content %}`.
  They do not reference any allauth `{% element %}` tags from the base. The base
  template rewrite (replacing `{% element %}` in `{% block content %}`) does not
  touch `{% block reauthenticate_content %}`, so both MFA templates continue to work
  unmodified.
- **Conclusion**: MFA reauthenticate templates are out of scope and will not be broken
  by the base template rewrite.
