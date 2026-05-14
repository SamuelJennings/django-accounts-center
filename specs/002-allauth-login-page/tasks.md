**Propagated**: 2026-05-09 — Updated from spec.md refinement (FR-016 / User Story 7: socialaccount templates added to scope)

# Tasks: Allauth Login Page

**Input**: Design documents from `specs/002-allauth-login-page/`
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, contracts/ ✅, quickstart.md ✅

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies on incomplete tasks)
- **[Story]**: Which user story this task belongs to (US1–US6)
- Include exact file paths in descriptions

## Implementation Strategy

**MVP scope**: Complete Phase 3 (US1 + US2) first — this delivers the styled email/password login page. All P2 phases (US3, US4, US6) are independent of each other and can be implemented in any order afterward.

**Key facts**:

- `account/login.html` covers US1, US2, US3, US5, and US6 — it is written once as a complete file (T002)
- `account/request_login_code.html` and `account/confirm_login_code.html` cover US4 and are independent of T002
- No new Python code, models, or Cotton components are introduced
- All shared infrastructure (`<c-entrance>`, `allauth/layouts/entrance.html`, `socialaccount/snippets/provider_list.html`) is implemented and unchanged from spec 001

---

## Phase 1: Setup

**Purpose**: Create the integration test module skeleton so test tasks can be executed independently.

- [X] T001 Create tests/test_addons/test_allauth/test_login_view.py with empty test class structure and required imports (`pytest`, `@pytest.mark.django_db`, allauth URL names, `override_settings`)

---

## Phase 2: Foundational (N/A)

All shared infrastructure from spec 001 is in place. No foundational tasks needed — user story implementation begins immediately in Phase 3.

---

## Phase 3: US1 + US2 — Developer Integration & Email/Password Login (Priority: P1) 🎯 MVP

**Goal**: A developer adds `"dac"` and `"dac.addons.allauth"` to `INSTALLED_APPS` and immediately gets a styled, functional login page. End users log in with email/password credentials through Cotton-rendered forms.

**Independent Test**: Add `"dac.addons.allauth"` to `INSTALLED_APPS`, visit `/accounts/login/` as anonymous user — page renders with `<c-entrance>` shell, email/password form, "Forgot password?" link, and signup cross-link at the bottom. No `{% element %}` syntax in rendered HTML.

- [X] T002 [US1] Write dac/addons/allauth/templates/account/login.html — complete Cotton rewrite of the existing `{% element %}`-based placeholder. Template must:
      - `{% extends "account/base_entrance.html" %}` + `{% load i18n %}`
      - `{% block title %}{% trans "Sign In" %}{% endblock title %}`
      - `{% block title %}{% trans "Sign in" %}{% endblock title %}`
      - `{% block content %}` — ordered sections:
          1. `{% if SOCIALACCOUNT_ENABLED %}` → `{% include "socialaccount/snippets/provider_list.html" with process="login" %}` → `{% if not SOCIALACCOUNT_ONLY %}<c-card.divider text="or" />{% endif %}` `{% endif %}`
          2. `{% if not SOCIALACCOUNT_ONLY %}` → `<c-form method="post" action=".">` + `<c-form.crispy />` + `{{ redirect_field }}` + `<c-button.stack class="mt-4">` + `<c-button text="Sign in" icon="login" size="lg" type="submit" variant="primary" reverse />` + `</c-button.stack></c-form>` + `<c-text class="mt-2 mb-0">` "Forgot your password?" link to `{% url 'account_reset_password' %}` `</c-text>` `{% endif %}`
          3. `{% if not SOCIALACCOUNT_ONLY and (PASSKEY_LOGIN_ENABLED or LOGIN_BY_CODE_ENABLED) %}` → `<c-card.divider text="or" />` + `<c-button.stack>` + passkey `<c-button id="passkey_login" .../>` (if `PASSKEY_LOGIN_ENABLED`) + code `<c-button href="{{ request_login_code_url }}" .../>` (if `LOGIN_BY_CODE_ENABLED`) + `</c-button.stack>` `{% endif %}`
          4. `{% if signup_url %}` → `<c-text class="mt-4 mb-0">{% blocktrans %}Don't have an account? <a href="{{ signup_url }}">Sign up</a>.{% endblocktrans %}</c-text>` `{% endif %}`
      - `{% block extra_js %}{{ block.super }}{% if PASSKEY_LOGIN_ENABLED %}{% include "mfa/webauthn/snippets/login_script.html" with button_id="passkey_login" %}{% endif %}{% endblock extra_js %}`
- [X] T003 [P] [US2] Write email/password login tests in tests/test_addons/test_allauth/test_login_view.py covering:
      - Login page renders (200 OK) for anonymous user
      - Form renders email/password fields (no `{% element %}` tags in output)
      - POST invalid credentials → page re-renders with error message, no `{% if form.non_field_errors %}` block in template source (FR-007)
      - `ACCOUNT_AUTHENTICATION_METHOD="email"` → login field label is "Email address" (parametrize all three)
      - `ACCOUNT_AUTHENTICATION_METHOD="username"` → login field label is "Username"
      - `ACCOUNT_AUTHENTICATION_METHOD="username_email"` → login field label is "Username or Email"
      - "Remember me" checkbox present when `ACCOUNT_SESSION_REMEMBER=None`
      - "Remember me" checkbox absent when `ACCOUNT_SESSION_REMEMBER=True`
      - "Forgot password?" link present with `href` pointing to password reset URL
      - Signup cross-link present at bottom when `signup_url` is set
      - Signup cross-link absent when signup is closed

**Checkpoint**: Phase 3 done when all US2 tests pass.

- [X] TVAL-1 [US1] Run `python manage.py check` — MUST produce no errors
- [X] TVAL-2 [US2] Run `poetry run pytest tests/test_addons/test_allauth/test_login_view.py -k "login"` — MUST pass

---

## Phase 4: US3 — Social Login (Priority: P2)

**Goal**: Social login provider buttons appear at the top of the login card, above a horizontal divider and the email/password form, when `allauth.socialaccount` is installed and providers are configured.

**Independent Test**: Configure a mock social provider, visit `/accounts/login/`, confirm social buttons appear above the "or" divider. Set `SOCIALACCOUNT_ONLY=True`, confirm the email/password form and passkey/code buttons are hidden.

- [X] T004 [P] [US3] Write social login rendering tests in tests/test_addons/test_allauth/test_login_view.py covering:
      - No social section rendered when `SOCIALACCOUNT_ENABLED=False`
      - Social buttons rendered when `SOCIALACCOUNT_ENABLED=True` and provider is configured
      - "or" divider present when social buttons AND form are both visible
      - Email/password form hidden when `SOCIALACCOUNT_ONLY=True`
      - Passkey and login-by-code buttons hidden when `SOCIALACCOUNT_ONLY=True`

**Checkpoint**: Phase 4 done when all US3 tests pass.

---

## Phase 5: US4 — Login by Code (Priority: P2)

**Goal**: Both login-by-code page templates render within the `<c-entrance>` shell using Cotton components, visually consistent with the main login page.

**Independent Test**: Set `ACCOUNT_LOGIN_BY_CODE_ENABLED=True`, visit the request-code URL, confirm it renders with `<c-entrance>` shell and email form. Visit the confirm-code URL, confirm it renders with `<c-entrance>` shell and code-entry form. Neither template contains `{% element %}` syntax.

- [X] T005 [P] [US4] Write dac/addons/allauth/templates/account/request_login_code.html — full Cotton rewrite:
      - `{% extends "account/base_entrance.html" %}` + `{% load i18n %}`
      - `{% block title %}{% trans "Request Sign-In Code" %}{% endblock title %}`
      - `{% block title %}{% trans "Send me a sign-in code" %}{% endblock title %}`
      - `{% block content %}`: `<c-text class="mb-3">{% blocktrans %}You will receive a special code for a password-free sign-in.{% endblocktranslate %}</c-text>` → `<c-form method="post" action="{{ request_login_code_url }}">` + `<c-form.crispy />` + `{{ redirect_field }}` + `<c-button.stack class="mt-4">` + `<c-button text="Send Code" icon="send" type="submit" variant="primary" size="lg" />` + `</c-button.stack></c-form>` → `<c-text class="mt-3 mb-0"><a href="{{ login_url }}">{% trans "Other sign-in options" %}</a></c-text>`
- [X] T006 [US4] Write dac/addons/allauth/templates/account/confirm_login_code.html — full Cotton rewrite extending `account/base_entrance.html` directly (NOT `account/base_confirm_code.html`):
      - `{% extends "account/base_entrance.html" %}` + `{% load i18n %}`
      - `{% block title %}{% trans "Enter Sign-In Code" %}{% endblock title %}`
      - `{% block title %}{% trans "Enter Sign-In Code" %}{% endblock title %}`
      - `{% block content %}`: recipient description text via `<c-text>` (show email or phone from context) → place the two auxiliary form elements outside the button stack (invisible): `{% if can_resend %}<form id="resend" method="post">{% csrf_token %}<input type="hidden" name="action" value="resend"></form>{% endif %}` and `{% if not cancel_url %}<form id="logout-from-stage" method="post">{% csrf_token %}</form>{% endif %}` → primary `<c-form method="post" action=".">` + `<c-form.crispy form=verify_form />` + `{{ redirect_field }}` + `<c-button.stack class="mt-4">` containing ALL action buttons: `<c-button text="Confirm" icon="check-circle" type="submit" variant="primary" size="lg" />` + `{% if can_resend %}<c-button type="submit" form="resend" text="Resend Code" icon="arrow-repeat" class="border-light-subtle" />{% endif %}` + cancel button (always last, inside the stack): `{% if cancel_url %}<c-button href="{{ cancel_url }}" text="Cancel" icon="x-circle" class="border-light-subtle" />{% else %}<c-button type="submit" form="logout-from-stage" text="Cancel" icon="x-circle" class="border-light-subtle" />{% endif %}` + `</c-button.stack></c-form>`
- [X] T007 [P] [US4] Write login-by-code tests in tests/test_addons/test_allauth/test_login_view.py covering:
      - request_login_code.html renders (200 OK) with `<c-entrance>` shell
      - request_login_code.html contains email form field
      - request_login_code.html shows "Other sign-in options" link back to login
      - confirm_login_code.html renders (200 OK) with `<c-entrance>` shell
      - confirm_login_code.html uses `verify_form` (code entry field present)
      - No `{% element %}` tags in rendered output for either template

**Checkpoint**: Phase 5 done when all US4 tests pass.

- [X] TVAL-3 [US4] Run `poetry run pytest tests/test_addons/test_allauth/test_login_view.py` — MUST pass

---

## Phase 6: US6 — Passkey Login (Priority: P2)

**Goal**: A "Sign in with a passkey" button renders below the email/password form when `PASSKEY_LOGIN_ENABLED` is `True`, and the WebAuthn login script is injected into the page body with the correct button ID.

**Independent Test**: Set `PASSKEY_LOGIN_ENABLED=True`, visit `/accounts/login/`, confirm (a) passkey button is present with `id="passkey_login"`, (b) WebAuthn script content appears in the rendered page, (c) both button and script are absent when `PASSKEY_LOGIN_ENABLED=False`.

- [X] T008 [P] [US6] Write passkey rendering tests in tests/test_addons/test_allauth/test_login_view.py covering:
      - Passkey button absent when `PASSKEY_LOGIN_ENABLED=False`
      - Passkey button rendered with `id="passkey_login"` when `PASSKEY_LOGIN_ENABLED=True`
      - WebAuthn script injected into page when `PASSKEY_LOGIN_ENABLED=True`
      - WebAuthn script absent when `PASSKEY_LOGIN_ENABLED=False`
      - Passkey button absent when `SOCIALACCOUNT_ONLY=True`

**Checkpoint**: Phase 6 done when all US6 tests pass.

---

## Phase 7: US5 — Already Authenticated (Priority: P3)

**Goal**: An authenticated user visiting the login URL is redirected by allauth's built-in logic. No template change is needed — only test coverage.

**Independent Test**: Authenticate a test user, issue GET to the login URL, confirm 302 redirect to `LOGIN_REDIRECT_URL`.

- [X] T009 [P] [US5] Write authenticated-user redirect test in tests/test_addons/test_allauth/test_login_view.py:
      - Authenticated user GET `/accounts/login/` → 302 redirect (not 200)
      - Response redirects toward `LOGIN_REDIRECT_URL` or configured destination

**Checkpoint**: Phase 7 done when redirect test passes.

---

## Phase 8: US7 — Social OAuth Confirmation Pages (Priority: P2)

**Goal**: The three `socialaccount` entrance templates (`socialaccount/login.html`, `socialaccount/login_cancelled.html`, `socialaccount/login_redirect.html`) are rewritten using Cotton components, replacing all `{% element %}` syntax. All three are existing placeholder overrides added in FR-016 (spec.md refined 2026-05-09).

**Independent Test**: Configure a social provider, initiate an OAuth flow that triggers the confirmation step, and confirm `socialaccount/login.html` renders with the `<c-entrance>` shell. Cancel an OAuth flow and confirm `socialaccount/login_cancelled.html` renders cleanly with a sign-in link. Visit `socialaccount/login_redirect.html` and confirm the meta-refresh redirect fires correctly.

- [X] T012 [P] [US7] Rewrite dac/addons/allauth/templates/socialaccount/login.html using Cotton components:
      - `{% extends "socialaccount/base_entrance.html" %}` + `{% load i18n %}`
      - `{% block title %}{% trans "Sign In" %}{% endblock title %}`
      - `{% block title %}` — conditional: `{% if process == "connect" %}{% blocktrans with provider.name as provider %}Connect {{ provider }}{% endblocktrans %}{% else %}{% blocktrans with provider.name as provider %}Sign In Via {{ provider }}{% endblocktrans %}{% endif %}` `{% endblock title %}`
      - `{% block content %}`: `<c-text class="mb-3">` — conditional description text (connect vs sign-in blurb using `{% blocktrans %}`) `</c-text>` → `<c-form method="post" action=".">` + `{% csrf_token %}` + `{{ redirect_field }}` + `<c-button.stack class="mt-4">` + `<c-button text="{% trans "Continue" %}" icon="login" type="submit" variant="primary" size="lg" />` + `</c-button.stack></c-form>`
- [X] T013 [P] [US7] Rewrite dac/addons/allauth/templates/socialaccount/login_cancelled.html using Cotton components:
      - `{% extends "socialaccount/base_entrance.html" %}` + `{% load i18n %}`
      - `{% block title %}{% trans "Login Cancelled" %}{% endblock title %}`
      - `{% block title %}{% trans "Login Cancelled" %}{% endblock title %}`
      - `{% block content %}`: `{% url 'account_login' as login_url %}` → `<c-text class="mb-4">{% blocktrans %}You decided to cancel logging in to our site using one of your existing accounts. If this was a mistake, please proceed to <a href="{{ login_url }}">sign in</a>.{% endblocktrans %}</c-text>` → `<c-button.stack>` + `<c-button href="{{ login_url }}" text="{% trans "Sign in" %}" icon="login" variant="primary" size="lg" />` + `</c-button.stack>`
- [X] T014 [P] [US7] Rewrite dac/addons/allauth/templates/socialaccount/login_redirect.html — minimal rewrite preserving meta-refresh:
      - Standalone HTML (does NOT extend any base template — ephemeral redirect page, no `<c-entrance>` shell per FR-016)
      - Preserve `<meta http-equiv="refresh" content="0;URL='{{ redirect_to }}'" />`
      - Replace `{% element %}` link with plain `<a href="{{ redirect_to }}">{% trans "Continue" %}</a>`
      - Remove all `{% load allauth %}` and `{% element %}` tags; keep `{% load i18n %}`
- [X] T015 [P] [US7] Write US7 tests in tests/test_addons/test_allauth/test_login_view.py covering:
      - `socialaccount/login.html` renders (200 OK); no `{% element %}` tags; contains provider name; has Continue button
      - `socialaccount/login.html` with `process="connect"` shows "Connect \{provider\}" in title
      - `socialaccount/login.html` with `process="login"` shows "Sign In Via \{provider\}" in title
      - `socialaccount/login_cancelled.html` renders (200 OK); no `{% element %}` tags; contains "Login Cancelled" and sign-in link
      - `socialaccount/login_redirect.html` renders (200 OK); contains `http-equiv="refresh"`; no `{% element %}` tags
- [X] T016 [US7] Update screenshots/test_login_screenshots.py to add 2 new permutations (socialaccount templates) and re-run:
      - Add `socialaccount-login-confirm` — render `socialaccount/login.html` with a configured Google provider (`process="login"`)
      - Add `socialaccount-login-cancelled` — render `socialaccount/login_cancelled.html`
      - (`login_redirect.html` exempt from screenshots — ephemeral redirect page, per SC-005)
      - Run full suite and visually inspect all 27 screenshot files (9 permutations × 3 viewports)

**Checkpoint**: Phase 8 done when T012–T015 pass and 27 screenshots committed.

- [X] TVAL-4 [US7] Run `poetry run pytest tests/test_addons/test_allauth/test_login_view.py` — MUST pass (original 23 tests + new US7 tests)

---

## Final Phase: Screenshot Coverage & Polish

**Goal**: All 7 settings permutations captured at 3 viewports = 21 PNG files committed to `docs/_static/`.

- [X] T010 Write screenshots/test_login_screenshots.py with parametrized pytest-playwright tests:
      - 7 permutations via `@pytest.mark.parametrize`:
          - `login-page-social-disabled` — `SOCIALACCOUNT_ENABLED=False`
          - `login-page-social-enabled` — `SOCIALACCOUNT_ENABLED=True` with ≥1 provider
          - `login-page-social-only` — `SOCIALACCOUNT_ONLY=True`
          - `login-page-login-by-code` — `ACCOUNT_LOGIN_BY_CODE_ENABLED=True`
          - `login-page-passkey-enabled` — `PASSKEY_LOGIN_ENABLED=True`
          - `login-request-code-page` — `account/request_login_code.html`
          - `login-confirm-code-page` — `account/confirm_login_code.html`
      - 3 viewports: desktop (1440×900), tablet (768×1024), mobile (390×844)
      - Create `docs/_static/desktop/`, `docs/_static/tablet/`, `docs/_static/mobile/` if not present
      - Save to `docs/_static/{viewport}/{permutation-slug}.png` (21 files total)
      - Mirror patterns from `screenshots/test_signup_screenshots.py` if it exists
- [X] T011 Run `pytest screenshots/test_login_screenshots.py -v`, visually inspect all 21 generated screenshots for layout correctness, then commit all PNG files and the test file

---

## Dependencies

```
T001 (setup)
  └─ T002 [US1] login.html (all login-page stories depend on this file existing)
      ├─ T003 [US2] email/password tests     ─┐
      ├─ T004 [US3] social tests              │ all independent of each other
      ├─ T008 [US6] passkey tests             │
      └─ T009 [US5] redirect test            ─┘
T005 [US4] request_login_code.html  ─┐ independent of T002
T006 [US4] confirm_login_code.html  ─┤ independent of each other
T007 [US4] login-by-code tests      ─┘ depends on T005 + T006

T012 [US7] socialaccount/login.html       ─┐
T013 [US7] login_cancelled.html            │ independent of each other
T014 [US7] login_redirect.html             ├─ T015 [US7] tests (depends on T012 + T013 + T014)
T012 + T013 → T016 (screenshots; login_redirect exempt)

T002 + T005 + T006 → T010 → T011 (screenshots — all templates must exist first)
```

## Parallel Execution Examples

**After T002 completes**, these run simultaneously:

```
T003 (US2 tests)  ║  T004 (US3 tests)  ║  T008 (US6 tests)  ║  T009 (US5 test)
```

**Independently of T002** (different files):

```
T005 (request_login_code.html)  ║  T006 (confirm_login_code.html)
                                  → T007 (US4 tests, after T005 + T006)
```

**Task counts by user story**:

| Story | Tasks | Files touched |
|---|---|---|
| US1 (P1) | T002 | account/login.html |
| US2 (P1) | T003 | test_login_view.py |
| US3 (P2) | T004 | test_login_view.py |
| US4 (P2) | T005, T006, T007 | request_login_code.html, confirm_login_code.html, test_login_view.py |
| US5 (P3) | T009 | test_login_view.py |
| US6 (P2) | T008 | test_login_view.py |
| US7 (P2) | T012, T013, T014, T015, T016 | socialaccount/login.html, login_cancelled.html, login_redirect.html, test_login_view.py, screenshots/ |
| Polish | T010, T011 | screenshots/test_login_screenshots.py, docs/_static/ |

**Total tasks**: 16 implementation tasks + 4 validation checkpoints (TVAL-1, TVAL-2, TVAL-3, TVAL-4)
