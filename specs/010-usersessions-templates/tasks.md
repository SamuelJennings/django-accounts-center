# Tasks: User Sessions Management Templates

**Input**: Design documents from `specs/010-usersessions-templates/`
**Prerequisites**: plan.md ✅ | spec.md ✅ | research.md ✅ | data-model.md ✅ | contracts/component-interface.md ✅ | quickstart.md ✅

**Scope**: 2 template files edited · 1 integration test file · 1 screenshot test file · 6 PNGs (2 states × 3 viewports)

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3)
- Exact file paths included in every task description

---

## Phase 1: Setup

**Purpose**: Verify the test baseline before any changes are made

- [ ] T001 Run existing allauth addon test suite to establish a clean baseline: `poetry run pytest tests/test_addons/test_allauth/ --no-cov -q` — MUST pass before any edits begin

---

## Phase 2: User Story 1 — Developer Wires Sessions into DAC Layout (Priority: P1) 🎯 MVP

**Goal**: Fix `usersessions/base_manage.html` so the Sessions page inherits the full DAC Account Center layout (sidebar, breadcrumbs, card-stack). One-line change that propagates to all usersession templates.

**Independent Test**: Navigate to `/accounts/usersessions/` as a logged-in user; the Account Center sidebar, "Account Center" root breadcrumb, and "Sessions" leaf breadcrumb must all be visible.

- [ ] T002 [US1] Edit `dac/addons/allauth/templates/usersessions/base_manage.html` — change the single `extends` line from `allauth/layouts/manage.html` to `dac/base.html`

  Before:
  ```django
  {% extends "allauth/layouts/manage.html" %}
  ```
  After:
  ```django
  {% extends "dac/base.html" %}
  ```

- [ ] T003 [US1] playwright-cli skill verify — consult `.github/skills/playwright-cli/SKILL.md` before executing; start dev server (`poetry run python manage.py runserver`), log in as a test user, navigate to `/accounts/usersessions/`; confirm the Account Center sidebar, "Account Center" breadcrumb, "Sessions" breadcrumb, and "Sessions" heading are all rendered (page must NOT show the raw allauth layout)

- [ ] TVAL-1 [US1] Run `python manage.py check` — MUST pass with no errors after T002

**Checkpoint**: US1 complete — Sessions page now renders inside the DAC Account Center layout

---

## Phase 3: User Story 2 — End User Views and Signs Out Active Sessions (Priority: P2)

**Goal**: Fully rewrite `usersession_list.html` as a clean Cotton template: Bootstrap table inside `<c-card>`, `<c-badge variant="success">` for the current session, bulk sign-out form with `<c-button variant="primary">`, conditional "Last Seen" column. Zero allauth `{% element %}` tags.

**Independent Test**: Render the template with representative context (multiple sessions + `is_current` on one; `show_last_seen_at` both True and False); assert table rows, "Current" badge, button text, and column visibility are correct.

- [ ] T004 [US2] Fully rewrite `dac/addons/allauth/templates/usersessions/usersession_list.html` using the interface contract in `specs/010-usersessions-templates/contracts/component-interface.md`:

  - `{% load i18n humanize %}` (remove `{% load allauth %}` — no allauth tags used)
  - `{% block title %}{% trans "Sessions" %}{% endblock title %}`
  - `{% block page.breadcrumbs %}{{ block.super }}<c-breadcrumbs.item text="{% trans 'Sessions' %}" />{% endblock page.breadcrumbs %}`
  - `{% block page.content %}` — containing:
    - URL resolution: `{% url 'usersessions_list' as action_url %}` / `{% url 'account_logout' as action_url %}` conditional on `session_count > 1`
    - `<c-card>` wrapping a `<form method="post" action="{{ action_url }}">`
    - `{% csrf_token %}` inside the form
    - `<table class="table">` with thead (Started At, IP Address, Browser, optionally Last Seen, blank badge column) and tbody
    - Each `{% for session in sessions %}` row: `created_at|naturaltime`, `ip`, `user_agent` wrapped in `<span class="text-truncate d-inline-block" style="max-width: 20ch">` (or equivalent constrained container — `text-truncate` alone on a `<td>` is silent no-op; `d-inline-block` + `max-width` are required for truncation to work), optionally `last_seen_at|naturaltime`, and `<c-badge variant="success">` when `session.is_current`
    - `<c-button type="submit" variant="primary">` with conditional text ("Sign Out Other Sessions" vs "Sign Out")
  - All user-visible strings wrapped in `{% trans %}` (i18n)
  - NO `{% element %}`, `{% endelement %}`, or `{% slot %}` tags

- [ ] T005 [P] [US2] playwright-cli skill verify — consult `.github/skills/playwright-cli/SKILL.md` before executing; multiple-sessions state: confirm session table rows are visible, current session row has a green "Current" badge, "Sign Out Other Sessions" button is present, and the page is inside the DAC layout

- [ ] T006 [P] [US2] playwright-cli skill verify — consult `.github/skills/playwright-cli/SKILL.md` before executing; single-session state (manually create a test scenario or inspect template logic): confirm button text reads "Sign Out" (not "Sign Out Other Sessions")

- [ ] TVAL-2 [US2] Run `python manage.py check` — MUST pass after T004

- [ ] TVAL-3 [US2] Run `poetry run pytest tests/test_addons/test_allauth/ --no-cov -q` — MUST pass (existing tests must not regress)

**Checkpoint**: US2 complete — Sessions page shows Bootstrap table, Current badge, and sign-out form in the DAC layout

---

## Phase 4: User Story 3 — Developer Verifies Templates via Automated Tests (Priority: P3)

**Goal**: Automated integration tests and screenshot tests proving every conditional branch renders correctly without starting a server.

**Independent Test**: `pytest tests/test_addons/test_allauth/test_usersessions_view.py --no-cov -v` passes with zero failures. `pytest screenshots/test_usersessions_screenshots.py` generates 6 PNGs.

- [ ] T007 [P] [US3] Create `tests/test_addons/test_allauth/test_usersessions_view.py` — integration tests using the Cotton rendering fixtures (see `cotton-test-components` skill):

  Consult `.github/skills/cotton-test-components/SKILL.md` and `.github/skills/pytest-django-testing/SKILL.md` before writing tests.

  Required test cases (each covers one acceptance scenario from spec.md):
  1. **Layout test** (US1): Render with multiple sessions → assert Account Center sidebar element, "Account Center" breadcrumb text, "Sessions" breadcrumb text, and the heading string "Sessions" (rendered via `{% block title %}`) are all present in output
  2. **Table rows test** (US2 SC1): Render with 2 sessions using pinned `created_at` values (e.g., `timezone.now() - timedelta(days=1)` and `timezone.now() - timedelta(hours=2)`) → assert both IP addresses (`"1.2.3.4"`, `"5.6.7.8"`) and user-agent substrings appear in rows; use static field values for assertions, not `naturaltime` output
  3. **Current badge test** (US2 SC2): Render with `is_current=True` on one session → assert "Current" text appears in output; `is_current=False` sessions have no badge
  4. **Sign Out Other Sessions test** (US2 SC2, multiple): Render with `session_count=2` → assert button text "Sign Out Other Sessions" and form action `usersessions_list` URL
  5. **Sign Out test** (US2 SC3, single): Render with `session_count=1` → assert button text "Sign Out" and form action `account_logout` URL
  6. **Last Seen visible test** (US2 SC4): Render with `show_last_seen_at=True` → assert "Last seen at" column header is present
  7. **Last Seen hidden test** (US2 SC4): Render with `show_last_seen_at=False` → assert "Last seen at" column header is NOT present
  8. **No allauth element tags test** (US2 SC5): Render → assert rendered output contains no `{% element %}` and no `{% endelement %}` strings (allauth-specific tags); do NOT assert absence of `{% slot %}` in rendered output since Cotton components may emit that tag legitimately

  Use factory-boy (`DjangoModelFactory`) for `UserSession` test data if model access is needed; otherwise create plain dataclass/mock objects with the required attributes.

- [ ] T008 [P] [US3] Create `screenshots/test_usersessions_screenshots.py` — pytest-playwright screenshot tests (2 states × 3 viewports = 6 PNGs):

  Consult `.github/skills/playwright-cli/SKILL.md` for screenshot test patterns.

  States:
  - `sessions-multiple`: page rendered with ≥2 active sessions (current + others visible)
  - `sessions-single`: page rendered with 1 active session (current only, "Sign Out" button)

  Viewports: desktop (1440×900), tablet (768×1024), mobile (390×844)

  Save to:
  - `docs/_static/desktop/sessions-multiple.png`
  - `docs/_static/desktop/sessions-single.png`
  - `docs/_static/tablet/sessions-multiple.png`
  - `docs/_static/tablet/sessions-single.png`
  - `docs/_static/mobile/sessions-multiple.png`
  - `docs/_static/mobile/sessions-single.png`

  Use `@pytest.mark.parametrize` or a viewport fixture to avoid duplicating assertion logic across sizes.

- [ ] TVAL-4 [US3] Run `poetry run pytest tests/test_addons/test_allauth/test_usersessions_view.py --no-cov -v` — MUST pass with zero failures; all 8 test cases green

- [ ] TVAL-5 [US3] Run `poetry run pytest screenshots/test_usersessions_screenshots.py -v` — MUST produce 6 PNG files in `docs/_static/`; inspect each screenshot visually to confirm correct layout (Principle XIII agent visual verification)

**Checkpoint**: US3 complete — every conditional branch verified by automated tests; 6 screenshots committed as visual documentation

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Final quality gates across all modified files

- [ ] T009 [P] Run djlint on modified templates — zero violations:
  ```bash
  poetry run djlint dac/addons/allauth/templates/usersessions/base_manage.html dac/addons/allauth/templates/usersessions/usersession_list.html --check
  ```
  Fix any violations before marking complete.

- [ ] T010 [P] Grep for residual allauth element tags in modified templates — MUST return zero matches (SC-002):
  ```bash
  Select-String -Path "dac\addons\allauth\templates\usersessions\*.html" -Pattern "element|endelement" -SimpleMatch
  ```
  Any matches are blocking defects.

- [ ] T011 Run full test suite to confirm no regressions:
  ```bash
  poetry run pytest tests/ --no-cov -q
  ```
  MUST pass with zero failures.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — run immediately
- **US1 (Phase 2)**: Depends on Phase 1 baseline passing; T002 is a one-line edit
- **US2 (Phase 3)**: Depends on T002 (base_manage.html fix) — `usersession_list.html` must extend through a fixed `base_manage.html` for full layout testing
- **US3 (Phase 4)**: Depends on T004 (template rewrite complete) — tests assert the rewritten template's output; T007 and T008 can run in parallel
- **Polish (Phase 5)**: Depends on all US phases complete; T009 and T010 can run in parallel

### User Story Dependencies

- **US1 (P1)**: Can start immediately after Phase 1 — no story dependencies
- **US2 (P2)**: Depends on US1 (T002) for full layout chain; template rewrite (T004) can be drafted independently but cannot be fully validated until T002 is merged
- **US3 (P3)**: Depends on US2 (T004) complete — tests assert the rewritten template's output structure

### Within Each User Story

- T002 → T003 → TVAL-1 (sequential within US1)
- T004 → [T005 ‖ T006] → TVAL-2 → TVAL-3 (parallel Playwright verifies after T004)
- [T007 ‖ T008] → TVAL-4 → TVAL-5 (parallel test files, sequential validation)
- [T009 ‖ T010] → T011 (parallel polish checks, then full suite)

---

## Parallel Execution Examples

### User Story 2

```bash
# After T004 is complete, launch both Playwright verifications in parallel:
Task T005: Verify multiple-sessions state in browser
Task T006: Verify single-session state in browser
```

### User Story 3

```bash
# Both test files can be written simultaneously (different files, no shared state):
Task T007: tests/test_addons/test_allauth/test_usersessions_view.py
Task T008: screenshots/test_usersessions_screenshots.py
```

### Polish

```bash
# Both quality gate checks can run simultaneously:
Task T009: djlint check on template files
Task T010: grep for residual element tags
```

---

## Implementation Strategy

### MVP First (User Story 1 + 2 Only)

1. Complete Phase 1: Baseline check (T001)
2. Complete Phase 2: US1 — one-line `base_manage.html` fix (T002–TVAL-1)
3. Complete Phase 3: US2 — full `usersession_list.html` rewrite + Playwright verify (T004–TVAL-3)
4. **STOP and VALIDATE**: Manually verify Sessions page in browser; confirm all US2 acceptance criteria met
5. Ship if ready — US3 (tests) can follow in the next iteration

### Incremental Delivery

| Step | Tasks | Deliverable |
|---|---|---|
| 1 | T001 | Confirmed green baseline |
| 2 | T002–TVAL-1 | Sessions page inside DAC layout (US1 ✅) |
| 3 | T004–TVAL-3 | Sessions table, badge, sign-out form in browser (US2 ✅) |
| 4 | T007–TVAL-5 | All conditional branches covered by automated tests (US3 ✅) |
| 5 | T009–T011 | djlint clean, zero element tags, full suite green |

---

## Notes

- [P] tasks use different files or independent tools — safe to run simultaneously
- All `{% element %}` / `{% endelement %}` / `{% slot %}` tags are BANNED in the rewritten template (FR-006, SC-002)
- `{% load allauth %}` is NOT needed in the rewrite — remove it
- `{% load i18n humanize %}` ARE needed — keep both
- Refer to `specs/010-usersessions-templates/contracts/component-interface.md` for the exact block structure and component attributes
- Refer to `specs/010-usersessions-templates/data-model.md` for the 4-state matrix (session_count × show_last_seen_at)
- The `text-truncate` class alone requires a block-level or `d-inline-block` container with a `max-width` to work correctly
