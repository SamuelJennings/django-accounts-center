# Tasks: Allauth Password Reset Flow

**Input**: Design documents from `specs/003-allauth-password-reset/`
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, contracts/ ✅, quickstart.md ✅
**Propagated**: 2026-05-11 — Updated from spec.md refinement (T002, T003, T004, T005, T011, TPW-1)

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies on incomplete tasks)
- **[Story]**: Which user story this task belongs to (US1–US5)
- Include exact file paths in descriptions

## Implementation Strategy

**MVP scope**: Complete Phase 3 (US1 + US2) first — this delivers all four standard password-reset pages, both the valid-token and invalid-token branches, and 15 screenshots. US3 (P2) is test-only with zero code changes. US4 (P2) adds the code-based flow and can be implemented independently.

**Key facts**:

- All four standard templates (`password_reset.html`, `password_reset_done.html`, `password_reset_from_key.html`, `password_reset_from_key_done.html`) are written once as complete files — each template is a single task
- `password_reset_from_key.html` covers both US1 (valid-token form) and US2 (invalid-token branch) in one template file — written in Phase 3, tested across both phases
- `base_confirm_code.html` is a full rewrite (not a block-only update); `confirm_password_reset_code.html` is block-values only
- No new Python code, models, migrations, or Cotton components are introduced
- All shared infrastructure (`<c-entrance>`, template chain, `<c-form>`, `<c-button>`) is in place from specs 001 and 002

---

## Phase 1: Setup

**Purpose**: Create the integration test module skeleton.

- [X] T001 Create `tests/test_addons/test_allauth/test_password_reset_view.py` with empty test class structure and required imports (`pytest`, `@pytest.mark.django_db`, allauth URL names, `Client`, `override_settings`)

---

## Phase 2: Foundational (N/A)

All shared infrastructure from specs 001 and 002 is in place. No foundational tasks needed — user story implementation begins immediately in Phase 3.

---

## Phase 3: US1 + US2 — Standard Link Reset & Invalid Token (Priority: P1) 🎯 MVP

**Goal**: All four standard password-reset pages render within the `<c-entrance>` shell using Cotton components. End users can complete the full link-based reset flow and receive a clear recovery message when their token is expired or invalid.

**Independent Test**: Navigate to `/accounts/password/reset/`, submit a registered email, follow the emailed link to `/accounts/password/reset/key/<uid>-<key>/`, set a new password, and verify `/accounts/password/reset/key/done/` displays the success message. Separately, navigate directly to a reset URL with an invalid key and confirm the invalid-token error branch renders with a link back to the reset form.

- [X] T002 [US1] Write `dac/addons/allauth/templates/account/password_reset.html` — full Cotton rewrite of the existing `{% element %}`-based placeholder. Template must:
      - `{% extends "account/base_entrance.html" %}` + `{% load i18n account %}`
      - `{% block title %}{% trans "Password Reset" %}{% endblock title %}`
      - `{% block title %}{% trans "Password Reset" %}{% endblock title %}`
      - `{% block content %}` — ordered sections per contracts/template-context.md:
          1. `{% if user.is_authenticated %}{% include "account/snippets/already_logged_in.html" %}{% endif %}`
          2. Description via `<c-text center>{% trans "Forgotten your password? Enter your email…" %}</c-text>`
          3. `{% url 'account_reset_password' as reset_url %}` → `<c-form method="post" action="{{ reset_url }}">{% csrf_token %}<c-form.render form=form />{{ redirect_field }}<c-button.stack><c-button text="Send email" icon="send" size="lg" type="submit" variant="primary" /></c-button.stack></c-form>`
          4. Contact-us via `<c-text text="..." small />`
      - Zero `{% element %}` tags

- [X] T003 [P] [US1] Write `dac/addons/allauth/templates/account/password_reset_done.html` — full Cotton rewrite. Template must:
      - `{% extends "account/base_entrance.html" %}` + `{% load i18n %}`
      - `{% block title %}{% trans "Password Reset" %}{% endblock title %}` (no `head_title` block)
      - `{% block content %}`:
          1. `{% if user.is_authenticated %}{% include "account/snippets/already_logged_in.html" %}{% endif %}`
          2. Confirmation via `<c-text center>{% blocktrans %}We have sent you an email. If you have not received it please check your spam folder. Otherwise contact us if you do not receive it in a few minutes.{% endblocktrans %}</c-text>`
      - No form, no button — informational only
      - Zero `{% element %}` tags

- [X] T004 [US1] [US2] Write `dac/addons/allauth/templates/account/password_reset_from_key.html` — full Cotton rewrite covering both branches per contracts/template-context.md (US1: valid-token; US2: invalid-token). Template must:
      - `{% extends "account/base_entrance.html" %}` + `{% load i18n account %}`
      - `{% block title %}{% trans "Change Password" %}{% endblock title %}`
      - `{% block title %}` — conditional: `{% if token_fail %}{% trans "Bad Token" %}{% else %}{% trans "Change Password" %}{% endif %}` `{% endblock title %}`
      - `{% block content %}` — two branches:
          - **Invalid branch** (`{% if token_fail %}`): `<c-text>{% blocktrans with passwd_reset_url=... %}The password reset link was invalid, possibly because it has already been used. Please request a <a href="{{ passwd_reset_url }}">new password reset</a>.{% endblocktrans %}</c-text>`
          - **Valid branch** (`{% else %}`): `<c-form method="post" action="{{ action_url }}">{% csrf_token %}<c-form.render form=form />{{ redirect_field }}<c-button.stack><c-button text="Confirm" icon="submit" size="lg" type="submit" variant="primary" />{% if cancel_url %}<c-button text="Cancel" href="{{ cancel_url }}" icon="x-circle" size="lg" class="border-secondary-subtle" />{% else %}<c-button text="Cancel" icon="x-circle" type="submit" form="logout-from-stage" size="lg" class="border-secondary-subtle" />{% endif %}</c-button.stack></c-form>`
          - Hidden logout form (when no `cancel_url`): `{% if not cancel_url %}<form id="logout-from-stage" method="post" action="{% url 'account_logout' %}">{% csrf_token %}<input type="hidden" name="next" value="{% url 'account_login' %}" /></form>{% endif %}`
      - Zero `{% element %}` tags

- [X] T005 [P] [US1] Write `dac/addons/allauth/templates/account/password_reset_from_key_done.html` — full Cotton rewrite. Template must:
      - `{% extends "account/base_entrance.html" %}` + `{% load i18n %}`
      - `{% block title %}{% trans "Change Password" %}{% endblock title %}` (no `head_title` block)
      - `{% block content %}`: `<c-text center>{% trans 'Your password is now changed.' %}</c-text>`
      - No button, no link, no further action — informational only
      - Zero `{% element %}` tags

- [X] T006 [P] [US1] [US5] Write US1 integration tests in `tests/test_addons/test_allauth/test_password_reset_view.py` covering:
      - `password_reset.html` renders HTTP 200 for anonymous user
      - `password_reset.html` renders HTTP 200 for authenticated user (includes `already_logged_in` snippet)
      - `password_reset.html` contains email form field; no `{% element %}` in rendered HTML
      - `password_reset.html` contains `redirect_field` hidden input inside form
      - `password_reset.html` contains contact-us paragraph text
      - POST to password reset form → redirects to `account_reset_password_done`
      - `password_reset_done.html` renders HTTP 200; no `{% element %}` in output
      - `password_reset_done.html` renders HTTP 200 for authenticated user (includes `already_logged_in` snippet)
      - `password_reset_from_key.html` (valid token) renders HTTP 200; contains password fields; no `{% element %}`
      - `password_reset_from_key.html` (valid token) contains `redirect_field` inside form
      - `password_reset_from_key.html` (valid token) contains Cancel button targeting `#logout-from-stage`
      - `password_reset_from_key.html` (valid token) contains hidden `<form id="logout-from-stage">` POSTing to logout URL
      - `password_reset_from_key_done.html` renders HTTP 200; contains "Your password is now changed."; no `{% element %}`
      - Full end-to-end: request → done → change password → success (no rendering exception at any step)

- [X] T007 [P] [US2] Write US2 integration tests in `tests/test_addons/test_allauth/test_password_reset_view.py` covering:
      - `password_reset_from_key.html` with `token_fail=True` renders the invalid-token branch (not the form)
      - Invalid-token branch contains a link back to `account_reset_password`
      - Invalid-token branch does NOT contain a password input field
      - Invalid-token branch title is "Bad Token"
      - Valid-token branch title is "Change Password"

- [X] T008 [US1] [US5] Write `screenshots/test_password_reset_screenshots.py` with parametrized pytest-playwright tests:
      - 5 page-state permutations:
          - `password-reset` — renders `account/password_reset.html` (anonymous user)
          - `password-reset-done` — renders `account/password_reset_done.html`
          - `password-reset-from-key` — renders `account/password_reset_from_key.html` with valid token (form visible)
          - `password-reset-from-key-invalid` — renders `account/password_reset_from_key.html` with `token_fail=True`
          - `password-reset-from-key-done` — renders `account/password_reset_from_key_done.html`
      - 3 viewport sizes: desktop (1440×900), tablet (768×1024), mobile (390×844)
      - Save screenshots to `docs/_static/{desktop,tablet,mobile}/<page-state>.png`
      - Run with `poetry run pytest screenshots/test_password_reset_screenshots.py`
      - Commit both test file and all 15 generated PNG files

- [ ] TPW-1 [US1] [US2] Playwright MCP browser verification — all five password-reset page states (Principle VI):
      - Start dev server: `poetry run python manage.py runserver`
      - Open Playwright MCP browser → navigate to `/accounts/password/reset/` → confirm `<c-entrance>` shell renders, email form and contact-us paragraph visible
      - Navigate to `/accounts/password/reset/done/` → confirm informational text renders, no form present
      - Navigate to a valid reset-key URL → confirm password fields, "Confirm" submit button (with send icon) and Cancel button visible inside `<c-entrance>`
      - Navigate to an invalid reset-key URL → confirm error-branch paragraph with inline "new password reset" link; NO password form
      - Navigate to `/accounts/password/reset/key/done/` → confirm "Your password is now changed." paragraph, no button or link
      - Trigger Cancel button on the valid-key page → confirm redirect to login and session terminated
      - **MUST NOT be marked done until agent has visually inspected each page state in the Playwright MCP browser**

**Checkpoint**: Phase 3 done when all T006 + T007 tests pass, TPW-1 verified, and 15 screenshots committed.

- [X] TVAL-1 [US1] Run system check then pytest:
      ```
  poetry run python manage.py check --settings=tests.settings
      poetry run pytest tests/test_addons/test_allauth/test_password_reset_view.py --no-cov
      ```
      — Both MUST pass; zero errors from system check
- [X] TVAL-2 [US1] Run `poetry run pytest screenshots/test_password_reset_screenshots.py --no-cov` — MUST produce 15 PNG files

---

## Phase 4: US3 — Email Enumeration Protection (Priority: P2)

**Goal**: Submitting the password-reset form with an unregistered email address produces the same `password_reset_done.html` response as a valid address — no error, no difference in wording.

**Independent Test**: POST to the password-reset form with a non-existent email address and assert the response redirects to `account_reset_password_done` with HTTP 200 and no inline error message.

- [X] T009 [P] [US3] Write US3 test in `tests/test_addons/test_allauth/test_password_reset_view.py`:
      - POST password-reset form with unrecognised email → response redirects to `account_reset_password_done`
      - `password_reset_done.html` page contains no error message or "not registered" wording
      - Response wording is identical to a valid-email submission (SC-001 compliance)

**Checkpoint**: Phase 4 done when T009 test passes.

- [X] TVAL-3 [US3] Run system check then targeted pytest:
      ```
  poetry run python manage.py check --settings=tests.settings
      poetry run pytest tests/test_addons/test_allauth/test_password_reset_view.py -k "enumeration or unknown_email" --no-cov
      ```
      — Both MUST pass; zero errors from system check

---

## Phase 5: US4 — Code-Based Password Reset (Priority: P2)

**Goal**: When `ACCOUNT_EMAIL_VERIFICATION_BY_CODE_ENABLED = True`, the code-entry page `account/confirm_password_reset_code.html` renders within a consistent `<c-entrance>` shell, inheriting all structure from the fully-rewritten `account/base_confirm_code.html` Cotton base. The base template faithfully replicates the allauth original's full branching structure.

**Independent Test**: With `ACCOUNT_EMAIL_VERIFICATION_BY_CODE_ENABLED = True`, complete a password-reset flow and assert `confirm_password_reset_code.html` renders correctly with a code-entry field, Confirm button, and consistent visual structure matching the login-code and email-verification-code pages.

- [X] T010 [US4] Rewrite `dac/addons/allauth/templates/account/base_confirm_code.html` — full Cotton replacement of all `{% element %}` syntax per contracts/component-interface.md. Template must:
      - `{% extends "account/base_entrance.html" %}` + `{% load i18n account %}`
      - `{% block title %}{% block head_title_ %}{% endblock head_title_ %}{% endblock title %}`
      - `{% block title %}{% block title_ %}{% endblock title_ %}{% endblock title %}`
      - `{% block content %}` — complete structure:
          1. Recipient paragraph: `<p>{% blocktrans with recipient=... %}We've sent a code to {{ recipient }}.…{% endblocktrans %}</p>` (uses `{% block recipient %}`)
          2. Primary confirm form: `<c-form method="post" action="{% block action_url %}{% endblock action_url %}">{% csrf_token %}<c-form.render form=verify_form unlabeled=True />{{ redirect_field }}<c-button.stack><c-button type="submit" {% block submit_button_tags %}tags="{% block extra_tags %}{% endblock extra_tags %}"{% endblock submit_button_tags %}>{% trans "Confirm" %}</c-button>{% if can_resend %}<c-button type="submit" form="resend">{% trans "Request new code" %}</c-button>{% endif %}{% if cancel_url %}<c-button href="{{ cancel_url }}">{% trans "Cancel" %}</c-button>{% else %}<c-button type="submit" form="logout-from-stage">{% trans "Cancel" %}</c-button>{% endif %}</c-button.stack></c-form>`
          3. Hidden resend form (always): `<form id="resend" method="post" action="{% block action_url_resend %}{% endblock action_url_resend %}">{% csrf_token %}<input type="hidden" name="action" value="resend" />{{ redirect_field }}</form>`
          4. Hidden logout-from-stage form (when `cancel_url` absent): `{% if not cancel_url %}<form id="logout-from-stage" method="post" action="{% url 'account_logout' %}">{% csrf_token %}<input type="hidden" name="next" value="{% url 'account_login' %}" /></form>{% endif %}`
          5. Collapsible change section (when `can_change`): `{% if can_change %}<details class="mt-3"><summary>{% block change_title %}{% trans "Change" %}{% endblock change_title %}</summary><c-form method="post" action="{% block action_url_change %}{% endblock action_url_change %}">{% csrf_token %}<c-form.render form=change_form />{{ redirect_field }}<c-button name="action" value="change" type="submit">{% trans "Change" %}</c-button></c-form></details>{% endif %}`
      - Zero `{% element %}` tags

- [X] T011 [US4] Update `dac/addons/allauth/templates/account/confirm_password_reset_code.html` — block-values only (no structural changes). Must set per contracts/template-context.md:
      - `{% block title_ %}{% trans "Enter Password Reset Code" %}{% endblock title_ %}` (only `title_` overridden — no `head_title_` block)
      - `{% block recipient %}<a href="mailto:{{ email }}">{{ email }}</a>{% endblock recipient %}`
      - `{% block action_url %}{% url 'account_confirm_password_reset_code' as confirm_code_url %}{{ confirm_code_url }}{% endblock action_url %}` (fail-silent pattern)
      - `{% block action_url_resend %}{% url 'account_confirm_password_reset_code' as confirm_code_url_resend %}{{ confirm_code_url_resend }}{% endblock action_url_resend %}` (fail-silent pattern)
      - `{% block extra_tags %}email,verification{% endblock extra_tags %}`
      - Zero `{% element %}` tags

- [X] T012 [P] [US4] Write US4 tests in `tests/test_addons/test_allauth/test_password_reset_view.py` covering (use `@override_settings(ACCOUNT_EMAIL_VERIFICATION_BY_CODE_ENABLED=True)`):
      - `confirm_password_reset_code.html` renders HTTP 200; page title is "Enter Password Reset Code"
      - Page contains code-entry field from `verify_form`; no `{% element %}` tags in rendered HTML
      - "Confirm" submit button is present
      - `redirect_field` hidden input is present inside the form
      - "Request new code" button visible when `can_resend=True`; absent when `can_resend=False`
      - Cancel button renders as link when `cancel_url` is set; renders as submit targeting `#logout-from-stage` when absent
      - `<form id="resend">` is always present in the HTML
      - `<form id="logout-from-stage">` present when `cancel_url` is absent; absent when `cancel_url` is set
      - `can_change=True` → collapsible `<details>` section is present; `can_change=False` → absent

- [ ] TPW-2 [US4] Playwright MCP browser verification — code-based password reset page (Principle VI):
      - With `ACCOUNT_EMAIL_VERIFICATION_BY_CODE_ENABLED=True`, start dev server: `poetry run python manage.py runserver`
      - Open Playwright MCP browser → navigate to the confirm-password-reset-code URL
      - Confirm: `<c-entrance>` shell renders; recipient email text present; code-entry field visible; Confirm and Cancel buttons present
      - Verify "Request new code" button visible when `can_resend=True`; confirm it submits the `#resend` form
      - Verify `can_change=True` renders collapsible `<details>` change-address section below the confirm form
      - **MUST NOT be marked done until agent has visually inspected each state in the Playwright MCP browser**

**Checkpoint**: Phase 5 done when all T012 tests pass and TPW-2 verified.

- [X] TVAL-4 [US4] Run system check then full pytest suite:
      ```
  poetry run python manage.py check --settings=tests.settings
      poetry run pytest tests/test_addons/test_allauth/test_password_reset_view.py --no-cov
      ```
      — Both MUST pass (all US1–US4 tests); zero errors from system check

---

## Final Phase: Polish & Cross-Cutting Concerns

**Goal**: All six template files contain zero `{% element %}` tags; templates pass djlint; full test suite is green.

- [X] T013 [US5] Verify zero `{% element %}` instances across all six files:
      ```
  Select-String -Path "dac/addons/allauth/templates/account/password_reset*.html","dac/addons/allauth/templates/account/base_confirm_code.html","dac/addons/allauth/templates/account/confirm_password_reset_code.html" -Pattern "{%\s*element" | Select-Object Filename, LineNumber, Line
      ```
      — MUST return zero results

- [X] T014 [P] Run djlint on all six modified templates:
      ```
  poetry run djlint dac/addons/allauth/templates/account/password_reset.html dac/addons/allauth/templates/account/password_reset_done.html dac/addons/allauth/templates/account/password_reset_from_key.html dac/addons/allauth/templates/account/password_reset_from_key_done.html dac/addons/allauth/templates/account/base_confirm_code.html dac/addons/allauth/templates/account/confirm_password_reset_code.html --check
      ```
      — MUST produce no errors

- [X] T015 [P] Run full test suite to confirm no regressions:
      ```
  poetry run pytest tests/ --no-cov -q
      ```
      — MUST pass (green)

---

## Dependencies

```
T001 → T002 ┐
     → T003 ├→ T006 → TVAL-1
     → T004 ├→ T007 ↗
     → T005 ┘
     → T002–T005 → TPW-1 → TVAL-1
     → T008 → TVAL-2

T009 → TVAL-3  (independent of T002–T008, shares test file from T001)

T010 → T011
     → TPW-2 → TVAL-4
     → T012 → TVAL-4

T013, T014, T015  (parallel, after all template tasks complete)
```

## Parallel Execution Examples

**After T001 (test file created)**:

- T002 (password_reset.html) + T003 (password_reset_done.html) + T005 (password_reset_from_key_done.html) can run in parallel
- T004 (password_reset_from_key.html) is independent of T003 and T005

**After T002–T005 (all four standard templates written)**:

- T006 (US1 tests) + T007 (US2 tests) + T008 (screenshots) can run in parallel
- T009 (US3 test) can run in parallel with T006–T008

**After T001 (Phase 5)**:

- T010 (base_confirm_code.html) → T011 (child template) → T012 (tests)

**Final phase**:

- T013 + T014 + T015 all parallel

## Total Task Count

| Phase | Tasks | User Story |
|---|---|---|
| Phase 1: Setup | 1 | — |
| Phase 3: US1+US2 MVP | 10 (T002–T008 + TPW-1 + TVAL-1–2) | US1, US2 |
| Phase 4: US3 | 2 (T009 + TVAL-3) | US3 |
| Phase 5: US4 | 5 (T010–T012 + TPW-2 + TVAL-4) | US4 |
| Final: Polish | 3 (T013–T015) | — |
| **Total** | **21** | |

**Suggested MVP**: Complete Phase 3 only (T001–T008 + TVAL-1–2) — delivers all four standard pages, both token branches, full integration test coverage, and 15 screenshots.
