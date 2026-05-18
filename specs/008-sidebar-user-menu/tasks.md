# Tasks: Sidebar User Menu Component

**Propagated**: 2026-05-18 — Updated from spec.md refinements (zero-config redesign; inline template-string tests; screenshot tasks removed).

**Input**: Design documents from `specs/008-sidebar-user-menu/`
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, contracts/component-interface.md ✅, quickstart.md ✅

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies on incomplete tasks)
- **[Story]**: Which user story this task belongs to (US1–US5)
- Tests are **written during US5** phase (US5 is the explicit testing story)

## Path Conventions

- **Cotton component**: `dac/templates/cotton/dac/user_menu.html` (snake_case per `COTTON_SNAKE_CASED_NAMES = True`)
- **Component tests**: `tests/test_components/test_dac_base.py` (EDIT — add `TestDacUserMenu`)
- ~~**Screenshot tests**: `screenshots/test_user_menu_screenshots.py` (NEW)~~ — **[REMOVED]** screenshots are out of scope
- ~~**Screenshot artifacts**: `docs/_static/{desktop,tablet,mobile}/`~~ — **[REMOVED]**
- Full component template: `specs/008-sidebar-user-menu/contracts/component-interface.md`

---

## Phase 1: Setup

No project setup required. `dac/templates/cotton/dac/` already exists; no new apps,
migrations, settings keys, or Python files needed. Proceed directly to Phase 2.

---

## Phase 2: Foundational — Component Scaffold

**Purpose**: Create the component file with its prop declarations and auth guard.
All user-story phases add content inside this scaffold.

**⚠️ CRITICAL**: All subsequent phases write content inside this file. Complete T001
before starting US1–US4 implementation.

- [X] T001 Create `dac/templates/cotton/dac/user-menu.html` with the component scaffold:
  `{% load i18n %}`, then `<c-vars>` declaring all 7 props with Python-typed boolean
  defaults (`:show_account_center="True"`, `:show_logout="True"`), then an outer
  `{% if request.user.is_authenticated %}` guard wrapping a
  `<c-dropdown direction="up" min_width="100%" dropdown_class="dac-user-menu w-100 {{ class }}">`.
  Leave the `<c-slot name="button">` and panel body empty as placeholders for US1/US2.

  Reference `contracts/component-interface.md` → "Full Component Template" for the
  exact `<c-vars>` declaration:

  ```django
  {% load i18n %}
  <c-vars display_name=""
          subtitle=""
          avatar_url=""
          avatar_size="sm"
          :show_account_center="True"
          :show_logout="True"
          class="" />
  {% if request.user.is_authenticated %}
    <c-dropdown direction="up"
                min_width="100%"
                dropdown_class="dac-user-menu w-100 {{ class }}">
      {# Trigger and panel content added in US1/US2 phases #}
    </c-dropdown>
  {% endif %}
  ```

- [X] TVAL-1 Run `python manage.py check` — MUST pass with no errors before proceeding.

---

## Phase 3: User Story 1 — Developer Drops User Menu into the Sidebar Footer (P1)

**Goal**: Authenticated users see a trigger button at the sidebar bottom showing their
avatar (`<c-avatar size="sm" />`), username (`{{ request.user }}`), and email
(`{{ request.user.email }}`). Component renders nothing for anonymous users.

**Note (2026-05-18 refinement)**: No `display_name` or `subtitle` props exist.
All user data is sourced from `request.user` directly.

**Independent Test**:

```bash
poetry run pytest tests/test_components/test_dac_base.py::TestDacUserMenu::test_authenticated_user_renders_trigger --no-cov -v
```

- [X] T002 [US1] Implement the trigger button in `dac/templates/cotton/dac/user_menu.html`.
  **Note (2026-05-18 refinement)**: Implemented using `<c-button>` (not a raw `<button>`),
  with `data-bs-toggle="dropdown"`, `aria-expanded="false"`, `aria-haspopup="true"`.
  Inside: `<c-avatar size="sm" />` (no `src`), then a flex span with
  `{{ request.user }}` (username) and `{{ request.user.email }}` (muted secondary line).

  ~~Original plan used a raw `<button class="btn btn-link dac-user-menu__trigger ...">` with
  `{{ display_name }}` and conditional `{{ subtitle }}`. Both props removed.~~

- ~~[ ] TPLAY-3 [US1] Playwright MCP verification~~ **[REMOVED]** — Playwright/E2E testing is out of scope for this component.

- [X] TVAL-2 Run `python manage.py check ; poetry run pytest tests/test_components/ --no-cov -q` —
  MUST pass before proceeding to Phase 4.

---

## Phase 4: User Story 2 — End User Opens the Dropup and Navigates (P1)

**Goal**: Clicking the trigger opens a dropup panel with an Account Center link and a logout
button. Both URLs degrade gracefully when not registered.

**Note (2026-05-18 refinement)**: The non-clickable user-info header row was removed from the
panel in the zero-config redesign. User info is only shown in the trigger button now.

**Independent Test**:

```bash
poetry run pytest tests/test_components/test_dac_base.py::TestDacUserMenu::test_account_center_link_present tests/test_components/test_dac_base.py::TestDacUserMenu::test_logout_form_present --no-cov -v
```

- ~~[X] T003 [US2] Implement the panel header `<li>` row~~ **[REMOVED]** — The non-clickable user-info
  header inside the dropdown panel was removed in the zero-config redesign (2026-05-18).
  User information (avatar, username, email) is now shown exclusively in the trigger button;
  the dropdown panel opens directly with the Account Center link as its first item.

- [X] T004 [US2] Implement the Account Center link in `dac/templates/cotton/dac/user_menu.html`.
  **Note (2026-05-18 refinement)**: Implemented using `{% url "account-center" %}` inline
  (no `as var` assignment) since the URL is always present when `dac.urls` is included.
  Uses `<c-dropdown.item href="..." text="Account Center" icon="grid" />`.

  ~~Original plan used `{% url 'account-center' as account_center_url %}{% if account_center_url %}...
  {% endif %}` assignment form.~~

- [X] T005 [US2] Implement the logout action in `dac/templates/cotton/dac/user_menu.html`.
  **Note (2026-05-18 refinement)**: Implemented using `<c-dropdown.item type="submit"
  form="logoutForm" ...>` linked to a hidden `<form id="logoutForm" method="post"
  action="{{ logout_url }}">` placed below the `</c-dropdown>` tag (outside the `<ul>`).
  The `{% url 'account_logout' as logout_url %}` assignment form still suppresses
  `NoReverseMatch`; the form is only rendered `{% if logout_url %}`.

  ~~Original plan used a raw `<li><form method="post">...<button type="submit">` inside
  the dropdown body. Replaced with `<c-dropdown.item form="...">` approach.~~

- ~~[ ] TPLAY-4 [US2] Playwright MCP verification~~ **[REMOVED]** — Playwright/E2E testing is out of scope.

- [X] TVAL-3 Run `python manage.py check ; poetry run pytest tests/test_components/ --no-cov -q` —
  MUST pass before proceeding to Phase 5.

---

## Phase 5: User Story 3 — Developer Adds Custom Menu Items (P2)

**Goal**: Slot content passed inside `<c-dac.user-menu>` renders between the Account
Center link and the logout button.

**Independent Test**:

```bash
poetry run pytest tests/test_components/test_dac_base.py::TestDacUserMenu::test_custom_slot_item_appears_before_logout --no-cov -v
```

- [X] T006 [US3] Add `{{ slot }}` between the Account Center item and the logout divider in
  `dac/templates/cotton/dac/user_menu.html`. Position: immediately after the
  Account Center block and before `<c-dropdown.divider />`.

  ```django
  {# Developer's custom items #}
  {{ slot }}
  ```

- ~~[ ] TPLAY-5 [US3] Playwright MCP verification~~ **[REMOVED]** — Playwright/E2E testing is out of scope.

- [X] TVAL-4 Run `python manage.py check ; poetry run pytest tests/test_components/ --no-cov -q` —
  MUST pass before proceeding to Phase 6.

---

## ~~Phase 6: User Story 4 — Developer Overrides Default Menu Items (P3)~~ **[REMOVED]**

~~**Goal**: `:show_account_center="False"` suppresses the Account Center link;
`:show_logout="False"` suppresses the divider + logout form. Both can be combined.~~

**Removed (2026-05-18)**: US4 was removed from the spec in the zero-config redesign.
The `show_account_center` and `show_logout` props were never implemented; the component
is intentionally opinionated — items are always shown when their URLs resolve.

- ~~[X] T007 [US4]~~ **[REMOVED]** — `show_account_center` prop was never implemented.
- ~~[X] T008 [US4]~~ **[REMOVED]** — `show_logout` prop was never implemented.
- ~~[ ] TPLAY-6 [US4]~~ **[REMOVED]** — Playwright/E2E out of scope.
- ~~[X] TVAL-5~~ **[REMOVED]** — Phase removed.

---

## Phase 7: User Story 5 — Developer Verifies via Automated Tests (P3)

**Goal**: `TestDacUserMenu` class in `tests/test_components/test_dac_base.py` covers
all unit tests from spec.md US5 and runs in isolation. Tests compose Cotton template
strings inline — no external template files.

**Independent Test**:

```bash
poetry run pytest tests/test_components/test_dac_base.py::TestDacUserMenu --no-cov -v
```

Expected: all methods pass, 0 failures.

**⚠️ TEST-FIRST (Constitution Principle I)**: Write T009–T012 first and confirm they
fail against the missing component _before_ running T001–T008. Reorder your workflow:

1. Write the full test class skeleton (T009–T012) → run → observe failures
2. Implement T001–T008 → run → observe all tests turn green

- [X] T009 [US5] Add `TestDacUserMenu` class to `tests/test_components/test_dac_base.py`.
  **Note (2026-05-18 refinement)**: Uses `cotton_render_string_soup_authenticated` fixture
  (authenticated user mock with `__str__` returning `"testuser"`). All tests pass `"<c-dac.user-menu />"`
  as an inline template string — no external template files. Actual tests implemented:

  - `test_anonymous_user_renders_nothing` — asserts no `div.dac-user-menu` for anonymous user
  - `test_authenticated_user_renders_component` — asserts `div.dac-user-menu` wrapper present
  - `test_username_in_trigger` — asserts `"testuser"` in trigger button text
  - `test_email_in_trigger` — asserts `"test@example.com"` in muted span in trigger
  - `test_trigger_has_aria_attrs` — asserts `aria-expanded="false"` and `aria-haspopup="true"`
  - `test_username_has_truncate_class` — asserts `span.text-truncate` contains username

  ~~Original plan included `test_display_name_in_trigger`, `test_subtitle_present`,
  `test_subtitle_absent`, `test_authenticated_user_renders_trigger` (different selector).
  All replaced by the above tests matching the zero-config redesign.~~

- [X] T010 [US5] Add avatar test to `TestDacUserMenu`.
  **Note (2026-05-18 refinement)**: Single test `test_avatar_component_present_in_trigger`
  — asserts `span.avatar` is present inside the trigger button. The component uses
  `<c-avatar size="sm" />` with no `src`; avatar URL resolution is delegated entirely
  to `<c-avatar>`.

  ~~Original plan included `test_avatar_with_url_shows_img` (pass `avatar_url` prop;
  assert `img.avatar-img`) and `test_avatar_without_url_shows_svg` (assert `<svg>`).
  Both removed: no `avatar_url` prop exists; testing `<c-avatar>` internals is out of scope.~~

- [X] T011 [US5] Add menu item presence tests to `TestDacUserMenu` in `tests/test_components/test_dac_base.py`:

  - `test_account_center_link_present` — assert dropdown contains `<a>` with `href`
    containing `/account-center/`
  - `test_logout_form_present` — assert dropdown contains `<form method="post">`
    targeting the logout URL
  - `test_account_center_link_absent_when_url_not_registered` — render using a URL
    conf that does NOT include the `account-center` route; assert no `<a>` with
    `href` containing `/account-center/` appears (graceful degradation, FR-005)
  - `test_logout_form_absent_when_url_not_registered` — render using a URL conf that
    does NOT include the `account_logout` route; assert no `<form method="post">`
    appears (graceful degradation, FR-006)

- [X] T012 [US5] Add custom-slot test to `TestDacUserMenu`.
  **Note (2026-05-18 refinement)**: Implements `test_custom_slot_item_appears_before_logout`
  only — renders inline template string with `<c-dac.user-menu>` wrapping a
  `<c-dropdown.item text="Settings" href="#" />` and asserts the Settings link appears
  before the logout `<form method="post">` in the rendered HTML.

  ~~Original plan included `test_show_account_center_false` and `test_show_logout_false`.
  Both removed: `show_account_center` and `show_logout` props were never implemented
  (US4 removed from spec).~~

- [X] TVAL-6 [US5] Run full test suite — `poetry run pytest tests/ --no-cov -q` — MUST pass
  with 0 failures. **190 tests pass as of 2026-05-18.**

**Checkpoint**: `pytest tests/test_components/test_dac_base.py::TestDacUserMenu` shows
all 12 methods green (updated from 16 in original plan, due to zero-config redesign).
No regressions in other test classes.

---

## ~~Final Phase: Screenshots & Polish~~ **[REMOVED]**

**Removed (2026-05-18)**: Screenshot tests are explicitly out of scope for this component
per spec.md refinement. No Playwright, no live-server tests, no PNG artifacts.

- ~~[X] T013~~ **[REMOVED]** — Screenshot module never created; out of scope.
- ~~[X] T014~~ **[REMOVED]** — Screenshot run never performed; out of scope.

---

## Dependencies

```
T001 (scaffold)
  └── T002 [US1] trigger
        └── T004 [US2] account center link   (T003 panel header — REMOVED)
              └── T005 [US2] logout form
                    └── T006 [US3] custom slot
                          └── T009–T012 [US5] tests
                                   (T007, T008 show_* guards — REMOVED; US4 removed)
                                   (T013–T014 screenshots — REMOVED; out of scope)
```

US1 (T002) and US2 (T004–T005) can be considered independently testable checkpoints
within the same phase — US1 covers the trigger; US2 covers the panel content.

---

## Parallel Execution Opportunities

Within Phase 7 (US5 tests), once `TestDacUserMenu` class is created (T009), the
following test groups can be added in any order since they are independent test
methods in the same class:

```
T010 (avatar test)     ─┬─ all independent after T009
T011 (link tests)      ─┤
T012 (slot test)       ─┘
```

~~Within the final phase, T013 (create screenshot file) must precede T014 (run + commit).~~ **[REMOVED]**

---

## Implementation Strategy

**MVP Scope** (deliver first): Phase 2 + Phase 3 + Phase 4 (T001–T005)
This gives a fully functional `<c-dac.user-menu>` component with trigger, panel,
Account Center link, and logout — all a developer needs to integrate immediately.

**Incremental additions**:

1. T006 (custom slot) — needed for any project with additional menu items
2. T007–T008 (suppression) — needed for projects with custom logout flows
3. T009–TVAL-6 (tests) — required before merge per Constitution Principle VIII
4. T013–T014 (screenshots) — required before merge per Constitution Principle XIII

**Single-file implementation**: All of T001–T008 modify the same file
(`dac/templates/cotton/dac/user-menu.html`). Use the full template in
`contracts/component-interface.md` as the authoritative reference — the contract
already reflects all US1–US4 decisions and can be used directly as the final file
content, skipping the incremental phases if preferred.
