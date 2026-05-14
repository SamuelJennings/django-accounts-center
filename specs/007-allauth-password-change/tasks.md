# Tasks: Allauth Password Change Templates

**Input**: Design documents from `specs/007-allauth-password-change/`
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, contracts/component-interface.md ✅, quickstart.md ✅

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3, US4)
- Tests are **written during implementation** alongside each template rewrite

## Path Conventions

- **Addon templates**: `dac/addons/allauth/templates/account/`
- **Integration tests**: `tests/test_addons/test_allauth/test_password_change_view.py` (new)
- **Screenshot tests**: `screenshots/test_password_change_screenshots.py` (new)
- **Screenshot artifacts**: `docs/_static/{desktop,tablet,mobile}/`

---

## Phase 1: Setup

No project setup required. All files exist; no migrations, no new Python files, no new components. Proceed directly to Phase 2.

---

## Phase 2: Foundational — Rewrite Reauthenticate Base Template

**Purpose**: Replace all `{% element %}` tags in `base_reauthenticate.html` so the reauthenticate entrance shell is Cotton-native. This is foundational because `reauthenticate.html` (and the out-of-scope MFA reauthenticate templates) extend it.

**⚠️ CRITICAL**: `reauthenticate.html` (US3) depends on this base template. Complete this phase first.

- [X] T001 Rewrite `dac/addons/allauth/templates/account/base_reauthenticate.html` to use Cotton components throughout

  Replace every `{% element %}` / `{% endelement %}` tag with the Cotton equivalent per `contracts/component-interface.md`:

  - `{% element h1 %}{% trans "Confirm Access" %}{% endelement %}` → moved into `{% block title %}{% trans "Confirm Access" %}{% endblock %}` (the entrance layout renders this as the page heading; do NOT add a visible `<h1>` tag inside `{% block content %}`)
  - `{% element p %}…{% endelement %}` → `<c-entrance.section text="{% trans \"Please reauthenticate to safeguard your account.\" %}">` (the `text=` attribute renders the introductory paragraph)
  - `{% element hr %}` → `<c-card.divider text="{% trans "Alternative options" %}">`
  - `{% element h2 %}` → removed (divider text provides the label)
  - `{% element button_group %}` → `<c-button.stack>`
  - `{% element button href=alt.url tags="primary,outline" %}` → `<c-button href="{{ alt.url }}" variant="outline-primary" text="{{ alt.description }}" />`
  - Remove `{% load allauth %}` (no longer needed)
  - Keep `{% block reauthenticate_content %}{% endblock %}` inside the section wrapper

  Target structure:

  ```django
  {% extends "account/base_entrance.html" %}
  {% load i18n %}

  {% block title %}{% trans "Confirm Access" %}{% endblock title %}

  {% block content %}
    <c-entrance.section text="{% trans "Please reauthenticate to safeguard your account." %}">
      {% block reauthenticate_content %}{% endblock %}
    </c-entrance.section>
    {% if reauthentication_alternatives %}
      <c-card.divider text="{% trans "Alternative options" %}" />
      <c-button.stack>
        {% for alt in reauthentication_alternatives %}
          <c-button href="{{ alt.url }}" variant="outline-primary" text="{{ alt.description }}" />
        {% endfor %}
      </c-button.stack>
    {% endif %}
  {% endblock content %}
  ```

- [X] TVAL-0 Validate `base_reauthenticate.html` after T001 — Principle I requires a validation checkpoint after every template-modifying phase

  ```bash
  python manage.py check --settings=tests.settings
  poetry run pytest tests/test_addons/test_allauth/ --no-cov -q
  ```

  Expected: zero system-check errors; existing allauth tests all pass (no regressions in MFA reauthenticate or other entrance templates).

**Checkpoint**: `base_reauthenticate.html` has zero `{% element %}` tags, TVAL-0 passes. MFA reauthenticate templates still work (they only override `{% block reauthenticate_content %}`). US3 implementation can now begin.

---

## Phase 3: User Story 1 — Developer Wires Password Management Templates into the DAC Layout (Priority: P1)

**Goal**: `password_change.html` and `password_set.html` render their form content inside `{% block page.content %}` (not `{% block content %}`), placing forms inside the DAC card-stack with the Account Center sidebar and breadcrumb trail present.

**Independent Test**:

```bash
poetry run pytest tests/test_addons/test_allauth/test_password_change_view.py::TestPasswordChangeView tests/test_addons/test_allauth/test_password_change_view.py::TestPasswordSetView --no-cov -v
```

### Implementation for User Story 1

> **Design-First (Principle I)**: Write T004 tests *before* applying the template rewrites in T002/T003. Draft the test assertions, confirm they fail against the current templates, then do the rewrites to make them pass.

- [X] T004 [P] [US1] Write integration tests for US1 in `tests/test_addons/test_allauth/test_password_change_view.py` — **write these first so they fail before the template rewrites**

  Cover the following acceptance scenarios from spec.md:

  - `TestPasswordChangeView.test_renders_200_for_authenticated` — GET returns 200 with an authenticated user
  - `TestPasswordChangeView.test_no_element_tags_in_output` — rendered HTML contains no `{% element %}` / `{% endelement %}` tags
  - `TestPasswordChangeView.test_has_page_content_block` — response contains the DAC breadcrumb trail (checks for "Account Center" root)
  - `TestPasswordChangeView.test_has_change_password_breadcrumb` — "Change Password" appears in the breadcrumb output
  - `TestPasswordChangeView.test_has_submit_button` — `type="submit"` button is present
  - `TestPasswordChangeView.test_has_forgot_password_link` — link to `account_reset_password` is present
  - `TestPasswordSetView.test_renders_200_for_authenticated` — GET returns 200 with an authenticated user (no password)
  - `TestPasswordSetView.test_no_element_tags_in_output` — rendered HTML contains no `{% element %}` tags
  - `TestPasswordSetView.test_has_set_password_breadcrumb` — "Set Password" appears in the breadcrumb output
  - `TestPasswordSetView.test_has_submit_button` — submit button is present
  - `TestPasswordSetView.test_no_forgot_password_link` — no link to `account_reset_password` on set-password page
  - `TestBaseManagePasswordView.test_base_manage_password_inherits_dac_base` — render `base_manage_password.html` directly and assert DAC sidebar/breadcrumb structure is present (verifies the inheritance chain is unbroken)

  Use `client.force_login(user)` for authentication. `password_set` requires a user with no usable password (`set_unusable_password()`). Confirm these tests **FAIL** before proceeding to T002+T003.

- [X] T002 [P] [US1] Rewrite `dac/addons/allauth/templates/account/password_change.html` to use `{% block page.content %}`, add `{% block page.breadcrumbs %}` override, and replace all `{% element %}` tags with Cotton components

  Target structure (from `contracts/component-interface.md`):

  ```django
  {% extends "account/base_manage_password.html" %}
  {% load i18n %}

  {% block title %}{% trans "Change Password" %}{% endblock title %}

  {% block page.breadcrumbs %}
    {{ block.super }}
    <c-breadcrumbs.item text="{% trans "Change Password" %}" />
  {% endblock page.breadcrumbs %}

  {% block page.content %}
    <c-form.card method="post"
                 action="{% url 'account_change_password' %}"
                 :form-obj="form">
      {{ redirect_field }}
      <c-slot name="actions">
        <c-button.stack>
          <c-button type="submit"
                    variant="primary"
                    text="{% trans "Change Password" %}" />
          <a href="{% url 'account_reset_password' %}">{% trans "Forgot Password?" %}</a>
        </c-button.stack>
      </c-slot>
    </c-form.card>
  {% endblock page.content %}
  ```

  Key changes from current template:
  - Remove `{% load allauth %}` (no longer needed)
  - `{% block content %}` → `{% block page.content %}` (critical fix)
  - Add `{% block page.breadcrumbs %}` with "Change Password" leaf item
  - `{% element h1 %}` → removed (management shell provides page title)
  - `{% element form … %}` + `{% slot body %}` + `{% slot actions %}` → `<c-form.card>` with `<c-slot name="actions">`
  - `{% element fields form=form %}` → `:form-obj="form"` attribute on `<c-form.card>`
  - `{% element button %}` → `<c-button type="submit" variant="primary" …>`

- [X] T003 [P] [US1] Rewrite `dac/addons/allauth/templates/account/password_set.html` to use `{% block page.content %}`, add `{% block page.breadcrumbs %}` override, and replace all `{% element %}` tags with Cotton components

  Target structure:

  ```django
  {% extends "account/base_manage_password.html" %}
  {% load i18n %}

  {% block title %}{% trans "Set Password" %}{% endblock title %}

  {% block page.breadcrumbs %}
    {{ block.super }}
    <c-breadcrumbs.item text="{% trans "Set Password" %}" />
  {% endblock page.breadcrumbs %}

  {% block page.content %}
    <c-form.card method="post"
                 action="{% url 'account_set_password' %}"
                 :form-obj="form">
      {{ redirect_field }}
      <c-slot name="actions">
        <c-button.stack>
          <c-button type="submit"
                    variant="primary"
                    text="{% trans "Set Password" %}" />
        </c-button.stack>
      </c-slot>
    </c-form.card>
  {% endblock page.content %}
  ```

  Same changes as T002 but for the set-password flow. No "Forgot Password?" link.

- [X] TVAL-1 [US1] Run `python manage.py check --settings=tests.settings` — MUST pass with no errors

- [X] TVAL-2 [US1] Run `poetry run pytest tests/test_addons/test_allauth/test_password_change_view.py::TestPasswordChangeView tests/test_addons/test_allauth/test_password_change_view.py::TestPasswordSetView tests/test_addons/test_allauth/test_password_change_view.py::TestBaseManagePasswordView --no-cov -v` — MUST pass

- [X] TPWVI-1 [US1] Open the change-password and set-password pages in the Playwright MCP browser and visually confirm:
  - DAC Account Center sidebar is visible on both pages
  - Breadcrumb trail reads "Account Center › Change Password" (and "Set Password" respectively)
  - `<c-form.card>` renders inside the card-stack (not a raw unstyled form)
  - All form fields are rendered (current password, new password, confirmation for change; new password, confirmation for set)
  - "Change Password" submit button is visible; "Forgot Password?" link is below it
  - "Set Password" submit button is visible; no "Forgot Password?" link

**Checkpoint**: US1 complete when TVAL-1, TVAL-2, and TPWVI-1 all pass.

---

## Phase 4: User Story 2 — End User Changes or Sets Password with a Consistent UI (Priority: P2)

**Goal**: An end user on either management page sees all expected form fields, submit button, and (on change-password) the "Forgot Password?" link — all rendered within the DAC card-stack via Cotton components.

**Independent Test**:

```bash
poetry run pytest tests/test_addons/test_allauth/test_password_change_view.py::TestPasswordChangeFormFields tests/test_addons/test_allauth/test_password_change_view.py::TestPasswordSetFormFields --no-cov -v
```

### Implementation for User Story 2

- [X] T005 [US2] Write end-user-focused integration tests for US2 in `tests/test_addons/test_allauth/test_password_change_view.py`

  Extend the file from T004 with the following test classes:

  - `TestPasswordChangeFormFields`:
    - `test_form_has_old_password_field` — `name="oldpassword"` (or `type="password"`) present in rendered HTML
    - `test_form_has_new_password_fields` — `name="password1"` and `name="password2"` present
    - `test_submit_button_text_is_change_password` — button text is "Change Password"
    - `test_no_element_tags_present` — no raw `{% element %}` strings in rendered output
  - `TestPasswordSetFormFields`:
    - `test_form_has_new_password_fields` — `name="password1"` and `name="password2"` present (no `oldpassword` field)
    - `test_submit_button_text_is_set_password` — button text is "Set Password"
    - `test_no_element_tags_present` — no raw `{% element %}` strings in rendered output

- [X] TVAL-3 [US2] Run `poetry run pytest tests/test_addons/test_allauth/test_password_change_view.py::TestPasswordChangeFormFields tests/test_addons/test_allauth/test_password_change_view.py::TestPasswordSetFormFields --no-cov -v` — MUST pass

**Checkpoint**: US2 complete when TVAL-3 passes.

---

## Phase 5: User Story 3 — Reauthentication Gate Renders as Cotton Entrance Page (Priority: P2)

**Goal**: `reauthenticate.html` fills `{% block reauthenticate_content %}` with Cotton form components, producing a password field and "Confirm" button with no `{% element %}` tags.

**Independent Test**:

```bash
poetry run pytest tests/test_addons/test_allauth/test_password_change_view.py::TestReauthenticateView --no-cov -v
```

### Implementation for User Story 3

- [X] T006 [US3] Rewrite `dac/addons/allauth/templates/account/reauthenticate.html` to fill `{% block reauthenticate_content %}` with Cotton components (depends on T001 — foundational base template)

  Target structure:

  ```django
  {% extends "account/base_reauthenticate.html" %}
  {% load i18n %}

  {% block reauthenticate_content %}
    <c-form method="post"
            action="{% url 'account_reauthenticate' %}"
            :form-obj="form">
      {{ redirect_field }}
      <c-button.stack>
        <c-button type="submit"
                  variant="primary"
                  text="{% trans "Confirm" %}" />
      </c-button.stack>
    </c-form>
  {% endblock %}
  ```

  Key changes from current template:
  - Remove `{% load allauth %}` (no longer needed)
  - `{% element p %}Enter your password:{% endelement %}` → removed (field label rendered by `<c-form>`)
  - `{% element form … %}` + `{% slot body %}` + `{% slot actions %}` → `<c-form>` with inline `<c-button.stack>`
  - `{% element fields form=form unlabeled=True %}` → `:form-obj="form"` on `<c-form>`
  - `{% element button … %}` → `<c-button type="submit" variant="primary" …>`

- [X] T007 [US3] Write integration tests for US3 in `tests/test_addons/test_allauth/test_password_change_view.py`

  Add `TestReauthenticateView` class:

  - `test_renders_200_for_authenticated` — GET `account_reauthenticate` returns 200 with authenticated user
  - `test_no_element_tags_in_output` — rendered HTML contains no `{% element %}` / `{% endelement %}` tags
  - `test_has_password_field` — `type="password"` input is present in rendered output
  - `test_has_confirm_button` — submit button with text "Confirm" is present
  - `test_no_alternatives_section_by_default` — "Alternative options" section is absent when `reauthentication_alternatives` is not set
  - `test_alternatives_section_when_provided` — "Alternative options" section appears when the template is rendered with a mock `reauthentication_alternatives` list

    Use `cotton_render_string` from `django-cotton-bs5` (see `cotton-test-components` skill) — do **NOT** use `render_to_string` (Principle I prohibits it for Cotton tests). The `account_reauthenticate` URL does not expose a configurable alternatives list at runtime, so a direct URL test is not feasible for this state; `cotton_render_string` is the correct approach.

    ```python
    from django_cotton_bs5.test import cotton_render_string

    class MockAlternative:
        url = "/accounts/2fa/authenticate/"
        description = "Use authenticator code"

    def test_alternatives_section_when_provided(self):
        html = cotton_render_string(
            '{% extends "account/reauthenticate.html" %}',
            context={"form": ReauthenticateForm(), "reauthentication_alternatives": [MockAlternative()]},
        )
        assert "Alternative options" in html
        assert "/accounts/2fa/authenticate/" in html
    ```

- [X] TVAL-4 [US3] Run `python manage.py check --settings=tests.settings` — MUST pass with no errors

- [X] TVAL-5 [US3] Run `poetry run pytest tests/test_addons/test_allauth/test_password_change_view.py::TestReauthenticateView --no-cov -v` — MUST pass

- [X] TPWVI-2 [US3] Open `/accounts/reauthenticate/` in the Playwright MCP browser and visually confirm:
  - The entrance-style layout is rendered (no DAC sidebar — this is an entrance page)
  - "Confirm Access" heading is visible
  - "Please reauthenticate…" introductory text is visible
  - Password field is present
  - "Confirm" submit button is present
  - No "Alternative options" section (unless alternatives are configured)

**Checkpoint**: US3 complete when TVAL-4, TVAL-5, and TPWVI-2 all pass.

---

## Phase 6: User Story 4 — Developer Verifies Templates via Automated Tests (Priority: P3)

**Goal**: The full integration test suite and screenshot tests pass with zero failures. 12 PNGs generated (4 page states × 3 viewports).

**Independent Test**:

```bash
poetry run pytest tests/test_addons/test_allauth/test_password_change_view.py --no-cov -v
```

### Implementation for User Story 4

- [X] T008 [P] [US4] Run the full integration test suite and confirm zero failures

  ```bash
  poetry run pytest tests/test_addons/test_allauth/test_password_change_view.py --no-cov -v
  ```

  Expected: All test classes pass — `TestBaseManagePasswordView`, `TestPasswordChangeView`, `TestPasswordSetView`, `TestPasswordChangeFormFields`, `TestPasswordSetFormFields`, `TestReauthenticateView`.

- [X] T009 [P] [US4] Write and run screenshot tests in `screenshots/test_password_change_screenshots.py`

  Capture 4 page states × 3 viewports = 12 PNGs:

  | Page state | Screenshot filename |
  |---|---|
  | password-change | `password-change.png` |
  | password-set | `password-set.png` |
  | reauthenticate (no alternatives) | `reauthenticate.png` |
  | reauthenticate (with alternatives) | `reauthenticate-alternatives.png` |

  Viewports: desktop (1440×900), tablet (768×1024), mobile (390×844).
  Save to `docs/_static/{desktop,tablet,mobile}/`.

  **Viewport parametrization (Principle XIII)**: Use `@pytest.mark.parametrize` over a viewport fixture — see `screenshots/test_login_screenshots.py` as the reference pattern. Do not duplicate assertion logic per viewport.

  **`reauthenticate-alternatives` state**: The live `account_reauthenticate` view does not expose `reauthentication_alternatives` without real MFA configuration. Register a lightweight test-only view in `tests/urls.py` that renders `account/reauthenticate.html` with a mock alternatives list — the same pattern as `_verified_email_required_view` in spec 006. Example:

  ```python
  # tests/urls.py addition
  from django.shortcuts import render

  class _MockAlternative:
      url = "/accounts/mock-mfa/"
      description = "Use authenticator code"

  def _reauthenticate_with_alternatives_view(request):
      from allauth.account.forms import ReauthenticateForm
      return render(request, "account/reauthenticate.html", {
          "form": ReauthenticateForm(),
          "reauthentication_alternatives": [_MockAlternative()],
      })

  urlpatterns = [
      # … existing patterns …
      path("test/reauthenticate-alternatives/", _reauthenticate_with_alternatives_view),
  ]
  ```

  Navigate the screenshot test to this test-only URL to capture the alternatives state.

  Run with:

  ```bash
  poetry run pytest screenshots/test_password_change_screenshots.py -v
  ```

  Inspect each generated PNG to verify the DAC layout, breadcrumbs, and form structure are correct (Principle XIII visual verification).

- [X] TVAL-6 [US4] Run the full allauth test suite to confirm no regressions

  ```bash
  poetry run pytest tests/test_addons/test_allauth/ --no-cov -q
  ```

**Checkpoint**: US4 complete when all tests pass and 12 PNGs are generated.

---

## Phase 7: Polish & Cross-Cutting Concerns

- [X] T010 [P] Verify no `{% element %}` or `{% endelement %}` tags remain in any rewritten template

  ```powershell
  Select-String -Path `
    "dac\addons\allauth\templates\account\base_reauthenticate.html",`
    "dac\addons\allauth\templates\account\reauthenticate.html",`
    "dac\addons\allauth\templates\account\password_change.html",`
    "dac\addons\allauth\templates\account\password_set.html" `
    -Pattern "element"
  ```

  Expected: No matches. If any are found, remove them before proceeding.

- [X] T011 [P] Verify all user-visible strings in rewritten templates are wrapped in `{% trans %}` or `{% blocktrans %}`

  Scan each rewritten file for bare English prose not preceded by a translation tag. Pay particular attention to button text, label text, heading text, and link text. Correct any unwrapped string in-place.

- [X] T012 [P] Run the full test suite to confirm no regressions

  ```bash
  poetry run pytest tests/ --no-cov -q
  ```

  Expected: All tests pass with zero failures.

- [X] T013 Mark all tasks complete in `specs/007-allauth-password-change/tasks.md` and update `specs-overview.md` if present.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: N/A — proceed immediately
- **Phase 2 (Foundational)**: No dependencies — start here (T001)
- **Phase 3 (US1)**: Depends on Phase 2 (T001) for reauthenticate base; T002 and T003 are parallel
- **Phase 4 (US2)**: Depends on Phase 3 (T002, T003 complete)
- **Phase 5 (US3)**: Depends on Phase 2 (T001); T006 is the primary impl task
- **Phase 6 (US4)**: Depends on all previous phases complete
- **Phase 7 (Polish)**: Depends on Phase 6 complete

### User Story Dependencies

- **US1 (P1)**: Depends only on foundational T001 — T002 and T003 are parallel
- **US2 (P2)**: Depends on US1 (T002, T003 must be complete before testing form fields)
- **US3 (P2)**: Depends on foundational T001 only — can proceed in parallel with US1/US2
- **US4 (P3)**: Depends on US1 + US2 + US3 all complete

### Parallel Execution

**Phase 3** (US1): T002 (`password_change.html`) and T003 (`password_set.html`) can run in parallel — different files.

**Phase 5** (US3): T006 (`reauthenticate.html`) can run in parallel with Phase 3 tasks (T002, T003) — different files, same foundational dependency (T001).

### MVP Scope

Deliver US1 (Phase 3) first:

1. Complete T001 (foundational base template)
2. Complete T002 + T003 in parallel (management template rewrites)
3. Write T004 tests and run TVAL-1 + TVAL-2

This delivers the core DAC layout fix for password management in isolation before tackling reauthentication (US3) or form-field tests (US2/US4).

---

## Implementation Strategy

1. **Start with foundational**: T001 (`base_reauthenticate.html`) — blocks US3 but is safe to do first since MFA templates are not in scope
2. **Parallel management rewrites**: T002 (`password_change.html`) + T003 (`password_set.html`) — identical pattern, different files
3. **Write tests alongside**: T004 (US1 tests) immediately after T002+T003; T005 (US2 tests) confirms form fields; T007 (US3 tests) alongside T006
4. **Screenshots last**: T009 after all templates and tests pass
5. **Polish**: T010–T013 as a final sweep before committing
