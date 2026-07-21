# Tasks: Social Account Connections Templates

**Input**: Design documents from `specs/009-socialaccount-connections/`
**Spec**: [spec.md](spec.md) | **Plan**: [plan.md](plan.md)

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies on incomplete tasks)
- **[Story]**: Which user story this task belongs to (US1, US2, US3)
- All file paths are relative to the repository root

## Dependencies

```
Phase 1 (Setup) → Phase 2 (Foundational) → Phase 3 (US1) → Phase 4 (US2) → Phase 5 (US3) → Phase 6 (Polish)
                                                                ↑
                                                   authentication_error.html (US2)
                                                   is independent of connections.html (US1)
                                                   but is grouped in Phase 4 for clarity
```

**US1 and US2 templates are independent of each other after Phase 2.**

## Parallel Execution Opportunities

- After T001 (base_manage.html fix), US1 (connections.html) and US2 (authentication_error.html) can proceed independently
- T006 and T007 (US2 test stubs + template fix) can be written/applied in any order
- Screenshot tests (T010) can be written in parallel with completing integration tests (T008)

---

## Phase 1: Setup

**Purpose**: Ensure screenshot output directories exist before any screenshot tasks run

- [X] T001 Verify `docs/_static/desktop/`, `docs/_static/tablet/`, and `docs/_static/mobile/` directories exist; create any that are missing per Principle XIII

---

## Phase 2: Foundational — Fix `socialaccount/base_manage.html`

**Purpose**: One-line extends fix that propagates the DAC layout to all socialaccount management templates. MUST complete before any US1 or US2 template work.

**⚠️ CRITICAL**: No user story template work can begin until this phase is complete — the layout chain does not resolve correctly until `base_manage.html` extends `dac/base.html`.

- [X] T002 Edit `dac/addons/allauth/templates/socialaccount/base_manage.html` — change `{% extends "allauth/layouts/manage.html" %}` to `{% extends "dac/base.html" %}` (single line change per `contracts/component-interface.md` §1)

**Checkpoint**: `base_manage.html` fix is in place

- [X] TVAL-F1 Run `poetry run python manage.py check` — MUST pass with no errors
- [X] TVAL-F2 Run `poetry run pytest tests/test_addons/test_allauth/ --no-cov -q` — existing tests MUST still pass

---

## Phase 3: User Story 1 — Developer Wires Social Account Management into the DAC Layout (Priority: P1) 🎯 MVP

**Goal**: `socialaccount/connections.html` fully rewritten as a Cotton template rendering inside the DAC Account Center sidebar/breadcrumbs/card-stack shell via `{% block page.content %}`. A single `<c-card title="Account Connections">` lists all configured social providers; connected providers appear disabled with a "Connected" badge and "Remove" button; unconnected providers appear as clickable connect buttons. A custom template tag (`get_connected_provider_map`) provides the provider-to-account mapping (FR-003b).

**Independent Test**: Render the connections page for an authenticated user and assert the DAC sidebar, "Account Center" root breadcrumb, and "Account Connections" leaf breadcrumb are present in the output.

### Integration Tests for User Story 1

> **Write these tests FIRST. Run with `--no-cov -q` and confirm they FAIL before T005.**

- [X] T003 [US1] Write integration test class `TestConnectionsLayoutAndStructure` in `tests/test_addons/test_allauth/test_social_connections_view.py` covering US1 acceptance scenarios:
  - `test_renders_200_for_authenticated` — GET `socialaccount_connections` returns HTTP 200
  - `test_no_element_tags_in_output` — rendered HTML contains no `{% element` or `{% endelement` strings
  - `test_dac_layout_sidebar_present` — rendered HTML contains `<aside class="app-sidebar">` (confirmed selector from `tests/test_components/test_dac_base.py:L43`)
  - `test_breadcrumb_account_connections_present` — rendered HTML contains the "Account Connections" breadcrumb leaf
  - `test_content_in_page_content_block` — rendered HTML does NOT contain the raw allauth heading outside the card-stack

- [X] T004 [US1] Confirm T003 tests FAIL before implementation: run `poetry run pytest tests/test_addons/test_allauth/test_social_connections_view.py --no-cov -q`
  - `test_renders_200_for_authenticated` MAY already pass (page loads; old template still renders)
  - `test_dac_layout_sidebar_present`, `test_breadcrumb_account_connections_present`, and `test_no_element_tags_in_output` MUST fail (old template has no DAC sidebar, no breadcrumb, and contains `{% element %}` tags)
  - If ALL tests pass before T005, stop and investigate — the existing template has already been partially corrected

### Implementation for User Story 1

- [ ] T005 [US1] Rewrite `dac/addons/allauth/templates/socialaccount/connections.html` per FR-002/FR-003/FR-004/FR-005:
  - Load `{% load i18n socialaccount %}` (for provider tags used by snippets)
  - Keep `{% block title %}` and `{% block page.breadcrumbs %}` unchanged
  - In `{% block page.content %}`:
    - `{% if form.accounts %}` branch: `<c-card title="{% trans 'Account Connections' %}">` with `<c-list flush :border="False">` — one `<c-list.item>` per account; each item shows `<c-badge text="{{ provider_account.get_brand.name }}">` and an inline POST form to `{% url 'socialaccount_connections' %}` with a hidden `account` PK and `<c-button text="{% trans 'Remove' %}" variant="danger" />`
    - `{% else %}` branch: empty-state `<c-card>` with `<c-text>{% trans "You currently have no third-party accounts connected to this account." %}</c-text>`
    - "Add a Third-Party Account" `<c-card>` in all cases: `{% include "socialaccount/snippets/provider_list.html" with process="connect" %}` and `{% include "socialaccount/snippets/login_extra.html" %}`
  - All user-visible strings in `{% trans %}`; zero `{% element %}` / `{% endelement %}` / `{% slot %}` tags

- [ ] T006 [US1] Playwright MCP verification — open the connections page in a real browser, confirm `<aside class="app-sidebar">` is present, "Account Connections" breadcrumb is visible, connected account badges and Remove buttons are rendered, and the "Add a Third-Party Account" section appears

**Checkpoint**: User Story 1 is fully functional and independently testable

- [X] TVAL-1A Run `poetry run python manage.py check` — MUST pass
- [ ] TVAL-1B Run `poetry run pytest tests/test_addons/test_allauth/test_social_connections_view.py --no-cov -q` — T003 tests MUST now pass

---

## Phase 4: User Story 2 — End User Manages Connected Social Accounts with a Consistent UI (Priority: P2)

**Goal**: `socialaccount/connections.html` correctly renders connected accounts in a `<c-list>` with per-account remove forms, the empty-state message when no accounts are connected, and the "Add a Third-Party Account" section in all cases. `socialaccount/authentication_error.html` uses Cotton components (no `{% element %}` tags).

**Independent Test**: Render `connections.html` with a non-empty `form.accounts` and assert the provider badge and "Remove" button are present; render with an empty account list and assert the empty-state message and "Add a Third-Party Account" section are present. Render `authentication_error.html` and assert Cotton output with no element tags.

### Integration Tests for User Story 2

> **Write these tests FIRST. Confirm they FAIL before T009 (authentication_error.html fix).**

- [ ] T007 [P] [US2] Write/update integration tests in `tests/test_addons/test_allauth/test_social_connections_view.py` covering US2 acceptance scenarios:
  - `TestConnectionsWithAccounts`:
    - `test_connected_account_badge_present` — rendered HTML contains the provider brand name as a badge
    - `test_remove_button_present` — rendered HTML contains a submit button with text "Remove"
    - `test_account_pk_in_hidden_field` — rendered HTML contains `<input type="hidden" name="account"` with the account PK
    - `test_add_connections_section_present` — rendered HTML contains "Add a Third-Party Account"
  - `TestConnectionsEmpty`:
    - `test_no_accounts_message_present` — rendered HTML contains the empty-state message
    - `test_add_connections_section_still_present` — "Add a Third-Party Account" section is rendered even with no accounts
  - `TestAuthenticationErrorView` *(unchanged)*:
    - `test_renders_200` — GET `socialaccount_login_error` returns HTTP 200
    - `test_no_element_tags` — rendered HTML contains no `{% element` strings
    - `test_explanatory_text_present` — rendered HTML contains "An error occurred"

- [ ] T008 [US2] Confirm T007 tests FAIL before T009: run `poetry run pytest tests/test_addons/test_allauth/test_social_connections_view.py --no-cov -q`

### Implementation for User Story 2

- [X] T009 [P] [US2] Fix `dac/addons/allauth/templates/socialaccount/authentication_error.html` per `contracts/component-interface.md` §3:
  - Remove `{% load allauth %}` (no allauth tags remain after fix)
  - Drop `{% element h1 %}...{% endelement %}` entirely — the DAC `allauth/layouts/entrance.html` override renders the `{% block title %}` content as the page heading via `<c-entrance name="title">` slot; a second h1 would be semantically incorrect
  - Replace `{% element p %}...{% endelement %}` with `<c-text>{% trans "An error occurred while attempting to login via your third-party account." %}</c-text>`
  - Keep `{% block title %}{% trans "Third-Party Login Failure" %}{% endblock title %}` unchanged

- [ ] T010 [US2] Playwright MCP verification — open the authentication error page in a real browser, confirm the entrance layout renders the heading from the title slot and the explanatory paragraph appears as Cotton output

**Checkpoint**: User Stories 1 AND 2 are both functional and independently testable

- [ ] TVAL-2A Run `poetry run python manage.py check` — MUST pass
- [ ] TVAL-2B Run `poetry run pytest tests/test_addons/test_allauth/test_social_connections_view.py --no-cov -q` — all US1 and US2 tests MUST pass

---

## Phase 5: User Story 3 — Developer Verifies Templates via Automated Tests (Priority: P3)

**Goal**: All acceptance scenarios for US1–US3 are covered by passing integration tests and 9 persisted screenshot PNGs (3 states × 3 viewports).

**Independent Test**: `pytest tests/test_addons/test_allauth/test_social_connections_view.py --no-cov` passes with 0 failures. `docs/_static/{desktop,tablet,mobile}/connections-has-accounts.png`, `connections-no-accounts.png`, and `authentication-error.png` exist and correctly reflect the rendered UI.

### Implementation for User Story 3

- [ ] T011 [US3] Finalise `tests/test_addons/test_allauth/test_social_connections_view.py` — T003 and T007 write the core scenario tests; this task adds the finishing touches:
  - Add module-level docstring describing what is covered, which spec scenarios are targeted, and the test design pattern (client-based HTTP vs Cotton rendering)
  - Add tests for spec edge cases not covered by T003/T007:
    - Multiple social accounts from the same provider — each appears as its own list item with its own "Remove" button
    - No social providers configured — the "Add a Third-Party Account" card renders without error
    - Form re-render on submission failure — page renders without server error (template handles form errors inline via Cotton form components)

- [ ] T012 [P] [US3] Add pytest-playwright E2E workflow test to `screenshots/test_social_connections_screenshots.py` (or a separate `tests/test_addons/test_allauth/test_social_connections_e2e.py`) covering the disconnect workflow end-to-end per Principle VIII:
  - Log in as a user with 1 connected social account
  - Navigate to `socialaccount_connections` URL
  - Click the "Remove" button for the connected account
  - Assert the page redirects (or re-renders) and the disconnected account no longer appears in the list
  - This verifies the POST → `ConnectionsView` → `DisconnectForm.save()` → redirect flow at the browser level

- [X] T013 [P] [US3] Write screenshot tests in `screenshots/test_social_connections_screenshots.py` covering 3 page states × 3 viewports = 9 PNGs:
  - `connections-has-accounts` — `socialaccount_connections` URL, authenticated user with ≥1 social account connected
  - `connections-no-accounts` — `socialaccount_connections` URL, authenticated user with 0 social accounts
  - `authentication-error` — `socialaccount_login_error` URL (confirmed allauth URL name; unauthenticated or error redirect)
  - Use `@pytest.mark.parametrize` or a viewport fixture to cover desktop (1440×900), tablet (768×1024), mobile (390×844)
  - Save to `docs/_static/{desktop,tablet,mobile}/<slug>.png` following the established `save_screenshot` fixture pattern

- [ ] T014 [US3] Run screenshot tests and commit the 9 generated PNGs:

  ```
  poetry run pytest screenshots/test_social_connections_screenshots.py -v
  ```

  Verify all 9 files are created under `docs/_static/`

- [ ] T015 [US3] Agent visual inspection — open each of the 9 generated PNG files and confirm the rendered output matches acceptance criteria: DAC layout visible, "Connected" badge + "Remove" button present for connected provider in has-accounts state, all providers rendered as connect buttons in no-accounts state (no empty-state message), entrance layout with heading in authentication-error state (Principle XIII NON-NEGOTIABLE)

**Checkpoint**: All three user stories are implemented, tested, and visually verified

- [ ] TVAL-3A Run `poetry run pytest tests/test_addons/test_allauth/test_social_connections_view.py --no-cov -v` — MUST pass with 0 failures
- [ ] TVAL-3B Run `poetry run pytest screenshots/test_social_connections_screenshots.py -v` — MUST pass; 9 PNGs generated
- [ ] TVAL-3C Run E2E disconnect workflow test: `poetry run pytest tests/test_addons/test_allauth/test_social_connections_e2e.py -v` (or equivalent) — MUST pass

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Linting, final grep verification, full suite sign-off

- [ ] T016 [P] Run djlint on all three modified templates and fix any violations:

  ```
  poetry run djlint dac/addons/allauth/templates/socialaccount/base_manage.html \
                    dac/addons/allauth/templates/socialaccount/connections.html \
                    dac/addons/allauth/templates/socialaccount/authentication_error.html \
                    --reformat
  ```

- [ ] T017 [P] Grep verification — confirm zero `{% element %}` / `{% endelement %}` tags remain in any of the three modified files:

  ```powershell
  Select-String `
    -Path "dac/addons/allauth/templates/socialaccount/base_manage.html",
          "dac/addons/allauth/templates/socialaccount/connections.html",
          "dac/addons/allauth/templates/socialaccount/authentication_error.html" `
    -Pattern "{% element|{% endelement|{% slot"
  ```

  Expected: no output (zero matches)

- [ ] T018 Run full test suite to confirm no regressions across the broader test tree:

  ```
  poetry run pytest tests/ --no-cov -q
  ```

  MUST pass with 0 failures

---

## Implementation Strategy

**MVP Scope** (User Story 1 only, ~30 min):

1. T001 → T002 → TVAL-F1/F2 (base_manage.html fix, 5 min)
2. T003 → T004 (write US1 tests, observe fail)
3. T005 (rewrite connections.html, ~20 min)
4. T006 (Playwright MCP verify)
5. TVAL-1A/1B (validate)

After MVP, US2 (T007–T010) and US3 (T011–T014) can be completed incrementally.

**Total task count**: 26 tasks (18 implementation + 8 validation checkpoints)

| User Story | Tasks | Parallel opportunities |
|---|---|---|
| Foundational | T001–T002, TVAL-F1/F2 | None (sequential) |
| US1 | T003–T006, TVAL-1A/1B | T003/T004 independent of T005/T006 |
| US2 | T007–T010, TVAL-2A/2B | T007 [P] and T009 [P] can run in parallel |
| US3 | T011–T015, TVAL-3A/3B/3C | T012 [P] and T013 [P] can run in parallel with T011 |
| Polish | T016–T018 | T016 [P] and T017 [P] can run in parallel |
