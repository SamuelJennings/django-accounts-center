# Tasks: Allauth Email Management Templates

**Input**: Design documents from `specs/006-allauth-email-management/`
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, contracts/component-interface.md ✅

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3)
- Tests are **pre-written** in `tests/test_addons/test_allauth/test_email_management_view.py` and `screenshots/test_email_management_screenshots.py` — implementation goal is to make them pass

## Path Conventions

- **Addon templates**: `dac/addons/allauth/templates/account/`
- **Integration tests** (pre-written): `tests/test_addons/test_allauth/test_email_management_view.py`
- **Screenshot tests** (pre-written): `screenshots/test_email_management_screenshots.py`
- **Screenshot artifacts**: `docs/_static/{desktop,tablet,mobile}/`

---

## Phase 1: Setup

No project setup required. All files exist; no migrations, no new Python files, no new components. Proceed directly to Phase 2.

---

## Phase 2: Foundational — Fix Template Inheritance Root

**Purpose**: Correct the one-line extends defect in `base_manage.html` so all email management templates can inherit the DAC management layout.

**⚠️ CRITICAL**: No user story work can begin until this task is complete. This single change propagates the DAC layout to all descendants.

- [ ] T001 Change `{% extends "allauth/layouts/manage.html" %}` to `{% extends "dac/base.html" %}` in `dac/addons/allauth/templates/account/base_manage.html`

**Checkpoint**: `base_manage.html` now chains `dac/base.html`. User story implementation can begin.

---

## Phase 3: User Story 1 — Developer Wires Email Templates into the DAC Layout (Priority: P1)

**Goal**: `email_change.html` and `verified_email_required.html` both override `{% block page.content %}` (not `{% block content %}`), placing their content inside the DAC card-stack rather than bypassing the layout.

**Independent Test**:

```bash
poetry run pytest tests/test_addons/test_allauth/test_email_management_view.py::TestEmailChangeView tests/test_addons/test_allauth/test_email_management_view.py::TestVerifiedEmailRequiredView --no-cov -v
```

### Implementation for User Story 1

- [ ] T002 [US1] Rewrite `email_change.html` to use `{% block page.content %}` (not `{% block content %}`), add `{% block page.breadcrumbs %}` override, and keep `<c-form>` as the form wrapper in `dac/addons/allauth/templates/account/email_change.html`

  Exact structure required (from `contracts/component-interface.md`):

  ```django
  {% extends "account/base_manage_email.html" %}
  {% load i18n crispy_forms_tags %}

  {% block title %}{% trans "Email Address" %}{% endblock title %}

  {% block page.breadcrumbs %}
    {{ block.super }}
    <c-navigation.breadcrumbs.item text="{% trans "Email Address" %}" />
  {% endblock page.breadcrumbs %}

  {% block page.content %}
    {# warn_no_email snippet, conditional current/pending fields, c-form, hidden #pending-email form #}
  {% endblock page.content %}
  ```

- [ ] T003 [P] [US1] Fix `verified_email_required.html` to use `{% block page.content %}` (not `{% block content %}`), add `{% block title %}` override, and wrap paragraphs in an explicit `<c-card>` in `dac/addons/allauth/templates/account/verified_email_required.html`

  Exact structure required:

  ```django
  {% block page.content %}
    <c-card>
      <p>{% blocktrans %}... verification explanation ...{% endblocktrans %}</p>
      <p>{% blocktrans %}... spam folder note ...{% endblocktrans %}</p>
      <p>{% blocktrans %}<strong>Note:</strong> you can still <a href="{{ email_url }}">change your email address</a>.{% endblocktrans %}</p>
    </c-card>
  {% endblock page.content %}
  ```

- [ ] TVAL-1 [US1] Run `python manage.py check --settings=tests.settings` and confirm zero errors after completing T002 and T003

- [ ] TPWVI-1 [US1] Open the email change and verified-email-required pages in the Playwright MCP browser and visually confirm:
  - DAC Account Center sidebar is visible on both pages
  - Breadcrumb trail on `email_change_test` reads "Account Center › Email Address"
  - The `<c-form>` renders inside the card-stack (not a raw unstyled form)
  - Current email disabled input is present on the change page
  - "Change Email" submit button is visible
  - On the verified-email-required page: a card wrapping the explanation text is visible, and the link to the email management page is rendered

**Checkpoint**: US1 complete when TVAL-1 passes, TPWVI-1 visual check passes, and `TestEmailChangeView` and `TestVerifiedEmailRequiredView` test classes pass.

---

## Phase 4: User Story 2 — End User Manages Email Addresses with a Consistent UI (Priority: P2)

**Goal**: `email.html` renders all expected form buttons with the correct `name` attributes so the management flow works (make-primary, re-send, remove, add-email).

**Independent Test**:

```bash
poetry run pytest tests/test_addons/test_allauth/test_email_management_view.py::TestEmailMultiView --no-cov -v
```

### Implementation for User Story 2

- [ ] T004 [US2] Audit `email.html` and correct any functional errors so all `TestEmailMultiView` tests pass in `dac/addons/allauth/templates/account/email.html`

  Audit checklist (check each item against the pre-written tests):
  - [ ] `name="action_send"` MUST appear in the dropdown for every address regardless of verified status — remove the `{% if not emailaddress.verified %}` guard around this item (required by `test_action_send_button_present`, which creates a single verified+primary address and asserts `action_send` is present)
  - [ ] `name="action_primary"` MUST appear in the dropdown for every address regardless of primary status — remove the `{% if not emailaddress.primary %}` guard around this item (required by `test_action_primary_button_present`, which creates a single verified+primary address and asserts `action_primary` is present)
  - [ ] `name="action_remove"` present for each address (with `disabled` class when primary)
  - [ ] `name="action_add"` present when `can_add_email` is True
  - [ ] All `<form>` `action` attributes target `{% url "account_email" %}`
  - [ ] All page content is inside `{% block page.content %}` (already correct — do not move)
  - [ ] `account/js/account.js` loaded in `{% block extra_js %}` (already correct)

  Make only the corrections needed to pass the failing tests. Do not cosmetically refactor.

- [ ] TVAL-2 [US2] Run `python manage.py check --settings=tests.settings` and confirm zero errors after completing T004

- [ ] TPWVI-2 [US2] Open `/accounts/email/` in the Playwright MCP browser and visually confirm:
  - DAC Account Center sidebar is visible
  - Both email addresses appear in the list with Primary/Verified badges
  - Three-dots dropdown per address is clickable and reveals all action items (including Make Primary and Re-send Verification)
  - "Add email" form is visible below the list

**Checkpoint**: US2 complete when TVAL-2 passes, TPWVI-2 visual check passes, and `TestEmailMultiView` test class passes.

---

## Phase 5: User Story 3 — Developer Verifies Templates via Automated Tests (Priority: P3)

**Goal**: The full integration test suite and screenshot tests pass with zero failures.

**Independent Test**:

```bash
poetry run pytest tests/test_addons/test_allauth/test_email_management_view.py --no-cov
```

### Implementation for User Story 3

- [ ] T005 [P] [US3] Run the full integration test suite and confirm zero failures

  ```bash
  poetry run pytest tests/test_addons/test_allauth/test_email_management_view.py --no-cov -v
  ```

  Expected: All tests in `TestEmailChangeView`, `TestEmailMultiView`, and `TestVerifiedEmailRequiredView` pass. If any test fails, return to the appropriate phase and correct the template.

- [ ] T006 [P] [US3] Run the screenshot tests and confirm 18 PNGs are generated (6 states × 3 viewports) in `screenshots/test_email_management_screenshots.py`

  ```bash
  poetry run pytest screenshots/test_email_management_screenshots.py -v
  ```

  Expected output files:

  ```
  docs/_static/{desktop,tablet,mobile}/
    email-change-no-pending.png
    email-change-pending.png
    email-change-no-email.png
    email-multi-list.png
    email-verified-required.png
    email-warn-no-email.png
  ```

**Checkpoint**: US3 complete when all 3 test classes pass and 18 PNGs are generated.

---

## Phase 6: Polish & Cross-Cutting Concerns

- [ ] T007 [P] Verify no `{% element %}` or `{% endelement %}` tags remain in any modified template file

  ```powershell
  Select-String -Path `
    "dac/addons/allauth/templates/account/base_manage.html",`
    "dac/addons/allauth/templates/account/email_change.html",`
    "dac/addons/allauth/templates/account/verified_email_required.html",`
    "dac/addons/allauth/templates/account/email.html" `
    -Pattern "{% element|{% endelement"
  ```

  Expected: No matches. If any are found, remove them before proceeding.

- [ ] T007b [P] Verify all user-visible strings in modified templates are wrapped in `{% trans %}` or `{% blocktrans %}`

  Scan each modified file for bare English prose not preceded by a translation tag. Pay particular attention to button text, label text, and help/hint text added or changed during the rewrites (T002, T003) and the audit (T004). Correct any unwrapped string in-place.

- [ ] T008 [P] Run the full test suite to confirm no regressions

  ```bash
  poetry run pytest tests/ --no-cov -q
  ```

- [ ] T009 Mark all tasks complete in `specs/006-allauth-email-management/tasks.md`

---

## Dependencies

```
T001 ──► T002 ──┐
            T003 ─┤─► TVAL-1 ──► TPWVI-1 ─┐
T001 ──► T004 ──► TVAL-2 ──► TPWVI-2 ──────┤
                                             ├──► T005 [P] + T006 [P]
                                             └──► T007 [P] + T007b [P] + T008 ──► T009
```

T002 and T003 can run in parallel after T001. T004 can also run in parallel with T002/T003. T005 and T006 can run in parallel after both TPWVI-1 and TPWVI-2 pass. T007 and T007b can run in parallel.

## Parallel Execution Example

**After T001**:

- Worker A: T002 — rewrite `email_change.html`
- Worker B: T003 — fix `verified_email_required.html`
- Worker C: T004 — audit `email.html`

**After T002 + T003**:

- Run TVAL-1 (`manage.py check`), then TPWVI-1 (Playwright MCP visual verification)

**After T004**:

- Run TVAL-2 (`manage.py check`), then TPWVI-2 (Playwright MCP visual verification)

**After TPWVI-1 + TPWVI-2**:

- Run T005 [P] and T006 [P] in parallel

## Implementation Strategy

**MVP Scope (US1 only)**: Complete T001 + T002 + T003. This gives the developer-facing inheritance chain fix — all email management pages render in the DAC layout.

**Full Delivery**: Add T004 (US2 — correct email.html) + T005–T006 (US3 — all tests pass).
