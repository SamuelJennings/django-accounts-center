# Tasks: Allauth Email Verification Flow

**Input**: Design documents from `specs/004-allauth-email-verification/`
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, contracts/ ✅, quickstart.md ✅

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies on incomplete tasks)
- **[Story]**: Which user story this task belongs to (US1–US5)
- Include exact file paths in descriptions

## Implementation Strategy

**MVP scope**: Complete Phase 3 (US1 + US2) first — this delivers the two highest-traffic
email-verification pages (`verification_sent.html` and both branches of `email_confirm.html`)
plus integration tests. US3 and US4 are P2 stories that can follow independently.

**Key facts**:

- All four templates already exist in `dac/addons/allauth/templates/account/` but use `{% element %}` syntax — each is a full rewrite (or block-fix for `confirm_email_verification_code.html`)
- `email_confirm.html` covers both US1 (valid-key branch) and US2 (invalid-key branch) in a single file — both branches written together in T003
- `confirm_email_verification_code.html` is a block-override-only template that extends `base_confirm_code.html` — no new structure needed, just block-name and URL fixes
- No new Python code, models, migrations, URL patterns, or Cotton components are introduced
- All shared infrastructure (`<c-entrance>`, `<c-text>`, `<c-form>`, `<c-button>`, `<c-button.stack>`, `base_entrance.html`) is in place from specs 001, 002, and 003
- Integration tests for the confirm button MUST assert non-empty button text and a rendered icon element — MUST NOT assert the specific label string `"Confirm"` or icon name `"check-circle"`

---

## Phase 1: Setup

**Purpose**: Create the integration test module skeleton.

- [X] T001 Create `tests/test_addons/test_allauth/test_email_verification_view.py` with empty test class structure and required imports (`pytest`, `@pytest.mark.django_db`, allauth URL names, `Client`, `override_settings`)

---

## Phase 2: Foundational (N/A)

All shared infrastructure from specs 001, 002, and 003 is in place. No foundational tasks
needed — user story implementation begins immediately in Phase 3.

---

## Phase 3: US1 + US2 — Standard Verification & Invalid Link (Priority: P1) 🎯 MVP

**Goal**: The two highest-traffic email-verification pages render within the `<c-entrance>` shell using Cotton components. A user can be redirected to the verification-sent page after signup, follow a valid confirmation link to confirm their address, and receive a clear error message when a link has expired or been already used.

**Independent Test**: Navigate to `account_email_verification_sent` and assert the informational page renders with no form. Craft a valid confirmation key URL, follow it, and assert the confirm form renders. Then test an invalid key and assert the error branch appears with no form and with a link back to email management.

- [X] T002 [P] [US1] Rewrite `dac/addons/allauth/templates/account/verification_sent.html` — full Cotton rewrite of the existing `{% element %}`-based template. Template must:
      - `{% extends "account/base_entrance.html" %}` + `{% load i18n %}`
      - `{% block title %}{% trans "Verify Your Email Address" %}{% endblock title %}` (no `head_title` block — `base_entrance.html` derives it from `title`)
      - `{% block content %}`:
          1. `<c-text center>{% blocktrans %}We have sent an email to you for verification. Follow the link provided to finalize the signup process. If you do not see the verification email in your main inbox, check your spam folder. Please contact us if you do not receive the verification email within a few minutes.{% endblocktrans %}</c-text>`
      - Remove `{% load allauth %}` — no longer needed without `{% element %}` tags
      - Zero `{% element %}` tags

- [X] T003 [P] [US1] [US2] Rewrite `dac/addons/allauth/templates/account/email_confirm.html` — full Cotton rewrite covering all three conditional branches. Template must:
      - `{% extends "account/base_entrance.html" %}` + `{% load i18n account %}`
      - `{% block title %}{% trans "Confirm Email Address" %}{% endblock title %}`
      - `{% block content %}` wrapping the outer `{% with email=confirmation.email_address.email %}…{% endwith %}` (so `{{ email }}` is available in Branch B):
          - **Branch A** (`{% if confirmation %}{% if can_confirm %}`): valid-key branch —
              1. `{% user_display confirmation.email_address.user as user_display %}`
              2. `{% url 'account_confirm_email' confirmation.key as action_url %}`
              3. `<c-text>{% blocktrans with confirmation.email_address.email as email %}Please confirm that <a href="mailto:{{ email }}">{{ email }}</a> is an email address for user {{ user_display }}.{% endblocktrans %}</c-text>`
              4. `<c-form method="post" action="{{ action_url }}">{% csrf_token %}{{ redirect_field }}<c-button.stack><c-button type="submit" icon="check-circle" size="lg" variant="primary">{% trans "Confirm" %}</c-button></c-button.stack></c-form>`
          - **Branch B** (`{% else %}` — confirmation exists but `can_confirm` is False):
              1. `<c-text>{% blocktrans %}Unable to confirm {{ email }} because it is already confirmed by a different account.{% endblocktrans %}</c-text>`
          - **Branch C** (`{% else %}` — no `confirmation` object):
              1. `{% url 'account_email' as email_url %}`
              2. `<c-text>{% blocktrans %}This email confirmation link expired or is invalid. Please <a href="{{ email_url }}">issue a new email confirmation request</a>.{% endblocktrans %}</c-text>`
      - Remove `{% load allauth %}` — no longer needed without `{% element %}` tags
      - Zero `{% element %}` tags
      - Replicate the allauth original exactly: every element, paragraph, and conditional present in the source must appear in the Cotton version with no additions or omissions beyond the syntax change (FR-003)

- [X] T004 [P] [US1] [US5] Write US1 integration tests in `tests/test_addons/test_allauth/test_email_verification_view.py` covering:
      - `account_email_verification_sent` renders HTTP 200 for anonymous user
      - `verification_sent.html` rendered output contains no `{% element %}` raw tags
      - `verification_sent.html` rendered output contains non-empty descriptive paragraph text inside the entrance shell
      - `verification_sent.html` rendered output contains no `<form>` element

- [X] T005 [P] [US1] [US2] [US5] Write US1 + US2 integration tests in `tests/test_addons/test_allauth/test_email_verification_view.py` covering:
      - `email_confirm.html` with a valid key (`can_confirm=True`) renders HTTP 200
      - Valid-key branch contains a `<form>` element
      - Valid-key branch contains a submit button with **non-empty** button text (MUST NOT assert specific label string; MUST NOT assert `"Confirm"` explicitly)
      - Valid-key branch contains a rendered icon element (e.g. `<svg>` or `<i>` element; MUST NOT assert the specific icon name `"check-circle"`)
      - Valid-key branch contains a `{{ redirect_field }}` hidden input inside the form
      - `email_confirm.html` with an invalid/expired key renders HTTP 200
      - Invalid-key branch does NOT contain a `<form>` element
      - Invalid-key branch contains a link pointing to the `account_email` URL
      - Both branches contain no `{% element %}` raw tags in rendered output

- [X] TVAL-A [US1] [US2] Phase 3 quality gate:
      - Run `poetry run python manage.py check` — MUST pass with no errors
      - Run `poetry run pytest tests/test_addons/test_allauth/test_email_verification_view.py --no-cov -q` — all Phase 3 tests MUST pass

**Checkpoint**: At this point US1 and US2 are fully functional. `verification_sent.html` and both branches of `email_confirm.html` have Cotton templates and integration tests.

---

## Phase 4: US4 — Account Inactive Error Page (Priority: P2)

**Goal**: The account-inactive page renders within the `<c-entrance>` shell rather than extending `allauth/layouts/entrance.html` directly, displaying a clear explanatory message.

**Independent Test**: Boot the example app and assert `account_inactive` URL returns HTTP 200 with a response body that contains the `<c-entrance>` wrapper and no `{% element %}` tags.

- [X] T006 [P] [US4] Rewrite `dac/addons/allauth/templates/account/account_inactive.html` — full Cotton rewrite. Template must:
      - Change `{% extends "allauth/layouts/entrance.html" %}` to `{% extends "account/base_entrance.html" %}`
      - `{% load i18n %}` (no `{% load allauth %}` — no longer needed)
      - `{% block title %}{% trans "Account Inactive" %}{% endblock title %}` (no `head_title` block)
      - `{% block content %}`:
          1. `<c-text center>{% trans "This account is inactive." %}</c-text>`
      - Zero `{% element %}` tags

- [X] T007 [P] [US4] [US5] Write US4 integration test in `tests/test_addons/test_allauth/test_email_verification_view.py` covering:
      - `account_inactive` URL renders HTTP 200
      - Rendered output contains a non-empty explanatory message
      - Rendered output contains no `{% element %}` raw tags
      - Rendered output does NOT contain a `<form>` element

- [X] TVAL-B [US4] Phase 4 quality gate:
      - Run `poetry run python manage.py check` — MUST pass with no errors
      - Run `poetry run pytest tests/test_addons/test_allauth/test_email_verification_view.py --no-cov -q` — all Phase 4 tests MUST pass

**Checkpoint**: US4 complete. Account-inactive page now uses the Cotton entrance shell consistently.

---

## Phase 5: US3 — Code-Based Email Verification (Priority: P2)

**Goal**: `confirm_email_verification_code.html` correctly extends `base_confirm_code.html` using the `title_` block (not `title`), provides `action_url_resend`, and uses fail-silent URL patterns so the template is safe in contexts where the URL is not registered.

**Independent Test**: With `ACCOUNT_EMAIL_VERIFICATION_BY_CODE_ENABLED = True`, navigate to the code-confirmation URL and assert HTTP 200 with a code-entry form rendered.

- [X] T008 [P] [US3] Rewrite `dac/addons/allauth/templates/account/confirm_email_verification_code.html` — use `<c-allauth.confirm-code>` component. Template must:
      - `{% extends "account/base_entrance.html" %}` + `{% load i18n %}`
      - `{% block title %}{% trans "Enter verification code" %}{% endblock title %}`
      - `{% block content %}` containing `<c-allauth.confirm-code>` with:
          - `recipient="{{ email }}"`
          - `action="{% url 'account_email_verification_sent' as u %}{{ u }}"`  (fail-silent)
          - `resend-url="{% url 'account_email_verification_sent' as u %}{{ u }}"`  (fail-silent)
          - `change-title="{% trans "Use a different email address" %}"`
          - `resend-supported` — MUST be declared (email verification supports resend)
      - Zero `{% element %}` tags
      - Note: `base_confirm_code.html` no longer exists; `<c-allauth.confirm-code>` is the replacement

- [X] T009 [P] [US3] [US5] Write US3 integration test in `tests/test_addons/test_allauth/test_email_verification_view.py` covering (using `@pytest.mark.override_settings(ACCOUNT_EMAIL_VERIFICATION_BY_CODE_ENABLED=True)` or `override_settings`):
      - `confirm_email_verification_code.html` renders HTTP 200 when the code-based flow is enabled
      - Rendered output contains a code-entry `<input>` field
      - Rendered output contains no `{% element %}` raw tags
      - Template renders without exception even when `ACCOUNT_EMAIL_VERIFICATION_BY_CODE_ENABLED = False` (fail-silent URL blocks)
      - POSTing an invalid code (with `ACCOUNT_EMAIL_VERIFICATION_BY_CODE_ENABLED = True`) returns a response containing a non-empty inline error message (US3 acceptance scenario 3)

- [X] TVAL-C [US3] Phase 5 quality gate:
      - Run `poetry run python manage.py check` — MUST pass with no errors
      - Run `poetry run pytest tests/test_addons/test_allauth/test_email_verification_view.py --no-cov -q` — all Phase 5 tests MUST pass

**Checkpoint**: All four templates are now Cotton-based. US3 complete.

---

## Phase 6: US5 — Screenshot Tests (Priority: P1)

**Goal**: 5 distinct page states captured at desktop (1440×900), tablet (768×1024), and mobile (390×844) viewports, producing 15 PNGs committed to `docs/_static/`.

**Page states to cover**:

| Slug | Template | State |
|---|---|---|
| `email-verification-sent` | `verification_sent.html` | anonymous user |
| `email-confirm-valid` | `email_confirm.html` | `can_confirm=True` (valid key) |
| `email-confirm-invalid` | `email_confirm.html` | no valid confirmation (invalid/expired key) |
| `email-verification-code` | `confirm_email_verification_code.html` | code-entry form |
| `account-inactive` | `account_inactive.html` | deactivated-account redirect |

- [X] T010 [US5] Write `screenshots/test_email_verification_screenshots.py` with parametrized pytest-playwright tests:
      - 5 page-state permutations (see table above)
      - 3 viewport sizes: desktop (1440×900), tablet (768×1024), mobile (390×844)
      - Follow the exact patterns established in `screenshots/test_password_reset_screenshots.py` (Spec 003)
      - Save screenshots to `docs/_static/{desktop,tablet,mobile}/<slug>.png`

- [X] T011 [US5] Run `poetry run pytest screenshots/test_email_verification_screenshots.py` — MUST pass; commit all 15 generated PNG files from `docs/_static/{desktop,tablet,mobile}/email-*.png` and `docs/_static/{desktop,tablet,mobile}/account-inactive.png`

- [ ] TPW-1 [US5] Playwright MCP browser verification — all five email-verification page states (Principle VI):
      - Start dev server: `poetry run python manage.py runserver`
      - Open each page state at desktop viewport (1440×900) and visually confirm the `<c-entrance>` shell, correct heading, and correct content per `contracts/component-interface.md`
      - Confirm `email_confirm.html` valid-key branch renders the confirm form with button and icon
      - Confirm `email_confirm.html` invalid-key branch renders an explanatory message and a link to email management — NO form, NO submit button
      - Confirm `account_inactive.html` uses the entrance shell (not a raw HTML page)
      - Confirm `confirm_email_verification_code.html` renders a code-entry field (requires `ACCOUNT_EMAIL_VERIFICATION_BY_CODE_ENABLED = True` in example settings)

---

## Phase 7: Polish & Cross-Cutting Validation

- [X] TVAL-1 Run `poetry run pytest tests/test_addons/test_allauth/test_email_verification_view.py --no-cov -q` — MUST pass with all tests green
- [X] TVAL-2 Run `poetry run pytest tests/ --no-cov -q` — full suite MUST pass; zero regressions from previous specs
- [X] TVAL-3 [P] Inspect all 15 screenshots in `docs/_static/{desktop,tablet,mobile}/` — verify layout, typography, and spacing are consistent with the signup and login pages from Specs 001 and 002

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies — start immediately
- **Phase 2 (Foundational)**: N/A — no blocking prerequisites beyond Phase 1
- **Phase 3 (US1+US2)**: Depends on Phase 1. No dependency on US3 or US4 — can start immediately
- **Phase 4 (US4)**: Depends on Phase 1. Independent of Phase 3 — can run in parallel if staffed
- **Phase 5 (US3)**: Depends on Phase 1. Independent of Phases 3 and 4 — can run in parallel if staffed
- **Phase 6 (Screenshots)**: Depends on Phases 3, 4, and 5 all being complete
- **Phase 7 (Polish)**: Depends on Phase 6

### User Story Dependencies

```
T001 (Setup)
├── T002 [P] [US1]         verification_sent.html
├── T003 [P] [US1+US2]     email_confirm.html
├── T004 [P] [US1+US5]     US1 integration tests
├── T005 [P] [US2+US5]     US2 integration tests
├── T006 [P] [US4]         account_inactive.html
├── T007 [P] [US4+US5]     US4 integration test
├── T008 [P] [US3]         confirm_email_verification_code.html
└── T009 [P] [US3+US5]     US3 integration test
    └── (all above complete)
        └── T010 → T011 → TPW-1 → TVAL-1 → TVAL-2 → TVAL-3
```

### Parallel Execution Examples

```bash
# Single developer — recommended sequential order:
T001 → T002 → T004 → T003 → T005 → T006 → T007 → T008 → T009 → T010 → T011 → TPW-1 → TVAL-1 → TVAL-2 → TVAL-3

# Two developers:
# Dev 1: T001 → T002 → T004 → T003 → T005 → T010 (wait for Dev 2) → T011 → TVAL-1 → TVAL-2 → TVAL-3
# Dev 2:         T006 → T007 → T008 → T009

# Fastest path to MVP (US1 + US2 only):
T001 → T002 → T003 → T004 → T005 → TVAL-1
```

### Total Task Count

| Phase | Tasks | User Stories |
|---|---|---|
| Phase 1 (Setup) | 1 | — |
| Phase 3 (US1+US2) | 4 | US1, US2 |
| Phase 4 (US4) | 2 | US4 |
| Phase 5 (US3) | 2 | US3 |
| Phase 6 (US5 Screenshots) | 3 | US5 |
| Phase 7 (Polish) | 3 | — |
| **Total** | **15** | US1–US5 |

**Parallelizable tasks**: T002, T003, T004, T005, T006, T007, T008, T009, TVAL-3 (9 of 15)

### MVP Scope

Implement Phases 1 and 3 only (T001–T005) to deliver the core email-verification flow
(verification_sent + both email_confirm branches) with integration tests. This satisfies all
P1 acceptance criteria for US1, US2, and US5.
