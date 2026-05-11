# Quickstart: Allauth Email Verification Flow

**Feature**: 004-allauth-email-verification  
**Date**: 2026-05-11

---

## What This Feature Delivers

Four allauth template overrides that replace `{% element %}` syntax with Cotton
components, making the email-verification flow visually consistent with the signup
and login pages already modernised in Specs 001 and 002.

| Template | Description |
|---|---|
| `account/verification_sent.html` | Informational page shown after signup with mandatory verification |
| `account/email_confirm.html` | Confirmation page for link-based verification (valid + invalid-key branches) |
| `account/confirm_email_verification_code.html` | Code-entry page for code-based verification |
| `account/account_inactive.html` | Error page shown when a deactivated account attempts to log in |

---

## No Developer Configuration Required

These are drop-in template overrides. No Django settings changes, URL additions,
or Python code changes are needed. Installing `dac.addons.allauth` in `INSTALLED_APPS`
is sufficient.

For the code-based verification page to be reachable, the Django project must have:

```python
ACCOUNT_EMAIL_VERIFICATION_BY_CODE_ENABLED = True
```

Without this setting, `confirm_email_verification_code.html` is never served; the
template override is a no-op and causes no errors.

---

## Testing Locally

```bash
# Run integration tests
poetry run pytest tests/test_addons/test_allauth/test_email_verification_view.py --no-cov -q

# Run screenshot tests (regenerates docs/_static/{desktop,tablet,mobile}/email-verification-*.png)
poetry run pytest screenshots/test_email_verification_screenshots.py
```

---

## File Locations

```
dac/addons/allauth/templates/account/
├── verification_sent.html        ← rewritten (was {% element %})
├── email_confirm.html            ← rewritten (was {% element %})
├── confirm_email_verification_code.html  ← corrected (title_ block + fail-silent URLs)
└── account_inactive.html         ← rewritten (extends base_entrance.html now)

tests/test_addons/test_allauth/
└── test_email_verification_view.py   ← new integration tests

screenshots/
└── test_email_verification_screenshots.py  ← new screenshot tests

docs/_static/{desktop,tablet,mobile}/
├── email-verification-sent.png
├── email-confirm-valid.png
├── email-confirm-invalid.png
├── email-verification-code.png
└── account-inactive.png
```
