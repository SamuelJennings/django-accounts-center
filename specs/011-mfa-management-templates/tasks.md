# Tasks: MFA Management Templates

**Input**: Design documents from `specs/011-mfa-management-templates/`
**Prerequisites**: plan.md ✅ | spec.md ✅ | research.md ✅ | data-model.md ✅ | contracts/component-interface.md ✅ | quickstart.md ✅

**Scope**: 10 template files edited (1 base + 9 content) · 1 integration test file · 1 screenshot test file · 22 PNGs (11 states × 2 viewports)

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1–US4)
- Exact file paths included in every task description

---

## Phase 1: Setup

**Purpose**: Verify the test baseline before any changes are made

- [X] T001 Run existing allauth addon test suite to establish a clean baseline: `poetry run pytest tests/test_addons/test_allauth/ --no-cov -q` — MUST pass before any edits begin

---

## Phase 2: User Story 1 — Developer Wires MFA Management into the DAC Layout (Priority: P1) 🎯 MVP

**Goal**: Fix `mfa/base_manage.html` so every MFA management page inherits the full DAC Account Center layout (sidebar, breadcrumbs, card-stack). One-line change that propagates automatically to all nine content templates through the existing sub-base chain.

**Independent Test**: Navigate to `/accounts/2fa/` as a logged-in user; the Account Center sidebar, "Account Center" root breadcrumb, and "Two-Factor Authentication" leaf breadcrumb must all be visible.

- [X] T002 [US1] Edit `dac/addons/allauth/templates/mfa/base_manage.html` — change the single `extends` line from `allauth/layouts/manage.html` to `dac/base.html`

  Before:

  ```django
  {% extends "allauth/layouts/manage.html" %}
  ```

  After:

  ```django
  {% extends "dac/base.html" %}
  ```

  No other changes to this file. The sub-base templates (`mfa/totp/base.html`, `mfa/recovery_codes/base.html`, `mfa/webauthn/base.html`) are NOT modified — the fix propagates through them automatically.

- [ ] T003 [US1] playwright-cli skill verify — consult `.github/skills/playwright-cli/SKILL.md` before executing; start dev server (`poetry run python manage.py runserver`), log in as a test user, navigate to `/accounts/2fa/`; confirm the Account Center sidebar, "Account Center" breadcrumb, "Two-Factor Authentication" breadcrumb, and page heading are all rendered (page must NOT show the raw allauth layout)

- [X] TVAL-1 [US1] Run `python manage.py check` — MUST pass with no errors after T002

**Checkpoint**: US1 complete — all MFA management pages now render inside the DAC Account Center layout

---

## Phase 3: User Story 2 — End User Manages Two-Factor Authentication (Priority: P2)

**Goal**: Fully rewrite `mfa/index.html`, the TOTP templates (`activate_form.html`, `deactivate_form.html`), and the Recovery Codes templates (`index.html`, `generate.html`) as clean Cotton templates using `<c-card>`, `<c-form>`, `<c-button>`, and raw HTML where needed. Zero allauth `{% element %}` tags.

**Independent Test**: Render each template with representative context; assert correct panels, status text, action buttons, QR code presence, textarea with `id="recovery_codes"`, and conditional danger buttons are all present.

- [X] T004 [US2] Fully rewrite `dac/addons/allauth/templates/mfa/index.html` using the interface contract in `specs/011-mfa-management-templates/contracts/component-interface.md`:

  - `{% load i18n %}` (remove `{% load allauth %}` — no allauth tags used)
  - `{% block title %}{% trans "Two-Factor Authentication" %}{% endblock title %}`
  - `{% block page.breadcrumbs %}{{ block.super }}<c-navigation.breadcrumbs.item text="{% trans 'Two-Factor Authentication' %}" />{% endblock page.breadcrumbs %}`
  - `{% block page.content %}` — containing one `<c-card>` per enabled method:

    **TOTP panel** (when `"totp"` in `MFA_SUPPORTED_TYPES`):

    ```django
    <c-card title="{% trans 'Authenticator App' %}">
      {% if authenticators.totp %}
        <p>{% trans "Authentication using an authenticator app is active." %}</p>
        <c-button href="{% url 'mfa_deactivate_totp' %}" variant="danger" text="{% trans 'Deactivate' %}" />
      {% else %}
        <p>{% trans "An authenticator app is not active." %}</p>
        <c-button href="{% url 'mfa_activate_totp' %}" variant="primary" text="{% trans 'Activate' %}" />
      {% endif %}
    </c-card>
    ```

    **Recovery Codes panel** (when `"recovery_codes"` in `MFA_SUPPORTED_TYPES`):

    ```django
    <c-card title="{% trans 'Recovery Codes' %}">
      {% if authenticators.recovery_codes %}
        <p>{% blocktrans with unused=authenticators.recovery_codes.get_unused_codes|length total=authenticators.recovery_codes.generate_codes|length %}{{ unused }} of {{ total }} recovery codes remaining.{% endblocktrans %}</p>
      {% else %}
        <p>{% trans "No recovery codes set up." %}</p>
      {% endif %}
      {% if is_mfa_enabled and authenticators.recovery_codes %}
        <c-button href="{% url 'mfa_view_recovery_codes' %}" variant="primary" text="{% trans 'View' %}" />
        <c-button href="{% url 'mfa_download_recovery_codes' %}" text="{% trans 'Download' %}" />
      {% endif %}
      <c-button href="{% url 'mfa_generate_recovery_codes' %}" text="{% trans 'Generate' %}" />
    </c-card>
    ```

    **WebAuthn panel** (when `"webauthn"` in `MFA_SUPPORTED_TYPES`):

    ```django
    <c-card title="{% trans 'Security Keys' %}">
      {% with count=authenticators.webauthn|length %}
        {% if count %}
          <p>{% blocktrans count counter=count %}{{ counter }} security key registered.{% plural %}{{ counter }} security keys registered.{% endblocktrans %}</p>
        {% else %}
          <p>{% trans "No security keys registered." %}</p>
        {% endif %}
      {% endwith %}
      <c-button href="{% url 'mfa_list_webauthn' %}" variant="primary" text="{% trans 'Manage' %}" />
    </c-card>
    ```

  - All user-visible strings wrapped in `{% trans %}` or `{% blocktrans %}` (i18n)
  - NO `{% element %}`, `{% endelement %}`, or `{% slot %}` tags

- [X] T005 [P] [US2] Fully rewrite `dac/addons/allauth/templates/mfa/totp/activate_form.html`:

  - `{% load i18n %}`
  - `{% block title %}{% trans "Activate Authenticator App" %}{% endblock title %}`
  - `{% block page.breadcrumbs %}{{ block.super }}<c-navigation.breadcrumbs.item href="{% url 'mfa_index' %}" text="{% trans 'Two-Factor Authentication' %}" /><c-navigation.breadcrumbs.item text="{% trans 'Activate' %}" />{% endblock page.breadcrumbs %}`
  - `{% block page.content %}` — using `<c-form>` without `form-obj` (custom content in default slot):

    ```django
    <c-form title="{% trans 'Activate Authenticator App' %}" method="post" action="{% url 'mfa_activate_totp' %}">
      {% csrf_token %}
      <c-slot name="form_actions">
        <c-button type="submit" variant="primary" text="{% trans 'Activate' %}" />
      </c-slot>
      <div class="text-center mb-3">
        <img src="{{ totp_svg_data_uri }}" alt="{% trans 'TOTP QR Code' %}" class="img-fluid" style="max-width: 220px" />
      </div>
      <p>{% blocktrans with secret=form.secret.value %}Or enter this secret manually: <code>{{ secret }}</code>{% endblocktrans %}</p>
      <c-form.field type="text"
                        id="{{ form.code.auto_id }}"
                        name="{{ form.code.html_name }}"
                        label="{{ form.code.label }}"
                        autocomplete="one-time-code"
                        placeholder="{% trans 'Code' %}"
                        value="{{ form.code.value|default_if_none:'' }}"
                        class="{% if form.code.errors %}is-invalid{% endif %}" />
      {% for error in form.code.errors %}<div class="invalid-feedback d-block">{{ error }}</div>{% endfor %}
    </c-form>
    ```

- [X] T006 [P] [US2] Fully rewrite `dac/addons/allauth/templates/mfa/totp/deactivate_form.html`:

  - `{% load i18n %}`
  - `{% block title %}{% trans "Deactivate Authenticator App" %}{% endblock title %}`
  - `{% block page.breadcrumbs %}{{ block.super }}<c-navigation.breadcrumbs.item href="{% url 'mfa_index' %}" text="{% trans 'Two-Factor Authentication' %}" /><c-navigation.breadcrumbs.item text="{% trans 'Deactivate' %}" />{% endblock page.breadcrumbs %}`
  - `{% block page.content %}` — using `<c-form>` with `:form-obj="form"`:

    ```django
    <c-form title="{% trans 'Deactivate Authenticator App' %}" method="post" action="{% url 'mfa_deactivate_totp' %}" :form-obj="form">
      <c-slot name="form_actions">
        <c-button type="submit" variant="danger" text="{% trans 'Deactivate' %}" />
      </c-slot>
    </c-form>
    ```

- [X] T007 [P] [US2] Fully rewrite `dac/addons/allauth/templates/mfa/recovery_codes/index.html`:

  Research Decision 3 applies: use `<c-form.field type="textarea">` with recovery codes in the default slot. `id="recovery_codes"` is a hard JS dependency and MUST be preserved exactly. The component template places `{{ slot }}` on its own indented line — use `{# djlint:off #}` to prevent reformatting.

  - `{% load i18n %}`
  - `{% block title %}{% trans "Recovery Codes" %}{% endblock title %}`
  - `{% block page.breadcrumbs %}{{ block.super }}<c-navigation.breadcrumbs.item href="{% url 'mfa_index' %}" text="{% trans 'Two-Factor Authentication' %}" /><c-navigation.breadcrumbs.item text="{% trans 'Recovery Codes' %}" />{% endblock page.breadcrumbs %}`
  - `{% block page.content %}` — a `<c-card>` containing:

    ```django
    <c-card title="{% trans 'Recovery Codes' %}">
      {% if can_view_codes %}
        <c-form.field type="textarea" id="recovery_codes" readonly
                          rows="{{ unused_codes|length }}" label="{% trans 'Unused codes' %}"
                          class="mb-3">
          {# djlint:off #}{% for code in unused_codes %}{% if forloop.counter0 %}

{% endif %}{{ code }}{% endfor %}{# djlint:on #}
        </c-form.field>
        {% if MFA_RECOVERY_CODES_SHOW_ONCE %}
          <div class="form-check mb-3">
            <input class="form-check-input" type="checkbox" id="codes_saved" />
            <label class="form-check-label" for="codes_saved">{% trans "I have saved my recovery codes." %}</label>
          </div>
        {% endif %}
        {% if can_download_codes %}
          <c-button href="{% url 'mfa_download_recovery_codes' %}" variant="primary" text="{% trans 'Download' %}" />
        {% endif %}
        {% if can_generate_codes %}
          <c-button href="{% url 'mfa_generate_recovery_codes' %}" text="{% trans 'Generate New Codes' %}" />
        {% endif %}
      {% endif %}
    </c-card>
    ```

- `{% block extra_js %}{{ block.super }}{% include "mfa/recovery_codes/snippets/scripts.html" %}{% endblock extra_js %}`

- [X] T008 [P] [US2] Fully rewrite `dac/addons/allauth/templates/mfa/recovery_codes/generate.html`:

  - `{% load i18n %}`
  - `{% block title %}{% trans "Generate Recovery Codes" %}{% endblock title %}`
  - `{% block page.breadcrumbs %}{{ block.super }}<c-navigation.breadcrumbs.item href="{% url 'mfa_index' %}" text="{% trans 'Two-Factor Authentication' %}" /><c-navigation.breadcrumbs.item href="{% url 'mfa_view_recovery_codes' %}" text="{% trans 'Recovery Codes' %}" /><c-navigation.breadcrumbs.item text="{% trans 'Generate' %}" />{% endblock page.breadcrumbs %}`
  - `{% block page.content %}` — using `<c-form>` with explicit `{% csrf_token %}` and single inline-conditional button:

    ```django
    <c-form title="{% trans 'Generate Recovery Codes' %}" method="post" action="{% url 'mfa_generate_recovery_codes' %}">
      {% csrf_token %}
      <c-slot name="form_actions">
        <c-button type="submit"
                  variant="{% if unused_code_count > 0 %}danger{% else %}primary{% endif %}"
                  text="{% trans 'Generate New Codes' %}" />
      </c-slot>
      {% if unused_code_count > 0 %}
        <p class="text-danger">
          {% blocktrans with count=unused_code_count %}
            Warning: generating new codes will invalidate your {{ count }} existing unused code(s).
          {% endblocktrans %}
        </p>
      {% endif %}
    </c-form>
    ```

- [ ] T009 [P] [US2] playwright-cli skill verify — consult `.github/skills/playwright-cli/SKILL.md` before executing; navigate to `/accounts/2fa/` with TOTP active and recovery codes set up; confirm TOTP panel shows "active" status and "Deactivate" button, Recovery Codes panel shows unused/total count, page is inside the DAC layout

- [ ] T010 [P] [US2] playwright-cli skill verify — navigate to `/accounts/2fa/recovery-codes/generate/` with existing unused codes; confirm danger-styled "Generate New Codes" button and invalidation warning are present

- [X] TVAL-2 [US2] Run `python manage.py check` — MUST pass with no errors after T004–T008

- [X] TVAL-3 [US2] Run `poetry run pytest tests/test_addons/test_allauth/ --no-cov -q` — MUST pass (existing tests must not regress)

**Checkpoint**: US2 complete — MFA overview, TOTP, and Recovery Codes pages render with DAC layout and Cotton components

---

## Phase 4: User Story 3 — End User Manages Security Keys (Priority: P3)

**Goal**: Fully rewrite the four WebAuthn management templates as clean Cotton templates. WebAuthn JavaScript blocks are preserved **verbatim**. `id="mfa_webauthn_add"` is a hard JS dependency and MUST be preserved.

**Independent Test**: Render `mfa/webauthn/authenticator_list.html` with both non-empty and empty authenticator lists; assert table rows with correct badge variants and action links (non-empty), and informational empty-state message (empty).

- [X] T011 [US3] Fully rewrite `dac/addons/allauth/templates/mfa/webauthn/authenticator_list.html`:

  Research Decision 6 applies: no `<c-table>` component exists; use raw Bootstrap `<table class="table mb-3">` inside `<c-card>`. Edit and Remove actions use `<c-dropdown>` (not `<c-button>` pairs). Add button in card body.

  - `{% load i18n %}`
  - `{% block title %}{% trans "Security Keys" %}{% endblock title %}`
  - `{% block page.breadcrumbs %}{{ block.super }}<c-navigation.breadcrumbs.item href="{% url 'mfa_index' %}" text="{% trans 'Two-Factor Authentication' %}" /><c-navigation.breadcrumbs.item text="{% trans 'Security Keys' %}" />{% endblock page.breadcrumbs %}`
  - `{% block page.content %}` — `<c-card>` with Add button in card body:

    ```django
    <c-card title="{% trans 'Security Keys' %}">
      {% if authenticators %}
        <table class="table mb-3">
          <thead>
            <tr>
              <th>{% trans "Name" %}</th>
              <th>{% trans "Type" %}</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {% for authenticator in authenticators %}
              <tr>
                {% with wrapped=authenticator.wrap %}
                  <td>{{ wrapped.name }}</td>
                  <td>
                    {% if wrapped.is_passwordless %}
                      <c-badge variant="primary" text="{% trans 'Passkey' %}" />
                    {% elif wrapped.is_passwordless is False %}
                      <c-badge variant="secondary" text="{% trans 'Security key' %}" />
                    {% else %}
                      <c-badge variant="warning" text="{% trans 'Unspecified' %}" />
                    {% endif %}
                  </td>
                  <td class="text-end">
                    <c-dropdown icon="three-dots" :caret="False" align="end">
                      <c-dropdown.item href="{% url 'mfa_edit_webauthn' authenticator.pk %}" text="{% trans 'Edit' %}" />
                      <c-dropdown.divider />
                      <c-dropdown.item href="{% url 'mfa_remove_webauthn' authenticator.pk %}" class="link-danger" icon="delete" text="{% trans 'Remove' %}" />
                    </c-dropdown>
                  </td>
                {% endwith %}
              </tr>
            {% endfor %}
          </tbody>
        </table>
      {% else %}
        <p>{% trans "No security keys have been registered." %}</p>
      {% endif %}
      <c-button href="{% url 'mfa_add_webauthn' %}" variant="primary" text="{% trans 'Add Security Key' %}" />
    </c-card>
    ```

- [X] T012 [P] [US3] Rewrite `dac/addons/allauth/templates/mfa/webauthn/add_form.html`:

  Research Decision 5 applies: the WebAuthn JS block MUST be preserved verbatim. `id="mfa_webauthn_add"` on the submit button is a hard JS dependency.

  - `{% load i18n %}`
  - `{% block title %}{% trans "Add Security Key" %}{% endblock title %}`
  - `{% block page.breadcrumbs %}{{ block.super }}<c-navigation.breadcrumbs.item href="{% url 'mfa_index' %}" text="{% trans 'Two-Factor Authentication' %}" /><c-navigation.breadcrumbs.item href="{% url 'mfa_list_webauthn' %}" text="{% trans 'Security Keys' %}" /><c-navigation.breadcrumbs.item text="{% trans 'Add' %}" />{% endblock page.breadcrumbs %}`
  - `{% block page.content %}` — `<c-form>` without `form-obj`:

    ```django
    <c-form title="{% trans 'Add Security Key' %}" method="post" action="{% url 'mfa_add_webauthn' %}">
      {% csrf_token %}
      <c-slot name="form_actions">
        <c-button type="submit" id="mfa_webauthn_add" variant="primary" text="{% trans 'Register Key' %}" />
      </c-slot>
      {% if form.passwordless %}
        <div class="form-check mb-3">
          <input class="form-check-input"
                 type="checkbox"
                 id="{{ form.passwordless.auto_id }}"
                 name="{{ form.passwordless.html_name }}"
                 {% if form.passwordless.value %}checked{% endif %} />
          <label class="form-check-label" for="{{ form.passwordless.auto_id }}">
            {{ form.passwordless.label }}
          </label>
          <div class="form-text">{{ form.passwordless.help_text }}</div>
        </div>
      {% endif %}
      {{ form.credential }}
    </c-form>
    ```

  - `{% block extra_js %}{{ block.super }}` — preserved verbatim:

    ```django
    {% include "mfa/webauthn/snippets/scripts.html" %}
    {{ js_data|json_script:"js_data" }}
    <script data-allauth-onload="allauth.webauthn.forms.addForm" type="application/json">
      {
        "ids": {
          "add": "mfa_webauthn_add",
          "passwordless": "{{ form.passwordless.auto_id }}",
          "credential": "{{ form.credential.auto_id }}",
          "data": "js_data"
        }
      }
    </script>
    {% endblock extra_js %}
    ```

- [X] T013 [P] [US3] Rewrite `dac/addons/allauth/templates/mfa/webauthn/edit_form.html`:

  - `{% load i18n %}`
  - `{% block title %}{% trans "Edit Security Key" %}{% endblock title %}`
  - `{% block page.breadcrumbs %}{{ block.super }}<c-navigation.breadcrumbs.item href="{% url 'mfa_index' %}" text="{% trans 'Two-Factor Authentication' %}" /><c-navigation.breadcrumbs.item href="{% url 'mfa_list_webauthn' %}" text="{% trans 'Security Keys' %}" /><c-navigation.breadcrumbs.item text="{% trans 'Edit' %}" />{% endblock page.breadcrumbs %}`
  - `{% block page.content %}` — `<c-form>` with `:form-obj="form"`:

    ```django
    <c-form title="{% trans 'Edit Security Key' %}" method="post" action="{% url 'mfa_edit_webauthn' authenticator.pk %}" :form-obj="form">
      <c-slot name="form_actions">
        <c-button type="submit" variant="primary" text="{% trans 'Save' %}" />
      </c-slot>
    </c-form>
    ```

- [X] T014 [P] [US3] Rewrite `dac/addons/allauth/templates/mfa/webauthn/authenticator_confirm_delete.html`:

  - `{% load i18n %}`
  - `{% block title %}{% trans "Remove Security Key" %}{% endblock title %}`
  - `{% block page.breadcrumbs %}{{ block.super }}<c-navigation.breadcrumbs.item href="{% url 'mfa_index' %}" text="{% trans 'Two-Factor Authentication' %}" /><c-navigation.breadcrumbs.item href="{% url 'mfa_list_webauthn' %}" text="{% trans 'Security Keys' %}" /><c-navigation.breadcrumbs.item text="{% trans 'Remove' %}" />{% endblock page.breadcrumbs %}`
  - `{% block page.content %}` — `<c-form>` with `:form-obj="form"`:

    ```django
    <c-form title="{% trans 'Remove Security Key' %}" method="post" action="{% url 'mfa_remove_webauthn' pk=authenticator.pk %}">
      {% csrf_token %}
      <c-slot name="form_actions">
        <c-button type="submit" variant="danger" text="{% trans 'Remove' %}" />
      </c-slot>
      <p>{% blocktrans with name=authenticator.wrap.name %}Are you sure you want to remove the security key "{{ name }}"?{% endblocktrans %}</p>
    </c-form>
    ```

- [ ] T015 [P] [US3] playwright-cli skill verify — consult `.github/skills/playwright-cli/SKILL.md` before executing; navigate to `/accounts/2fa/webauthn/` with registered security keys; confirm table rows appear with name, type badge, Edit and Remove action links, and the page is inside the DAC layout

- [ ] T016 [P] [US3] playwright-cli skill verify — navigate to `/accounts/2fa/webauthn/` with no registered keys; confirm empty-state message "No security keys have been registered." is shown (no table visible)

- [X] TVAL-4 [US3] Run `python manage.py check` — MUST pass with no errors after T011–T014

- [X] TVAL-5 [US3] Run `poetry run pytest tests/test_addons/test_allauth/ --no-cov -q` — MUST pass (existing tests must not regress)

**Checkpoint**: US3 complete — all four WebAuthn management pages render with DAC layout and Cotton components; WebAuthn JS preserved intact

---

## Phase 5: User Story 4 — Developer Verifies Templates via Automated Tests (Priority: P4)

**Goal**: Integration tests covering all acceptance scenarios from US1–US3. Screenshot tests capturing all 11 page states × 2 viewports = 22 PNGs.

**Independent Test**: `pytest tests/test_addons/test_allauth/test_mfa_management_view.py --no-cov -v` passes with zero failures. `pytest screenshots/test_mfa_management_screenshots.py` generates 22 PNGs.

- [X] T017 [US4] Create `tests/test_addons/test_allauth/test_mfa_management_view.py` — integration tests using the Cotton rendering fixtures.

  Consult `.github/skills/cotton-test-components/SKILL.md` and `.github/skills/pytest-django-testing/SKILL.md` before writing tests.

  Required test cases (each covers one acceptance scenario from spec.md):

  1. **Layout test** (US1 SC1–3): Render `mfa/index.html` with default context → assert Account Center sidebar element, "Account Center" breadcrumb text, "Two-Factor Authentication" breadcrumb text, and heading string "Two-Factor Authentication" (via `{% block title %}`) are all present
  2. **TOTP active state** (US2 SC1): Render `mfa/index.html` with `authenticators.totp` truthy → assert "Authentication using an authenticator app is active." text and "Deactivate" link are present
  3. **TOTP inactive state** (US2 SC2): Render `mfa/index.html` with `authenticators.totp` falsy → assert "An authenticator app is not active." text and "Activate" link are present
  4. **Recovery codes panel visible** (US2 SC3): Render `mfa/index.html` with `"recovery_codes"` in `MFA_SUPPORTED_TYPES` and `is_mfa_enabled=True` and `authenticators.recovery_codes` set → assert "View", "Download", "Generate" action links and unused/total count text are present
  5. **Method panel gating** (US2): Render `mfa/index.html` with `MFA_SUPPORTED_TYPES=["totp"]` only → assert WebAuthn panel and Recovery Codes panel are NOT present in output
  6. **TOTP activate form** (US2 SC4): Render `mfa/totp/activate_form.html` with mock form and `totp_svg_data_uri` → assert QR code `<img>` tag with data URI src, secret display, token input field, and "Activate" submit button are present
  7. **TOTP deactivate form** (US2 SC5): Render `mfa/totp/deactivate_form.html` → assert "Deactivate" button with danger variant is present
  8. **Recovery codes view** (US2 SC6): Render `mfa/recovery_codes/index.html` with `can_view_codes=True` and `unused_codes=["code1", "code2"]` → assert `<textarea id="recovery_codes">` with `readonly` attribute is present and contains the code strings; assert "Download" and "Generate" buttons are present
  9. **Recovery codes generate — existing codes** (US2 SC7): Render `mfa/recovery_codes/generate.html` with `unused_code_count=5` → assert invalidation warning text and danger-styled "Generate New Codes" button are present
  10. **Recovery codes generate — no codes** (edge case): Render `mfa/recovery_codes/generate.html` with `unused_code_count=0` → assert NO invalidation warning and NO danger variant on the "Generate" button
  11. **WebAuthn list — with keys** (US3 SC1): Render `mfa/webauthn/authenticator_list.html` with authenticators list containing 2 items → assert 2 table rows with key names, type badges, and a three-dots dropdown containing Edit and Remove action items per row
  12. **WebAuthn list — empty** (US3 SC2): Render `mfa/webauthn/authenticator_list.html` with `authenticators=[]` → assert "No security keys have been registered." empty-state message; assert no `<table>` in output
  13. **WebAuthn add form** (US3 SC3): Render `mfa/webauthn/add_form.html` → assert form fields and `<script data-allauth-onload="allauth.webauthn.forms.addForm">` block are present; assert `id="mfa_webauthn_add"` is present on the submit button
  14. **WebAuthn edit form** (US3 SC4): Render `mfa/webauthn/edit_form.html` with mock authenticator → assert "Save" submit button is present
  15. **WebAuthn remove confirmation** (US3 SC5): Render `mfa/webauthn/authenticator_confirm_delete.html` with mock authenticator → assert danger-styled "Remove" button and authenticator name in confirmation text are present
  16. **No allauth element tags** (SC-002): Render each of the 9 content templates → assert rendered output contains no `{% element %}` and no `{% endelement %}` strings
  17. **RC button suppression when MFA disabled** (Edge Case / L1): Render `mfa/index.html` with `"recovery_codes"` in `MFA_SUPPORTED_TYPES`, `is_mfa_enabled=False`, and `authenticators.recovery_codes` truthy → assert "View" and "Download" action links are absent from the Recovery Codes panel
  18. **Recovery codes save-once checkbox** (Edge Case / L2): Render `mfa/recovery_codes/index.html` with `can_view_codes=True` and `MFA_RECOVERY_CODES_SHOW_ONCE=True` → assert element with `id="codes_saved"` is present in output

  Use factory-boy (`DjangoModelFactory`) for any entities requiring database access; otherwise use plain dataclass/mock objects with the required template attributes.

- [X] T018 [P] [US4] Create `screenshots/test_mfa_management_screenshots.py` — pytest-playwright screenshot tests (11 states × 2 viewports = 22 PNGs):

  Consult `.github/skills/playwright-cli/SKILL.md` for screenshot test patterns.

  States and save paths (desktop 1440×900, mobile 390×844):

  | State | Desktop path | Mobile path | Template |
  |---|---|---|---|
  | `mfa-overview-active` | `docs/_static/desktop/mfa-overview-active.png` | `docs/_static/mobile/mfa-overview-active.png` | `mfa/index.html` |
  | `mfa-overview-inactive` | `docs/_static/desktop/mfa-overview-inactive.png` | `docs/_static/mobile/mfa-overview-inactive.png` | `mfa/index.html` |
  | `mfa-totp-activate` | `docs/_static/desktop/mfa-totp-activate.png` | `docs/_static/mobile/mfa-totp-activate.png` | `mfa/totp/activate_form.html` |
  | `mfa-totp-deactivate` | `docs/_static/desktop/mfa-totp-deactivate.png` | `docs/_static/mobile/mfa-totp-deactivate.png` | `mfa/totp/deactivate_form.html` |
  | `mfa-recovery-codes-view` | `docs/_static/desktop/mfa-recovery-codes-view.png` | `docs/_static/mobile/mfa-recovery-codes-view.png` | `mfa/recovery_codes/index.html` |
  | `mfa-recovery-codes-generate` | `docs/_static/desktop/mfa-recovery-codes-generate.png` | `docs/_static/mobile/mfa-recovery-codes-generate.png` | `mfa/recovery_codes/generate.html` |
  | `mfa-webauthn-list` | `docs/_static/desktop/mfa-webauthn-list.png` | `docs/_static/mobile/mfa-webauthn-list.png` | `mfa/webauthn/authenticator_list.html` |
  | `mfa-webauthn-list-empty` | `docs/_static/desktop/mfa-webauthn-list-empty.png` | `docs/_static/mobile/mfa-webauthn-list-empty.png` | `mfa/webauthn/authenticator_list.html` |
  | `mfa-webauthn-add` | `docs/_static/desktop/mfa-webauthn-add.png` | `docs/_static/mobile/mfa-webauthn-add.png` | `mfa/webauthn/add_form.html` |
  | `mfa-webauthn-edit` | `docs/_static/desktop/mfa-webauthn-edit.png` | `docs/_static/mobile/mfa-webauthn-edit.png` | `mfa/webauthn/edit_form.html` |
  | `mfa-webauthn-remove` | `docs/_static/desktop/mfa-webauthn-remove.png` | `docs/_static/mobile/mfa-webauthn-remove.png` | `mfa/webauthn/authenticator_confirm_delete.html` |

  Use `@pytest.mark.parametrize` or a viewport fixture to avoid duplicating assertion logic.
  Each state requires a live logged-in browser session against the running dev server.
  Commit both the screenshot test file and all 22 generated PNG files.

- [X] TVAL-6 [US4] Run `poetry run pytest tests/test_addons/test_allauth/test_mfa_management_view.py --no-cov -v` — MUST pass with zero failures; all 18 test cases green

- [X] TVAL-7 [US4] Run `poetry run pytest screenshots/test_mfa_management_screenshots.py -v` — MUST produce 22 PNG files in `docs/_static/` (11 states × 2 viewports); if interactive playwright-cli verification is insufficient to confirm layout differences across viewports, inspect the generated PNGs as a fallback (Principle XIII)

**Checkpoint**: US4 complete — all 16 integration tests green; 22 screenshots committed as visual documentation

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final quality gates across all modified files

- [X] T019 [P] Run djlint on all 10 modified templates — zero violations:

  ```bash
  poetry run djlint `
    dac/addons/allauth/templates/mfa/base_manage.html `
    dac/addons/allauth/templates/mfa/index.html `
    dac/addons/allauth/templates/mfa/totp/activate_form.html `
    dac/addons/allauth/templates/mfa/totp/deactivate_form.html `
    dac/addons/allauth/templates/mfa/recovery_codes/index.html `
    dac/addons/allauth/templates/mfa/recovery_codes/generate.html `
    dac/addons/allauth/templates/mfa/webauthn/authenticator_list.html `
    dac/addons/allauth/templates/mfa/webauthn/add_form.html `
    dac/addons/allauth/templates/mfa/webauthn/edit_form.html `
    dac/addons/allauth/templates/mfa/webauthn/authenticator_confirm_delete.html `
    --check
  ```

  Fix any violations before marking complete.

- [X] T020 [P] Grep for residual allauth element tags in all modified templates — MUST return zero matches (SC-002):

  ```powershell
  Select-String -Path "dac\addons\allauth\templates\mfa\**\*.html" -Pattern "element|endelement" -SimpleMatch -Recurse
  ```

  Any matches are blocking defects.

  Also verify i18n completeness (FR-011) with a heuristic scan for bare English strings:

  ```powershell
  Select-String -Path "dac\addons\allauth\templates\mfa\**\*.html" -Pattern ">\s*[A-Z][a-z ]{3,}<" -Recurse
  ```

  Review any hits manually — legitimate matches are strings already inside `{% trans %}` or `{% blocktrans %}` wrappers; any bare text outside a translation tag is a defect.

- [X] T021 Run full test suite to confirm no regressions:

  ```bash
  poetry run pytest tests/ --no-cov -q
  ```

  MUST pass with zero failures.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — run immediately
- **US1 (Phase 2)**: Depends on Phase 1 baseline passing; T002 is a one-line edit
- **US2 (Phase 3)**: Depends on T002 (base_manage.html fix) — TOTP/RC templates must extend through a fixed `base_manage.html` for full layout rendering
- **US3 (Phase 4)**: Depends on T002 — all WebAuthn templates inherit through `base_manage.html`; T011–T014 can run in parallel with each other and with US2 template tasks (different files)
- **US4 (Phase 5)**: Depends on all template rewrites complete (T004–T014); T017 and T018 can run in parallel
- **Polish (Phase 6)**: Depends on all US phases complete; T019 and T020 can run in parallel

### User Story Dependencies

- **US1 (P1)**: Can start immediately after Phase 1 — no story dependencies
- **US2 (P2)**: Depends on US1 (T002) for full layout chain
- **US3 (P3)**: Depends on US1 (T002) for full layout chain; independent of US2
- **US4 (P4)**: Depends on US2 (T004–T008) and US3 (T011–T014) complete

### Within Each User Story

- T002 → T003 → TVAL-1 (sequential within US1)
- T004 → [T005 ‖ T006 ‖ T007 ‖ T008] → [T009 ‖ T010] → TVAL-2 → TVAL-3
- T011 → [T012 ‖ T013 ‖ T014] → [T015 ‖ T016] → TVAL-4 → TVAL-5
- [T017 ‖ T018] → TVAL-6 → TVAL-7
- [T019 ‖ T020] → T021

---

## Parallel Execution Examples

### User Story 2 — template rewrites

```bash
# After T002 (base fix), all five US2 templates can be written in parallel:
Task T004: mfa/index.html
Task T005: mfa/totp/activate_form.html
Task T006: mfa/totp/deactivate_form.html
Task T007: mfa/recovery_codes/index.html
Task T008: mfa/recovery_codes/generate.html
```

### User Story 3 — template rewrites

```bash
# After T002, WebAuthn rewrites are independent of US2 and each other:
Task T011: mfa/webauthn/authenticator_list.html
Task T012: mfa/webauthn/add_form.html
Task T013: mfa/webauthn/edit_form.html
Task T014: mfa/webauthn/authenticator_confirm_delete.html
```

### User Story 4 — test files

```bash
# After all template rewrites complete, test files are independent:
Task T017: tests/test_addons/test_allauth/test_mfa_management_view.py (16 cases)
Task T018: screenshots/test_mfa_management_screenshots.py (22 PNGs)
```

---

## Implementation Strategy

**Deliver as incremental MVPs** — each phase is independently testable and mergeable:

1. **MVP (US1 only)**: Merge T002 alone — instantly fixes the layout chain for all 9 pages even before the content rewrites land. Pages will render with the DAC sidebar but still with allauth `{% element %}` content (which degrades gracefully — HTML output is produced, just unstyled).

2. **Increment 2 (US1 + US2)**: Add the 5 TOTP/RC content rewrites — TOTP management and Recovery Codes pages are now fully Cotton-rendered.

3. **Increment 3 (+ US3)**: Add the 4 WebAuthn rewrites — Security Keys management is fully Cotton-rendered; WebAuthn JS preserved.

4. **Increment 4 (+ US4)**: Add integration tests and screenshot tests — all acceptance criteria formally verified; 22 PNGs committed as documentation.
