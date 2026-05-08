---
description: "Task list for 001-allauth-signup-page implementation"
---

# Tasks: Allauth Signup Page

**Input**: Design documents from `/specs/001-allauth-signup-page/`
**Prerequisites**: plan.md ✅ | spec.md ✅ | research.md ✅ | data-model.md ✅ | contracts/ ✅ | quickstart.md ✅

**Tests**: Included — spec SC-002 and FR-011 require automated tests covering all allauth configuration permutations and multi-viewport screenshot coverage.  
**Propagated**: 2026-05-07 — Added Phase 8 (Multi-Viewport Screenshot Coverage) for FR-011 / Principle XIII compliance; updated dependency DAG, parallel execution table, and task counts.  
**Propagated**: 2026-05-08 — Updated T003 (entrance.html now delegates to `<c-entrance>`), T005 (signup.html is content-only; no card/logo markup; uses `<c-button.stack>`; no `{% if form.non_field_errors %}`), and T011 (provider_list uses Bootstrap Icon `<a>` tags instead of `<c-button>`). Added Phase 2b for Cotton entrance component creation.  
**Propagated**: 2026-05-08 — Added Phase 5b (User Story 6 — Passkey Signup, FR-012): T024 (signup_by_passkey.html using Cotton components), T025 [P] (integration tests), T026 (Playwright MCP verify), TVAL-6. Updated Phase 8 permutations table to 6 configurations × 3 viewports = 18 screenshot files. Updated T023, TVAL-5, task counts, and dependency DAG.  
**Propagated**: 2026-05-08 — Constitution v1.1.2 (Principle XIII PATCH): T023 path updated from `tests/test_addons/test_allauth/test_signup_screenshots.py` to `screenshots/test_signup_screenshots.py`. TVAL-5 run command updated to `pytest screenshots/`.

---

## Phase 1: Setup

**Purpose**: Create the test directory structure before any implementation begins.

- [X] T001 Create `tests/test_addons/__init__.py` and `tests/test_addons/test_allauth/__init__.py` (empty init files mirroring source tree)

---

## Phase 2: Foundational — Layout Base Templates

**Purpose**: Wire django-mvp's HTML shell into allauth's template hierarchy. All 7 downstream templates depend on these two files. No user story template work can begin until this phase is complete.

**⚠️ CRITICAL**: `account/signup.html` and every other allauth template inherits from these two files.

- [X] T002 Write `dac/addons/allauth/templates/allauth/layouts/base.html` — extend `mvp/base.html`, map `{% block title %}{% block head_title %}{% endblock %}{% endblock %}`
- [X] T003 Write `dac/addons/allauth/templates/allauth/layouts/entrance.html` — extend `allauth/layouts/base.html`, override `{% block app %}` with `<body>`, `<c-messages dismissible animate />`, and `<c-entrance cols="12" md="8" lg="5">` with a `<c-slot name="title">{% block title %}{% endblock %}</c-slot>` and `{% block content %}{% endblock %}`
- [X] T003b Create Cotton entrance components in `dac/templates/cotton/entrance/`: `index.html` (`<c-entrance>` — full-viewport layout, responsive col, card, logo, title, slot), `background.html` (`<c-entrance.background>` — `bg-primary-subtle bg-gradient` wrapper, override to change background), `logo.html` (`<c-entrance.logo>` — DAC SVG logo; no `src` prop, override template to change logo)
- [X] T004 Run `python manage.py check` in `example/` settings — must pass with no errors after layout templates are in place

**Checkpoint**: Layout base ready — all user story template work can now proceed.

---

## Phase 3: User Story 1 — Developer Enables the Allauth Addon (Priority: P1) 🎯 MVP

**Goal**: Adding `"dac"` and `"dac.addons.allauth"` to `INSTALLED_APPS` immediately renders a fully styled, allauth-settings-reactive signup page with zero additional configuration.

**Independent Test**: Install django-accounts-center into a fresh Django project with allauth configured for email-only signup. Visit `/account-center/signup/`. The page must render with mvp CSS applied, only email + password fields visible, and a "Already have an account? Sign in" link in the card header.

- [X] T005 [US1] Write `dac/addons/allauth/templates/account/signup.html` — content-only block (no card/logo markup, owned by `<c-entrance>`); `{% block title %}` provides heading text; social section guard (`{% if SOCIALACCOUNT_ENABLED %}`); email/password `<c-form>` guard (`{% if not SOCIALACCOUNT_ONLY %}`); `<c-form.crispy />` for field rendering including non-field errors (no standalone `{% if form.non_field_errors %}` block); submit button via `<c-button.stack>` + `<c-button icon="login" reverse />`; login link at bottom (`{% if login_url %}`)
- [X] T006 [P] [US1] Write integration tests in `tests/test_addons/test_allauth/test_signup_view.py` — assert page renders (HTTP 200) for each allauth field config: email-only, username-only, username+email; assert "Sign in" login link is present; assert no social buttons when `SOCIALACCOUNT_ENABLED=False`; assert that with `dac.addons.allauth` absent from `INSTALLED_APPS` allauth's own template renders instead of the DAC card (FR-009 / US1 scenario 1)
- [X] T007 [US1] Playwright MCP verify — visit signup page in email-only config, confirm: mvp AdminLTE/Bootstrap CSS is loaded, card is centred, email + password fields visible, "Already have an account?" link present in card header

- [X] TVAL-1 [US1] Run `poetry run pytest tests/test_addons/` — must pass with no failures

---

## Phase 4: User Story 2 — End User Creates Account via Email/Password (Priority: P1)

**Goal**: An anonymous user fills in the signup form, submits, and is either redirected to email verification or to `LOGIN_REDIRECT_URL`. Invalid submissions re-render with per-field inline errors without losing other field values.

**Independent Test**: Submit valid credentials → assert redirect. Submit invalid form (mismatched passwords, duplicate email) → assert page re-renders with inline field errors and other field values retained.

- [X] T008 [US2] Extend `tests/test_addons/test_allauth/test_signup_view.py` — POST valid form and assert redirect; POST with mismatched passwords and assert per-field error on password field; POST with duplicate email and assert error on email field; assert form repopulates other field values on re-render
- [X] T009 [P] [US2] Write `tests/test_addons/test_allauth/test_signup_e2e.py` — Playwright E2E: visit signup page → fill valid email + password → submit → assert redirect to verification notice or `LOGIN_REDIRECT_URL`
- [X] T010 [US2] Playwright MCP verify — submit form with invalid email format, confirm inline error appears immediately below the email field with no page reload required; submit valid credentials, confirm redirect

- [X] TVAL-2 [US2] Run `poetry run pytest tests/test_addons/test_allauth/` — must pass with no failures

---

## Phase 5: User Story 3 — End User Signs Up via Social Account (Priority: P2)

**Goal**: Social provider buttons appear above the form (FR-002), clicking one redirects to the provider's OAuth screen. The `socialaccount/signup.html` form handles the OAuth callback completion step.

**Independent Test**: Configure Google as a social provider. Visit signup page — confirm Google button appears above the "or" divider and the password form appears below. Click button — confirm redirect to Google OAuth URL begins.

- [X] T011 [US3] Write `dac/addons/allauth/templates/socialaccount/snippets/provider_list.html` — `{% load socialaccount %}`, `{% get_providers as socialaccount_providers %}`, loop rendering one Bootstrap Icon `<a>` tag per provider (using `btn btn-outline-secondary` classes and `<i class="bi bi-{provider}">` icons); handle OpenID brand sub-loop for `provider.id == "openid"` case
- [X] T012 [US3] Write `dac/addons/allauth/templates/socialaccount/snippets/login.html` — `{% include "socialaccount/snippets/provider_list.html" with process=page_layout|default:"login" %}` + `{% include "socialaccount/snippets/login_extra.html" %}`
- [X] T013 [US3] Write `dac/addons/allauth/templates/socialaccount/signup.html` — `<c-card>` with provider name + site name in header, `<c-form>` POSTing to `socialaccount_signup`, `<c-form.crispy />`, `{{ redirect_field }}`, submit `<c-button>`
- [X] T014 [P] [US3] Extend `tests/test_addons/test_allauth/test_signup_view.py` — assert social buttons present when `SOCIALACCOUNT_ENABLED=True` with one provider; assert social section absent when no providers configured; assert password form hidden when `SOCIALACCOUNT_ONLY=True`; assert multiple providers each render their own button
- [X] T015 [US3] Playwright MCP verify — social enabled config: Google button renders above `<c-card.divider>` with "or" label; social disabled config: no buttons and no divider; `SOCIALACCOUNT_ONLY=True`: password form is absent
- [X] T015b [P] [US3] Extend `tests/test_addons/test_allauth/test_signup_e2e.py` — Playwright E2E: with Google configured, assert clicking the Google button initiates an OAuth redirect (response URL starts with `accounts.google.com` or mocked provider URL); assert social section absent when `SOCIALACCOUNT_ENABLED=False`

- [X] TVAL-3 [US3] Run `python manage.py check` — must pass; then run `poetry run pytest tests/test_addons/test_allauth/` — must pass with no failures

---

## Phase 6: User Story 4 — Signup Disabled Message (Priority: P2)

**Goal**: When the allauth adapter's `is_open_for_signup()` returns `False`, allauth renders `account/signup_closed.html`. That template must show a clear, friendly card — no signup form, no social buttons.

**Independent Test**: Configure adapter to disable signups. Visit signup URL — assert HTTP 200, closed message card visible, no `<form>` element in page.

- [X] T016 [US4] Write `dac/addons/allauth/templates/account/signup_closed.html` — `<c-card class="shadow text-center">` with "Sign Up Closed" header and "We are sorry, but the sign up is currently closed." message body
- [X] T017 [P] [US4] Extend `tests/test_addons/test_allauth/test_signup_view.py` — configure adapter to return `is_open_for_signup=False`; assert response renders `signup_closed.html`; assert no `<form>` element in rendered HTML; assert closed message text present
- [X] T018 [US4] Playwright MCP verify — disabled signup renders the "Sign Up Closed" card; no form fields or social buttons visible on page
- [X] T018b [P] [US4] Extend `tests/test_addons/test_allauth/test_signup_e2e.py` — Playwright E2E: with adapter returning `is_open_for_signup=False`, assert `signup_closed.html` renders (no `<form>` element, "Sign Up Closed" heading present)

- [X] TVAL-4 [US4] Run `python manage.py check` — must pass; then run `poetry run pytest tests/test_addons/test_allauth/` — must pass with no failures

---

## Phase 5b: User Story 6 — End User Signs Up via Passkey (Priority: P2)

**Goal**: When `MFA_PASSKEY_SIGNUP_ENABLED=True` and `ACCOUNT_EMAIL_VERIFICATION_BY_CODE_ENABLED=True`, the main signup page surfaces a passkey option and the dedicated `/account-center/signup/passkey/` page renders within the `<c-entrance>` shell using Cotton components (FR-012).

**Independent Test**: Set `MFA_PASSKEY_SIGNUP_ENABLED=True` and `ACCOUNT_EMAIL_VERIFICATION_BY_CODE_ENABLED=True`. Assert the passkey option is visible on the main signup page. Visit `/account-center/signup/passkey/` — assert HTTP 200 and that the page renders within the entrance card shell with no raw Bootstrap layout markup.

- [X] T024 [US6] Write `dac/addons/allauth/templates/account/signup_by_passkey.html` — extend `account/base_entrance.html` (inherits `<c-entrance>` shell); `{% block title %}` set to "Sign up with a passkey"; `<c-form>` with `<c-form.crispy />` and `{{ redirect_field }}`; submit button via `<c-button.stack>` + `<c-button icon="fingerprint" reverse />`; back link to `signup_url` at bottom; no raw Bootstrap container/card/row markup (FR-012)
- [X] T025 [P] [US6] Extend `tests/test_addons/test_allauth/test_signup_view.py` — with `MFA_PASSKEY_SIGNUP_ENABLED=True` and `ACCOUNT_EMAIL_VERIFICATION_BY_CODE_ENABLED=True`: assert `/account-center/signup/passkey/` returns HTTP 200; assert passkey option link is visible on main signup page; with either setting `False`: assert passkey option absent from main signup page
- [X] T026 [US6] Playwright MCP verify — with passkey settings enabled: confirm "Sign up with a passkey" option appears on the main signup page and `/account-center/signup/passkey/` renders within the entrance card shell

- [X] TVAL-6 [US6] Run `poetry run pytest tests/test_addons/test_allauth/` — must pass with no failures

---

## Phase 7: User Story 5 — Already Authenticated User Visits Signup (Priority: P3)

**Goal**: Allauth's `AlreadyLoggedInMixin` redirects authenticated users before the template renders. No template work is needed — this phase is covered by a test confirming allauth's existing behavior functions correctly with the addon enabled.

**Independent Test**: Log in as an existing user, then visit the signup URL directly. Assert redirect to `LOGIN_REDIRECT_URL` (or allauth's configured redirect).

- [X] T019 [P] [US5] Extend `tests/test_addons/test_allauth/test_signup_view.py` — create authenticated test client, GET signup URL, assert HTTP 302 redirect to `LOGIN_REDIRECT_URL`; confirm no signup form is rendered

---

## Phase 8: Multi-Viewport Screenshot Coverage (FR-011 / Principle XIII)

**Purpose**: Satisfy FR-011 (constitution Principle XIII, v1.1.2) — capture automated pytest-playwright screenshots at three canonical viewport sizes for each visually distinct settings permutation and persist them as living documentation under `docs/_static/`. Screenshot tests live in `screenshots/` (not `tests/`) and are run explicitly with `pytest screenshots/`.

**Permutations required** (6 configurations × 3 viewports = 18 screenshot files):

| Slug | Configuration |
|------|---------------|
| `signup-page-social-disabled` | `SOCIALACCOUNT_ENABLED=False` — email/password form only |
| `signup-page-social-enabled` | One Google provider + SocialApp configured — social buttons + divider + form |
| `signup-page-social-only` | `SOCIALACCOUNT_ONLY=True` — social buttons only, no email/password form |
| `signup-page-signup-closed` | Adapter returns `is_open_for_signup=False` — closed message card, no form |
| `signup-page-passkey-enabled` | `MFA_PASSKEY_SIGNUP_ENABLED=True` + `ACCOUNT_EMAIL_VERIFICATION_BY_CODE_ENABLED=True` — signup page with passkey option visible |
| `signup-by-passkey-page` | Same passkey settings, screenshot taken at `/account-center/signup/passkey/` |

- [X] T022 Create `docs/_static/desktop/` and `docs/_static/mobile/` directories; add a `.gitkeep` file in each so the directories are committed to the repository before the first screenshot test run
- [X] T023 [P] Write `screenshots/test_signup_screenshots.py` — parametrize over three viewport sizes `(1440, 900)`, `(768, 1024)`, `(390, 844)` and six settings permutations (social-disabled, social-enabled, social-only, signup-closed, passkey-enabled, signup-by-passkey); for each combination navigate to the appropriate URL with the appropriate settings override, capture a full-page screenshot, and save to `docs/_static/{tier}/{slug}.png`; assert each output file is non-zero bytes
- [X] TVAL-5 Run `poetry run pytest screenshots/ --no-cov` — all 18 screenshot files must be generated; **agent MUST visually inspect every generated screenshot** (open each `docs/_static/{desktop,tablet,mobile}/signup-page-*.png` and `signup-by-passkey-page-*.png`) and confirm the rendered output matches the acceptance criteria for each permutation before marking this task complete

---

## Final Phase: Polish & Cross-Cutting

**Purpose**: Lint all modified templates, run the full test suite, and confirm nothing is broken end-to-end.

- [x] T020 [P] Run `poetry run djlint dac/addons/allauth/templates/ --reformat` — fix any reported issues in all 7 modified templates; add `{# djlint:off #}` / `{# djlint:on #}` guards around Cotton component tags if djlint cannot parse them cleanly; run `Select-String -Path 'dac/addons/allauth/templates/**/*.html' -Pattern '{% element'` — must return zero matches (FR-008 compliance check)
- [X] T021 Run `poetry run pytest tests/` with full test suite — all tests must pass; fix any regressions

---

## Dependencies

```
T001
└── T002
    └── T003
        └── T004
            ├── T005 (US1)
            │   ├── T006 (US1, parallel)
            │   └── T007 (US1)
            │       └── TVAL-1
            │           ├── T008 (US2)
            │           │   ├── T009 (US2, parallel)
            │           │   └── T010 (US2)
            │           │       └── TVAL-2
            │           │           ├── T011 (US3)
            │           │           │   └── T012 (US3)
            │           │           │       └── T013 (US3)
            │           │           │           ├── T014 (US3, parallel)
            │           │           │           ├── T015 (US3)
            │           │           │           │   ├── T015b (US3, parallel)
            │           │           │           │   └── TVAL-3
            │           │           │           │       └── T016 (US4)
            │           │           │           │           ├── T017 (US4, parallel)
            │           │           │           │           ├── T018 (US4)
            │           │           │           │           │   └── T018b (US4, parallel)
            │           │           │           │           └── TVAL-4
            │           │           │           │               ├── T022 (screenshots dir setup)
            │           │           │           │               │   └── T023 [P] (screenshot tests)
            │           │           │           │               │       └── TVAL-5 (run + inspect)
            │           │           └── T019 (US5, parallel with US3+)
            ├── T020 (final polish, parallel with T022→T023)
            └── T021 (final, after T020 and TVAL-5)
```

## Parallel Execution Per Story

Each story's parallel tasks ([P]) can be started simultaneously with the preceding implementation task **once its dependencies are met**:

| Story | Parallel Pair |
|---|---|
| Foundational | T004 runs sequentially after T003 (manage.py check requires templates to exist) |
| US1 | T006 (tests) runs alongside T005 (template) |
| US2 | T009 (E2E test) runs alongside T008 (integration test extension) |
| US3 | T014 (tests) runs alongside T011–T013 (templates) |
| US4 | T017 (tests) runs alongside T016 (template) |
| US5 | T019 independent of US3/US4 once TVAL-2 passes |
| US6 | T025 (tests) runs alongside T024 (template) |
| Polish | T020 (djlint) runs as soon as all templates are written |
| Screenshots | T022 (dir setup) → T023 (tests) run in parallel with T020 once TVAL-6 passes |

## Implementation Strategy

**MVP scope** (deliver first): Phase 2 + Phase 3 — layout base templates + `account/signup.html`. This gives any developer with allauth a styled email/password signup page with zero extra configuration, satisfying US1 (P1) and the core of US2 (P1).

**Increment 2**: Phase 4 (US2 tests + E2E) — validates the form actually works, not just renders.

**Increment 3**: Phase 5 (US3) — social provider support. Only needed when `allauth.socialaccount` is in use.

**Increment 4**: Phase 6 (US4) — signup closed page. Low-effort, high-value for closed-beta scenarios.

**Increment 5**: Phase 7 (US5) + Phase 8 (screenshots) + Polish — authenticated redirect test, viewport screenshot suite, linting.

---

**Total tasks**: 29 implementation tasks + 6 validation checkpoints  
**Tasks per user story**: US1: 3 | US2: 3 | US3: 6 | US4: 4 | US5: 1 | US6: 3 | Screenshots (Phase 8): 2  
**Parallel opportunities**: 9 task pairs (added T020 ‖ T022→T023, T025 ‖ T024)  
**Suggested MVP**: Phase 2 + Phase 3 (T001–T007 + TVAL-1)
