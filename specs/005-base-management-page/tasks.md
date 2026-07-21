# Tasks: Base Management Page

**Input**: Design documents from `specs/005-base-management-page/`
**Prerequisites**: plan.md ✅, spec.md ✅, data-model.md ✅, contracts/ ✅, quickstart.md ✅

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies on incomplete tasks)
- **[Story]**: Which user story this task belongs to (US1–US3)
- Include exact file paths in descriptions

## Implementation Strategy

**MVP scope**: US1 (developer block contract tests) is the single deliverable — all 7
Cotton rendering tests in one module. US2 and US3 tests are written alongside US1
because they exercise the same template and can share the same test module. The entire
spec is a single-phase test-only effort; `dac/base.html` is not modified.

**Key facts**:

- `dac/templates/dac/base.html` is already implemented and must NOT be modified
- `tests/test_components/` directory does not yet exist — must be created with `__init__.py`
- All tests use `cotton_render_string_soup` from `django-cotton-bs5` (per Principle I and the `cotton-test-components` skill); `Template()` and `render_to_string` are prohibited for Cotton component tests
- `dac/base.html` uses `{% block %}` tags, so each test renders a concrete minimal child template as an inline string
- The `account-center` URL is registered by `dac`; tests must use `settings.ROOT_URLCONF = "tests.urls"` (already provided by the `use_test_urls` autouse fixture in `tests/test_addons/test_allauth/conftest.py` — check whether a similar fixture is needed for `tests/test_components/`)
- No new Python code, models, migrations, URL patterns, views, or Cotton components are introduced

---

## Phase 1: Setup

**Purpose**: Create the `tests/test_components/` package so Cotton component tests have a home.

- [x] T001 Create `tests/test_components/__init__.py` (empty file) to register the directory as a Python package

---

## Phase 2: Foundational (N/A)

All shared infrastructure (`dac/base.html`, Cotton components, URL routing) is already in
place. No foundational tasks needed — user story implementation begins immediately in Phase 3.

---

## Phase 3: US1 — Developer Block Contract (Priority: P1) 🎯 MVP

**Goal**: Every public block in `dac/base.html` is verified by an automated Cotton rendering
test. A developer can confirm that extending the base and overriding any block produces the
documented output.

**Independent Test**: Running `pytest tests/test_components/test_dac_base.py --no-cov` passes
with 0 failures and covers all 7 acceptance scenarios from spec US1.

- [x] T002 [US1] Create `tests/test_components/test_dac_base.py` with all 7 Cotton rendering tests. Read the `cotton-test-components` skill at `.github/skills/cotton-test-components/SKILL.md` before writing any test. The file must contain:

  **Setup**: Import `pytest` and `cotton_render_string_soup` from `django_cotton_bs5.pytest`. Add a `@pytest.fixture(autouse=True)` that sets `settings.ROOT_URLCONF = "tests.urls"` so that `{% url "account-center" %}` resolves correctly (matching the pattern used in `tests/test_addons/test_allauth/conftest.py`).

  **Test helper**: Define a module-level helper `_render(settings, template_str)` that calls `cotton_render_string_soup(settings, template_str)` and returns the soup. Each test passes a minimal child template string like:

  ```
  {% extends "dac/base.html" %}{% load i18n %}
  ```

  with additional block overrides appended as needed.

  **Test 1 — `test_sidebar_injects_account_center_menu`** [US1, US2]:
  - Render a bare extend (no block overrides)
  - Assert `soup.find('aside', class_='app-sidebar') is not None` — the `<c-app.sidebar>` component renders an `<aside class="app-sidebar">` element; its presence confirms the sidebar block was overridden. Do NOT assert the menu name string `"Account Center Menu"` as text — that string is an internal flex_menu lookup key and is never emitted into the rendered HTML.

  **Test 2 — `test_breadcrumbs_root_item_present`** [US1, US2]:
  - Render a bare extend
  - Assert the rendered HTML contains an `<a>` element whose text is `"Account Center"` and whose `href` contains the account-center URL path (use `reverse("account-center")` or assert `href` is non-empty)

  **Test 3 — `test_title_block_empty_by_default`** [US1]:
  - Render a bare extend (no `title` block override)
  - `<c-mvp.toolbar>` renders its title `<h1>` only when the `title` slot is non-empty. Assert `soup.find('h1') is None` — confirming no heading was produced for an empty `title` block. (The `<c-slot name="title">` passes the empty block content as the `title` variable; `{% if title %}` in the component evaluates to False.)

  **Test 4 — `test_title_block_override_renders`** [US1]:
  - Render with `{% block title %}My Test Page{% endblock title %}`
  - Assert `soup.find('h1').get_text(strip=True) == 'My Test Page'` — `<c-mvp.toolbar>` renders the title slot content as an `<h1>` (default heading level 1) when non-empty.

  **Test 5 — `test_page_content_placeholder_default`** [US1, US3]:
  - Render a bare extend
  - Assert the rendered HTML contains the text `"Coming soon"` (the localised placeholder from `{% trans "Coming soon..." %}`)

  **Test 6 — `test_page_content_block_override_renders`** [US1]:
  - Render with `{% block page.content %}<p id="my-content">Hello</p>{% endblock page.content %}`
  - Assert an element with `id="my-content"` and text `"Hello"` is present in the rendered HTML

  **Test 7 — `test_breadcrumbs_block_override_extends_with_block_super`** [US1, US2]:
  - Render with:

    ```
    {% block page.breadcrumbs %}{{ block.super }}<c-navigation.breadcrumbs.item text="Sub Page" />{% endblock page.breadcrumbs %}
    ```

  - Assert the rendered HTML contains both `"Account Center"` and `"Sub Page"` as breadcrumb-related text

- [x] T003 [US1] Validate: run `poetry run pytest tests/test_components/test_dac_base.py --no-cov -v` and confirm all 7 tests pass. Also run `poetry run python manage.py check --settings=tests.settings` and confirm zero system check errors. Fix any failures before proceeding.

---

## Phase 4: US2 — Consistent Management UI (Priority: P2)

**Goal**: Two different sub-pages that extend `dac/base.html` both carry the Account Center
Menu in the sidebar and the "Account Center" root breadcrumb, confirming structural consistency.

**Independent Test**: Running `pytest tests/test_components/test_dac_base.py --no-cov -k "consistency"` passes. These tests share the same module as Phase 3.

- [x] T004 [US2] Add `test_two_subpages_share_sidebar_and_breadcrumb` to `tests/test_components/test_dac_base.py`:
  - Render two different child templates (one with `{% block title %}Page A{% endblock %}`, one with `{% block title %}Page B{% endblock %}`)
  - Assert both rendered outputs contain an `<aside class="app-sidebar">` element (sidebar present on every extending page)
  - Assert both rendered outputs contain an `<a>` element with text `"Account Center"` (root breadcrumb present on every extending page)
  - This is a single test function with two render calls, not two parallel tasks — they share the same file

- [x] T005 [US2] Add `test_real_account_center_page_renders_correctly` to `tests/test_components/test_dac_base.py`:
  - Render `{% extends "dac/account_center.html" %}` — this is the actual existing sub-page that extends `dac/base.html` with zero block overrides
  - Assert `<aside class="app-sidebar">` is present (sidebar injected)
  - Assert an `<a>` with text `"Account Center"` is present (breadcrumb present)
  - Assert the text `"Coming soon"` is present (default `page.content` placeholder)
  - This covers SC-001: verifying a real existing sub-page renders correctly

- [x] T006 [US2] Validate: run `poetry run pytest tests/test_components/test_dac_base.py --no-cov -v` and confirm all 9 tests pass (7 from Phase 3 + 2 from Phase 4).

---

## Phase 5: US3 — Template Structure Legibility (Priority: P3)

**Goal**: `dac/base.html` is verified to contain all required named blocks in the expected
positions, confirming structural legibility without rendering.

**Independent Test**: Running `pytest tests/test_components/test_dac_base.py --no-cov -k "structure"` passes.

- [x] T007 [US3] Add `test_all_required_blocks_present` to `tests/test_components/test_dac_base.py`:
  - Read the source of `dac/templates/dac/base.html` (use `pathlib.Path` or `django.template.loader.get_template().origin.name`)
  - Assert the source string contains each of the following block tags: `app.sidebar`, `content`, `breadcrumbs`, `page.breadcrumbs`, `page.content-wrapper`, `title`, `page.content`

- [x] T008 [US3] Add `test_page_breadcrumbs_default_has_one_item` to `tests/test_components/test_dac_base.py`:
  - Render a bare extend
  - Assert exactly one `<c-navigation.breadcrumbs.item>` equivalent element (or its rendered `<li>` / `<a>`) labelled `"Account Center"` appears in the breadcrumb region with a non-empty `href`

- [x] T009 [US3] Add `test_card_stack_wraps_page_content` to `tests/test_components/test_dac_base.py`:
  - Render a bare extend
  - `<c-card.stack>` renders as `<div class="d-flex flex-column gap-3">`. Assert `soup.find('div', class_='d-flex') is not None` — confirming the card stack structural wrapper is present around the content area (FR-009). This is structurally distinct from Test 5 which only checks the text content inside the card stack.

- [x] T010 [US3] Validate: run `poetry run pytest tests/test_components/test_dac_base.py --no-cov -v` and confirm all 12 tests pass (7 Phase 3 + 2 Phase 4 + 3 Phase 5).

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final validation, linting, and mark-up.

- [x] T011 Run `poetry run pytest tests/ --no-cov -q` and confirm the full test suite passes with no regressions
- [x] T012 Run `poetry run python manage.py check --settings=tests.settings` and confirm no system check errors
- [x] T013 Mark all tasks complete in this file and update `specs/005-base-management-page/plan.md` if any implementation decisions differed from the plan

---

## Dependencies

```
T001 (setup) → T002 (US1 tests) → T003 (validate US1)
                                 → T004, T005 (US2 tests) → T006 (validate US2)
                                 → T007, T008, T009 (US3 tests) → T010 (validate US3)
T010 → T011 → T012 → T013
```

## Parallel Execution

Within Phase 4 after T003 is complete:

- T004 and T005 write to the same file — write them in the same editing session, not as parallel file operations
- T007, T008, and T009 write to the same file — write them in the same editing session
- Validation tasks (T003, T006, T010) must run after their respective write tasks
