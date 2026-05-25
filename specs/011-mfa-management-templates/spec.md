# Feature Specification: MFA Management Templates

**Feature Branch**: `011-mfa-management-templates`
**Created**: 2026-05-22
**Status**: Refined
**Refined**: 2026-05-25 — Implementation decisions codified: `form_actions` slot name for `<c-form.card>` submit buttons (not `actions`); card body button placement for overview panels (not card-header slot); `<c-dac.form-field>` for TOTP code input with centred QR code; `<c-dropdown>` for WebAuthn edit/remove actions; Bootstrap `form-check` markup for the WebAuthn `passwordless` field; `variant="primary"` on primary action buttons; `authenticator.wrap.name` for the key name; corrected recovery codes API method names.

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Developer Wires MFA Management into the DAC Layout (Priority: P1) **[Developer]**

A developer enabling `allauth.mfa` in their DAC-based project expects all MFA management pages — the Two-Factor Authentication overview, the TOTP activate/deactivate forms, the Recovery Codes view and generate pages, and the Security Key management pages — to inherit the full DAC management layout (Account Center sidebar, breadcrumb trail rooted at "Account Center", and consistent card-stack content area) without writing any structural HTML. They do this by installing `dac.addons.allauth` and defining the allauth MFA URL patterns; the override templates handle the rest.

**Why this priority**: `mfa/base_manage.html` currently extends `allauth/layouts/manage.html` instead of `dac/base.html`. This single deviation means no MFA management page ever renders inside the DAC UI shell — the same defect class as specs 006 (email), 007 (password), 009 (social accounts), and 010 (user sessions). Fixing the base template unblocks all downstream rendering across nine MFA management templates.

**Independent Test**: Can be tested by rendering `mfa/index.html` in isolation using Cotton rendering tests and asserting that the DAC sidebar, breadcrumbs, and card-stack are present in the output.

**Acceptance Scenarios**:

1. **Given** `mfa/base_manage.html` in the DAC addon, **When** it is rendered as a base template, **Then** it extends `dac/base.html` (not `allauth/layouts/manage.html`), inheriting the full DAC management layout.
2. **Given** `mfa/index.html` which extends through `mfa/base_manage.html`, **When** rendered, **Then** the Account Center sidebar, breadcrumb trail, and card-stack content area are all present.
3. **Given** any template in `mfa/totp/`, `mfa/recovery_codes/`, or `mfa/webauthn/`, **When** rendered, **Then** the DAC layout is inherited via the base chain without any additional changes to those sub-base templates.

---

### User Story 2 — End User Manages Two-Factor Authentication with a Consistent UI (Priority: P2) **[End User]**

A logged-in user navigates to the "Two-Factor Authentication" page and sees a panel for each supported MFA method (TOTP authenticator app, Recovery Codes, Security Keys — shown conditionally based on `MFA_SUPPORTED_TYPES`). Each panel shows the current status of that method and provides action links to activate, deactivate, view, download, or manage as appropriate. The current session is inside the same DAC sidebar, breadcrumb trail, and card-stack as every other management page. From the TOTP and Recovery Codes pages they can complete setup, view codes, and generate new codes — all within the consistent DAC UI shell.

**Why this priority**: This is the primary end-user value of the feature. The existing templates use `{% element %}` tags throughout, producing raw allauth markup with no DAC layout context. A user who navigates to MFA management currently sees a completely unstyled page disconnected from the Account Center.

**Independent Test**: Can be tested by rendering `mfa/index.html` with representative context objects (TOTP active, recovery codes set up, WebAuthn not configured) and asserting that the correct panels, status text, and action buttons are present.

**Acceptance Scenarios**:

1. **Given** a user with TOTP active, **When** `mfa/index.html` is rendered, **Then** the TOTP panel shows "Authentication using an authenticator app is active." and a "Deactivate" button.
2. **Given** a user with TOTP not active, **When** `mfa/index.html` is rendered, **Then** the TOTP panel shows "An authenticator app is not active." and an "Activate" button.
3. **Given** `"recovery_codes"` in `MFA_SUPPORTED_TYPES` and `is_mfa_enabled=True`, **When** `mfa/index.html` is rendered, **Then** the Recovery Codes panel shows the unused/total count and action buttons for View, Download (if applicable), and Generate.
4. **Given** `mfa/totp/activate_form.html`, **When** rendered with form and QR code context, **Then** the QR code image (centered), the authenticator secret, a `<c-dac.form-field>` rendering the TOTP code input with label, and an "Activate" submit button with `variant="primary"` are all present.
5. **Given** `mfa/totp/deactivate_form.html`, **When** rendered, **Then** a confirmation message and a "Deactivate" submit button styled as a danger action are present.
6. **Given** `mfa/recovery_codes/index.html` with `can_view_codes=True`, **When** rendered, **Then** the unused recovery codes are shown in a read-only text area and download/generate buttons are present.
7. **Given** `mfa/recovery_codes/generate.html` with `unused_code_count > 0`, **When** rendered, **Then** a warning about invalidating existing codes is shown alongside the "Generate" confirmation button styled as a danger action.
8. **Given** any MFA management template, **When** rendered, **Then** no allauth `{% element %}`, `{% endelement %}`, or `{% slot %}` tags appear in the rendered HTML output.

---

### User Story 3 — End User Manages Security Keys (WebAuthn) with a Consistent UI (Priority: P3) **[End User]**

A logged-in user navigates to the Security Keys management page (when `"webauthn"` is in `MFA_SUPPORTED_TYPES`) and sees a table of their registered security keys — each with its name, type (Passkey / Security key / Unspecified), date added, and last used date — plus "Edit" and "Remove" links per key. An "Add" button lets them register a new security key. All pages in the WebAuthn sub-section render within the standard DAC layout and use Cotton components instead of allauth `{% element %}` tags. The JavaScript required for WebAuthn browser API interactions (credential creation and authentication) is preserved intact in all templates.

**Why this priority**: WebAuthn management (Security Keys) is part of MFA management and shares the same `mfa/base_manage.html` defect. Its templates also use `{% element %}` tags. However, the WebAuthn templates contain non-trivial JavaScript that drives credential creation and authentication flows; these scripts must remain functional through the rewrite.

**Independent Test**: Can be tested by rendering `mfa/webauthn/authenticator_list.html` with context containing both empty and non-empty authenticator lists and asserting the correct table rows, badge variants, and action links are present.

**Acceptance Scenarios**:

1. **Given** a user with registered security keys, **When** `mfa/webauthn/authenticator_list.html` is rendered, **Then** each key appears as a table row showing its name, type badge, and a three-dots dropdown containing Edit and Remove actions.
2. **Given** a user with no registered security keys, **When** `mfa/webauthn/authenticator_list.html` is rendered, **Then** an informational message stating no security keys have been added is shown.
3. **Given** `mfa/webauthn/add_form.html`, **When** rendered, **Then** the form fields and the JavaScript `<script>` block driving the WebAuthn credential-creation flow are both present.
4. **Given** `mfa/webauthn/edit_form.html`, **When** rendered, **Then** the editable name field and a "Save" submit button are present.
5. **Given** `mfa/webauthn/authenticator_confirm_delete.html`, **When** rendered, **Then** a confirmation message and a "Remove" submit button styled as a danger action are present.

---

### User Story 4 — Developer Verifies Templates via Automated Tests (Priority: P4) **[Developer]**

A developer running the test suite expects all MFA management template overrides to be covered by automated integration tests. The tests prove that the correct layout and components are rendered for each branch of the MFA management logic (TOTP active/inactive, recovery codes available/unavailable, WebAuthn keys present/absent, `MFA_SUPPORTED_TYPES` variations).

**Why this priority**: Without automated tests, regressions in block names or Cotton component usage go undetected until a browser. Tests also document the expected context variables for future maintainers.

**Independent Test**: Running `pytest tests/test_addons/test_allauth/test_mfa_management_view.py --no-cov` passes with zero failures. Each test targets a specific acceptance scenario from US1–US3.

**Acceptance Scenarios**:

1. **Given** a test that renders `mfa/index.html` with TOTP active, **When** it asserts the DAC sidebar, breadcrumbs, TOTP active status text, and "Deactivate" button are present, **Then** the assertions pass.
2. **Given** a test that renders `mfa/index.html` with only TOTP in `MFA_SUPPORTED_TYPES` and `is_mfa_enabled=False`, **When** it asserts the recovery codes panel is absent and the TOTP panel shows the "Activate" button, **Then** the assertions pass.
3. **Given** a test that renders `mfa/totp/activate_form.html`, **When** it asserts the QR code image, secret field, and "Activate" button are present, **Then** the assertions pass.
4. **Given** a test that renders `mfa/recovery_codes/index.html` with `can_view_codes=True`, **When** it asserts unused codes and action buttons are present, **Then** the assertions pass.
5. **Given** a test that renders `mfa/webauthn/authenticator_list.html` with an empty list, **When** it asserts the empty-state message is shown, **Then** the assertion passes.

---

### Edge Cases

- What happens when `MFA_SUPPORTED_TYPES` is empty? The `mfa/index.html` page renders with no method panels — only the page heading; no error is raised.
- What happens when `is_mfa_enabled=False` on the index page? The recovery codes panel still appears (showing setup status), but the action buttons for viewing/downloading codes are suppressed by the `{% if is_mfa_enabled %}` condition.
- What happens when `MFA_RECOVERY_CODES_SHOW_ONCE=True` and `can_view_codes=True`? The recovery codes view renders a "I have saved my recovery codes" checkbox controlled by the existing `mfa/js/recovery_codes.js` JavaScript; the template must include the script tag from `{% block extra_js %}`.
- What happens when a WebAuthn authenticator's `wrap().is_passwordless` is `None`? The type badge renders as "Unspecified" — the template handles all three states (True, False, None/other) via conditional branches.
- What happens when the WebAuthn `add_form.html` is rendered without the JS data context? The form renders but the WebAuthn button is non-functional; this is a configuration concern, not a template defect.
- What happens when `unused_code_count=0` on `recovery_codes/generate.html`? The invalidation warning is omitted; the "Generate" button renders with `variant="primary"` (not danger).

## Clarifications

### Session 2026-05-22

- Q: Should the `mfa/index.html` panels (TOTP, Security Keys, Recovery Codes) use `<c-card>` wrappers one-per-method, or a single `<c-card>` containing a list group with one item per method? → A: One `<c-card>` per method — consistent with the card-stack pattern used in all other DAC management pages; each method panel is an independent card with a title and action buttons.
- Q: Should the WebAuthn body rewrites (authenticator_list, add_form, edit_form, confirm_delete) be included in this spec or deferred to a dedicated WebAuthn spec? → A: Included in this spec — they all share the same `mfa/base_manage.html` defect class and the rewrites are straightforward Cotton conversions; the JavaScript blocks are preserved intact, not rewritten.
- Q: What page title and breadcrumb text should `mfa/index.html` use? → A: `{% trans "Two-Factor Authentication" %}` — reuse the existing allauth i18n key; the breadcrumb leaf item uses the same string.- Q: How should action buttons/links be placed inside the `mfa/index.html` method panels, and which card component pattern applies to form-based MFA templates? → A: `<c-card title="...">` for overview panels — action buttons placed in the **card body** below the status text (NOT in `<c-slot name="actions">`); primary action buttons use `variant="primary"`. `<c-form.card>` for form-based templates — submit buttons placed in `<c-slot name="form_actions">` (not `actions`).
- Q: Which content block MUST the WebAuthn management templates (FR-007–010) use after the base fix? → A: `{% block page.content %}` — same block required by all other DAC management templates; `dac/base.html` renders the card-stack via this block.
- Q: Should `mfa/recovery_codes/index.html` use a Cotton form component or a raw `<textarea>` element to render the unused codes? → A: `<c-dac.form-field>` — use `type="textarea"` with `id="recovery_codes"`, `readonly`, and `rows` passed via attrs, and place recovery code strings in the default slot; the `<c-dac.form-field>` component was extended to support a textarea content slot (Research Decision 3 in plan.md).
- Q: Should the Download and Generate buttons in `mfa/recovery_codes/index.html` go in the `<c-card>` `actions` slot (header toolbar) or inside the card body below the textarea? → A: Inside the card body — buttons rendered below the textarea in the default card slot, following the "view then act" linear flow of the original template.
- Q: How many page states should Playwright screenshot tests cover? → A: All distinct user-facing views in the MFA management flow × 2 viewports (desktop + mobile) = 22 PNGs. Every rendered template state a user may encounter is captured: MFA overview × 2 states, TOTP activate form, TOTP deactivate form, recovery codes view, recovery codes generate confirmation, WebAuthn key list × 2 states (with keys, empty), WebAuthn add form, WebAuthn edit form, WebAuthn remove confirmation.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: `mfa/base_manage.html` MUST extend `dac/base.html` (not `allauth/layouts/manage.html`). This single-line change propagates the DAC layout to all nine templates that inherit through this base without requiring changes to the sub-base files (`mfa/totp/base.html`, `mfa/recovery_codes/base.html`, `mfa/webauthn/base.html`).

- **FR-002**: `mfa/index.html` MUST be fully rewritten as a clean Cotton template. It MUST override `{% block title %}` with `{% trans "Two-Factor Authentication" %}`, append a "Two-Factor Authentication" item to `{% block page.breadcrumbs %}`, and place all content inside `{% block page.content %}` (not `{% block content %}`). The three method panels (TOTP, Security Keys, Recovery Codes) MUST each be rendered as an individual `<c-card title="...">` — the `title` attribute supplies the panel heading, and action buttons MUST be placed in the card body below the status text (NOT in `<c-slot name="actions">`). Primary action buttons (Activate, View, Manage) MUST use `variant="primary"`; Deactivate uses `variant="danger"`. The Recovery Codes View and Download buttons MUST only render when `is_mfa_enabled and authenticators.recovery_codes`; the Generate button renders unconditionally. The recovery codes counter MUST use `authenticators.recovery_codes.get_unused_codes|length` and `authenticators.recovery_codes.generate_codes|length`. Each panel MUST only render when its method appears in `MFA_SUPPORTED_TYPES`. The full rewrite is warranted because the existing template uses `{% block content %}` and allauth `{% element %}` tags throughout.

- **FR-003**: `mfa/totp/activate_form.html` MUST be fully rewritten as a clean Cotton template. It MUST use `<c-form.card>` POSTing to `{% url 'mfa_activate_totp' %}`. The QR code image MUST be centered inside a `<div class="text-center mb-3">` wrapper with `style="max-width: 220px"`. The authenticator secret MUST be rendered inline via `{% blocktrans with secret=form.secret.value %}`. The TOTP code input MUST be rendered via `<c-dac.form-field>` using explicit field attributes from `form.code` (id, name, label, autocomplete, placeholder); field validation errors are displayed via `invalid-feedback d-block`. The submit button MUST be placed in `<c-slot name="form_actions">` with `variant="primary"`.

- **FR-004**: `mfa/totp/deactivate_form.html` MUST be fully rewritten as a clean Cotton template. It MUST use `<c-form.card>` POSTing to `{% url 'mfa_deactivate_totp' %}` with `:form-obj="form"`. The submit button MUST be placed in `<c-slot name="form_actions">` as `<c-button variant="danger" type="submit">`.

- **FR-005**: `mfa/recovery_codes/index.html` MUST be fully rewritten as a clean Cotton template extending `mfa/recovery_codes/base.html`. All content MUST be placed inside `{% block page.content %}`. The unused/total count text MUST use `{% blocktranslate %}` as in the original. When `can_view_codes=True`, the unused codes MUST be rendered using `<c-dac.form-field type="textarea" id="recovery_codes" readonly rows="...">` with the recovery code strings placed in the default slot — `id="recovery_codes"` is a hard dependency of `mfa/js/recovery_codes.js` and MUST be preserved exactly. Download and Generate `<c-button>` components MUST be rendered below the textarea inside the card body (not in the `actions` slot), conditional on `can_download_codes` and `can_generate_codes` respectively, following the original template's "view then act" linear flow. When `MFA_RECOVERY_CODES_SHOW_ONCE` and `can_view_codes` are both True, a "I have saved my recovery codes" checkbox with `id="codes_saved"` MUST be rendered. The `{% block extra_js %}` block MUST include the recovery codes JavaScript (preserving `block.super`).

- **FR-006**: `mfa/recovery_codes/generate.html` MUST be fully rewritten as a clean Cotton template extending `mfa/recovery_codes/base.html`. The confirmation text block MUST conditionally include the invalidation warning when `unused_code_count > 0`. The form MUST use `<c-form.card>` POSTing to `{% url 'mfa_generate_recovery_codes' %}` with an explicit `{% csrf_token %}`. The submit button MUST be placed in `<c-slot name="form_actions">` as a single `<c-button>` with an inline conditional variant: `variant="danger"` when `unused_code_count > 0`, and `variant="primary"` otherwise.

- **FR-007**: `mfa/webauthn/authenticator_list.html` MUST be fully rewritten as a clean Cotton template extending `mfa/webauthn/base.html`. All content MUST be placed inside `{% block page.content %}` (not `{% block content %}`). When authenticators are present, they MUST be rendered in a Bootstrap table (`<table class="table mb-3">`) with columns for key name, type badge, and actions. The key name MUST be read from `wrapped.name` inside a `{% with wrapped=authenticator.wrap %}` block. Type badges MUST use `<c-badge>` with variant `primary` for passkeys, `secondary` for security keys, and `warning` for unspecified. Edit and Remove actions MUST use a `<c-dropdown icon="three-dots" :caret="False" align="end">` with `<c-dropdown.item>` children — Edit as a plain link item and Remove with `class="link-danger"` and `icon="delete"`. The "Add" button MUST be placed in the card body (NOT in a card-header slot) with `variant="primary"`. When no authenticators are registered, an informational message paragraph MUST be shown.

- **FR-008**: `mfa/webauthn/add_form.html` MUST be rewritten replacing `{% element %}` / `{% slot %}` / `{% endelement %}` tags with Cotton equivalents. All content MUST be placed inside `{% block page.content %}` (not `{% block content %}`). The submit button MUST use `<c-slot name="form_actions">` with `variant="primary"` and MUST retain `id="mfa_webauthn_add"`. The `passwordless` field (when present — only when `PASSKEY_LOGIN_ENABLED`) MUST be rendered as Bootstrap `form-check` markup with `class="form-check-input"` on the input, a `<label class="form-check-label">` for the field label, and a `<div class="form-text">` for the help text — NOT as a raw `{{ form.passwordless }}` widget. The `{% include "mfa/webauthn/snippets/scripts.html" %}`, `{{ js_data|json_script:"js_data" }}` script, and `<script data-allauth-onload="allauth.webauthn.forms.addForm">` block MUST be preserved exactly.

- **FR-009**: `mfa/webauthn/edit_form.html` MUST be rewritten replacing `{% element %}` / `{% slot %}` / `{% endelement %}` tags with Cotton equivalents. All content MUST be placed inside `{% block page.content %}` (not `{% block content %}`). The form MUST POST to `{% url 'mfa_edit_webauthn' authenticator.pk %}` and render the key name field via `:form-obj="form"` on the `<c-form.card>` component. The submit button MUST be placed in `<c-slot name="form_actions">` with `variant="primary"`.

- **FR-010**: `mfa/webauthn/authenticator_confirm_delete.html` MUST be rewritten replacing `{% element %}` / `{% slot %}` / `{% endelement %}` tags with Cotton equivalents. All content MUST be placed inside `{% block page.content %}` (not `{% block content %}`). The form MUST POST to `{% url 'mfa_remove_webauthn' pk=authenticator.pk %}` with an explicit `{% csrf_token %}`. The confirmation message MUST use `authenticator.wrap.name` (not `authenticator.name`). The submit button MUST be placed in `<c-slot name="form_actions">` with `variant="danger"`.

- **FR-011**: All user-visible strings in every rewritten template MUST be wrapped in `{% trans %}` or `{% blocktrans %}` for internationalisation, consistent with existing DAC addon templates.

- **FR-012**: All allauth `{% element %}`, `{% endelement %}`, and `{% slot %}` tags MUST be eliminated from all rewritten templates and replaced with Cotton components or standard HTML. Compliance is verified by a post-implementation grep over the modified files (SC-002).

- **FR-013**: Integration tests covering the acceptance scenarios for US1–US4 MUST be added to `tests/test_addons/test_allauth/test_mfa_management_view.py`.

### Key Entities

- **Authenticator**: An allauth model representing an active MFA authenticator. Relevant types: `TOTP` (single instance), `RECOVERY_CODES` (single instance), `WEBAUTHN` (list). The `authenticators` context variable in `mfa/index.html` is a dict keyed by type; `authenticators.totp`, `authenticators.recovery_codes`, and `authenticators.webauthn` are the keys used in templates.
- **ActivateTOTPForm**: The allauth form for activating TOTP. Contains a single `code` field for the verification code. The `totp_svg_data_uri` and `form.secret` context variables supply the QR code image and secret respectively.
- **ManageRecoveryCodesForm**: The allauth form used in the generate page (empty — only CSRF required). The `unused_code_count` context variable indicates how many existing codes would be invalidated.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: `mfa/index.html` renders with the DAC Account Center sidebar, "Two-Factor Authentication" heading text rendered via `{% block title %}`, "Account Center" root breadcrumb, and "Two-Factor Authentication" leaf breadcrumb present, verified by automated integration tests.

- **SC-002**: All allauth `{% element %}`, `{% endelement %}`, and `{% slot %}` tags are eliminated from all nine rewritten templates (`mfa/index.html`, `mfa/totp/activate_form.html`, `mfa/totp/deactivate_form.html`, `mfa/recovery_codes/index.html`, `mfa/recovery_codes/generate.html`, `mfa/webauthn/authenticator_list.html`, `mfa/webauthn/add_form.html`, `mfa/webauthn/edit_form.html`, `mfa/webauthn/authenticator_confirm_delete.html`), verified by a grep over the modified template files.

- **SC-003**: The automated test suite passes with zero failures for the new `test_mfa_management_view.py` module, covering at minimum the acceptance scenarios for each user story (US1–US4).

- **SC-004**: A developer can verify the correct rendering of every conditional branch (TOTP active/inactive, recovery codes set up/empty, WebAuthn keys present/absent, `MFA_SUPPORTED_TYPES` variations, `is_mfa_enabled` True/False) without starting a server — purely from the integration tests.

- **SC-005**: The WebAuthn JavaScript block (`allauth.webauthn.forms.addForm`) and its associated `id="mfa_webauthn_add"` attribute remain unchanged in the rewritten `mfa/webauthn/add_form.html`, verified by a diff of the JavaScript content before and after the rewrite. (`allauth.webauthn.forms.authenticateForm` is used only in out-of-scope reauthentication templates and is not part of this success criterion.)

## Assumptions

- `dac/base.html` (from spec 005) and `account/base_manage.html` (corrected in spec 006) are fully implemented and provide the `page.content`, `title`, `page.breadcrumbs`, and `page.header` blocks.
- The sub-base templates (`mfa/totp/base.html`, `mfa/recovery_codes/base.html`, `mfa/webauthn/base.html`) only need the `extends` fix in `mfa/base_manage.html` to inherit the correct layout; no other changes are required to these sub-base files.
- The allauth context variables (`authenticators`, `MFA_SUPPORTED_TYPES`, `MFA_RECOVERY_CODES_SHOW_ONCE`, `is_mfa_enabled`) are provided by `allauth.mfa.base.views.IndexView`; templates do not need to fetch or transform this data.
- No `<c-table>` Cotton component exists in the project; the WebAuthn authenticator list MUST be rendered using raw Bootstrap HTML (`<table class="table">`) inside a `<c-card>`.
- The Cotton components used in the rewritten templates (`<c-card>`, `<c-badge>`, `<c-button>`, `<c-form>`, `<c-form.card>`, `<c-form.fields>`, `<c-breadcrumbs.item>`) are available through `django-mvp`, `django-cotton-bs5`, or existing DAC custom components.
- The entrance/login-flow MFA templates (`mfa/base_entrance.html`, `mfa/authenticate.html`, `mfa/reauthenticate.html`, `mfa/trust.html`, `mfa/webauthn/reauthenticate.html`, `mfa/webauthn/signup_form.html`) are out of scope for this spec; they are login-flow templates rather than management templates and are addressed separately.
- The `mfa/recovery_codes/download.txt` template is a plain-text download file; it does not use `{% element %}` tags and is out of scope.
- Screenshots are required per Constitution Principle XIII (Multi-Viewport Screenshot Coverage); pytest-playwright screenshot tests covering all distinct user-facing page states × 2 viewports = 22 PNGs are written as part of this feature and live in the root `screenshots/` directory. The 11 page states are: (1) MFA overview with TOTP active + recovery codes set up, (2) MFA overview with nothing active, (3) TOTP activate form, (4) TOTP deactivate confirmation, (5) recovery codes view, (6) recovery codes generate confirmation, (7) WebAuthn key list with registered keys, (8) WebAuthn key list empty state, (9) WebAuthn add form, (10) WebAuthn edit form, (11) WebAuthn remove confirmation. Each state is captured at desktop 1440×900 and mobile 390×844.
- The existing allauth URL names (`mfa_index`, `mfa_activate_totp`, `mfa_deactivate_totp`, `mfa_view_recovery_codes`, `mfa_download_recovery_codes`, `mfa_generate_recovery_codes`, `mfa_list_webauthn`, `mfa_add_webauthn`, `mfa_edit_webauthn`, `mfa_remove_webauthn`) are registered by allauth when `allauth.mfa` is in `INSTALLED_APPS`; templates may use them freely.
