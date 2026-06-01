# Feature Specification: Allauth Password Change Templates

**Feature Branch**: `007-allauth-password-change`
**Created**: 2026-05-12
**Status**: Draft

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Developer Wires Password Management Templates into the DAC Layout (Priority: P1) **[Developer]**

A developer enabling allauth password management in their DAC-based project expects both the "Change Password" page and the "Set Password" page to inherit the full DAC management layout — Account Center sidebar, breadcrumb trail rooted at "Account Center", and consistent card-stack content area — without writing any structural HTML. They do this by installing `dac.addons.allauth` and defining the allauth password URL patterns; the override templates handle the rest.

**Why this priority**: `password_change.html` and `password_set.html` both currently override `{% block content %}` instead of `{% block page.content %}`. This means their form content is placed outside the DAC card-stack, and the page renders without the expected sidebar and breadcrumb structure. Correcting this unblocks both end-user stories and all downstream rendering.

**Independent Test**: Can be tested by rendering each password management template in isolation using Cotton rendering tests and asserting that the DAC sidebar, breadcrumbs, and card-stack are present in the output.

**Acceptance Scenarios**:

1. **Given** `account/base_manage_password.html` in the DAC addon, **When** it is rendered as a base template, **Then** it extends `account/base_manage.html` (and transitively `dac/base.html`), inheriting the full DAC management layout.
2. **Given** `account/password_change.html`, **When** rendered, **Then** its form content appears inside the `page.content` block (not the generic `content` block), placing it within the card-stack of the DAC management layout.
3. **Given** `account/password_set.html`, **When** rendered, **Then** its form content also appears inside the `page.content` block within the DAC management layout.
4. **Given** `account/password_change.html`, **When** rendered, **Then** the breadcrumb trail includes an "Account Center" root item and a "Change Password" leaf item.
5. **Given** `account/password_set.html`, **When** rendered, **Then** the breadcrumb trail includes an "Account Center" root item and a "Set Password" leaf item.

---

### User Story 2 — End User Changes or Sets Their Password with a Consistent UI (Priority: P2) **[End User]**

A logged-in user navigates to the "Change Password" page (or "Set Password" page, if they authenticated via a social provider and have no password yet) and sees a clean form rendered within the same DAC card-stack and sidebar layout as all other account management pages. They fill in the form fields, submit, and the action is processed by the standard allauth view.

**Why this priority**: This is the primary end-user value — password self-service that is visually integrated with the rest of the account centre. Without this, users see raw allauth markup disconnected from the DAC UI shell.

**Independent Test**: Can be tested by rendering `account/password_change.html` and `account/password_set.html` with representative form contexts and asserting that the expected form fields, submit button, and (for change) the "Forgot Password?" link are present with the correct structure.

**Acceptance Scenarios**:

1. **Given** a logged-in user with a password on `account/password_change.html`, **When** the page is rendered, **Then** a form with current-password, new-password, and new-password-confirmation fields is displayed inside a `<c-form.card>` wrapper.
2. **Given** a logged-in user on `account/password_change.html`, **When** the page is rendered, **Then** a "Change Password" submit button and a "Forgot Password?" link are present.
3. **Given** a logged-in user without a password (social-only account) on `account/password_set.html`, **When** the page is rendered, **Then** a form with new-password and new-password-confirmation fields is displayed inside a `<c-form.card>` wrapper.
4. **Given** a logged-in user on `account/password_set.html`, **When** the page is rendered, **Then** a "Set Password" submit button is present (no "Forgot Password?" link).
5. **Given** either password management page, **When** rendered, **Then** no allauth `{% element %}` or `{% endelement %}` tags appear in the rendered output.

---

### User Story 3 — Reauthentication Gate Renders as a Cotton Entrance-Style Page (Priority: P2) **[Developer]**

A developer configuring allauth reauthentication (triggered when a user tries to change their password without a recent login) expects both `account/base_reauthenticate.html` and `account/reauthenticate.html` to render using Cotton components within the entrance layout — no allauth `{% element %}` tags, consistent with all other entrance-layout templates in the DAC addon.

**Why this priority**: `base_reauthenticate.html` is the structural base for the reauthentication gate. It currently uses allauth `{% element %}` tags throughout its body. Rewriting it with Cotton components ensures the reauthentication UX is consistent with other entrance pages (login, signup) and eliminates the last allauth element tags in the entrance template chain.

**Independent Test**: Can be tested by rendering `account/reauthenticate.html` with a representative form context and asserting that the "Confirm Access" heading, introductory paragraph, password field, and "Confirm" submit button are present as Cotton-component output.

**Acceptance Scenarios**:

1. **Given** `account/base_reauthenticate.html`, **When** rendered, **Then** it extends `account/base_entrance.html` and produces a "Confirm Access" heading and introductory paragraph using Cotton components (no `{% element %}` tags).
2. **Given** `account/reauthenticate.html`, **When** rendered with a reauthentication form, **Then** a password input and a "Confirm" submit button are present, rendered via Cotton form components inside the `reauthenticate_content` block.
3. **Given** `account/reauthenticate.html` rendered with `reauthentication_alternatives` context, **Then** an "Alternative options" section appears below the form, with each alternative rendered as a Cotton button linking to its URL.
4. **Given** `account/reauthenticate.html` rendered without `reauthentication_alternatives`, **Then** no "Alternative options" section is present.

---

### User Story 4 — Developer Verifies Templates via Automated Integration Tests (Priority: P3) **[Developer]**

A developer running the test suite expects all password change and reauthentication template overrides to be covered by integration tests. The tests prove that the correct components are rendered (form fields, buttons, headings) for each template and form state.

**Why this priority**: Without automated tests, regressions in block names or Cotton component usage go undetected until a browser. Tests also document the expected context variables for future maintainers.

**Independent Test**: Running `pytest tests/test_addons/test_allauth/test_password_change_view.py --no-cov` passes with zero failures. Each test targets a specific acceptance scenario from US1–US3. The `reauthentication_alternatives` state uses `cotton_render_string` (Principle I) since no live URL exposes this state without real MFA configuration.

**Acceptance Scenarios**:

1. **Given** a test that renders `account/password_change.html` with a change-password form, **When** the test asserts that the DAC sidebar, breadcrumbs, form fields, and "Change Password" button are present, **Then** the assertions pass.
2. **Given** a test that renders `account/password_set.html` with a set-password form, **When** the test asserts that the form fields and "Set Password" button are present and no "Forgot Password?" link appears, **Then** the assertions pass.
3. **Given** a test that renders `account/reauthenticate.html` with a reauthentication form, **When** the test asserts that the password field and "Confirm" button are present, **Then** the assertions pass.
4. **Given** a test that renders `account/reauthenticate.html` with `reauthentication_alternatives`, **When** the test asserts that the "Alternative options" section appears, **Then** the assertion passes.

---

### Edge Cases

- What happens when `password_change.html` is rendered for a social-only user who has no password? Allauth prevents access to the change-password URL for passwordless accounts (redirecting to `password_set`); the template itself does not need to handle this case.
- What happens when form validation fails on `password_change.html`? Allauth re-renders the template with form errors; the Cotton form components render field errors inline — no special handling is required in the template.
- What happens when form validation fails on `password_set.html`? Same as above — Cotton form components render validation errors inline.
- What happens when `reauthentication_alternatives` is an empty list? The `{% if reauthentication_alternatives %}` guard prevents the "Alternative options" section from rendering; an empty list and a missing variable behave identically.
- What happens when `password_change.html` is accessed without authentication? Allauth's login-required decorator redirects the user; the template is never rendered.

## Clarifications

### Session 2026-05-12

- Q: Should `password_change.html` and `password_set.html` receive corrections only, or a full Cotton rewrite? → A: Full rewrite — both templates use `{% block content %}` (instead of `{% block page.content %}`) and `{% element %}` tags. A clean Cotton structure is warranted.
- Q: Should `password_change.html` keep `<c-form.card>` or use nested `<c-form>` + `<c-card>`? → A: Use `<c-form.card>` — it is the preferred wrapper for management-page forms, consistent with `email_change.html` in spec 006.
- Q: Should the reauthentication templates (`base_reauthenticate.html`, `reauthenticate.html`) be in scope for this spec? → A: Yes — they use allauth `{% element %}` tags and are part of the password-change workflow. Rewriting them as Cotton components completes the password-related template set.
- Q: Are MFA reauthentication templates (`mfa/reauthenticate.html`, `mfa/webauthn/reauthenticate.html`) in scope? → A: No — they are MFA-specific and will be addressed in a dedicated MFA template spec. Only `account/reauthenticate.html` and `account/base_reauthenticate.html` are in scope here.
- Q: Should `base_manage_password.html` be modified? → A: No — it already correctly extends `account/base_manage.html` with no content. It is tested but not changed.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: `account/base_manage_password.html` MUST continue to extend `account/base_manage.html` with no additional content. This file is already correct; it is verified by a rendering test but not modified.
- **FR-002**: `account/password_change.html` MUST be fully rewritten as a clean Cotton template. It MUST override `{% block title %}` with the localised "Change Password" string, append a "Change Password" item to `{% block page.breadcrumbs %}`, and place all form content inside `{% block page.content %}` (not `{% block content %}`). A full rewrite is warranted because the existing template's `{% block content %}` override means its form never renders inside the DAC management layout.
- **FR-003**: `account/password_set.html` MUST be fully rewritten as a clean Cotton template following the same structure as `password_change.html`. It MUST override `{% block title %}` with the localised "Set Password" string, append a "Set Password" breadcrumb, and place all form content inside `{% block page.content %}`.
- **FR-004**: The rewritten `account/password_change.html` MUST use `<c-form.card>` as the form wrapper and `<c-button>` for the submit action. It MUST render all fields from the change-password form (current password, new password, new-password confirmation) and include a "Forgot Password?" link pointing to `{% url 'account_reset_password' %}`. No raw allauth `{% element %}` tags are permitted.
- **FR-005**: The rewritten `account/password_set.html` MUST use `<c-form.card>` as the form wrapper and `<c-button>` for the submit action. It MUST render all fields from the set-password form (new password, new-password confirmation). No "Forgot Password?" link is present. No raw allauth `{% element %}` tags are permitted.
- **FR-006**: `account/base_reauthenticate.html` MUST be rewritten to replace all allauth `{% element %}` tags with Cotton equivalents. It MUST continue to extend `account/base_entrance.html`, override `{% block content %}`, render a "Confirm Access" heading and introductory paragraph via Cotton components, expose `{% block reauthenticate_content %}` for child templates, and conditionally render an "Alternative options" section (heading + Cotton buttons) when `reauthentication_alternatives` is non-empty.
- **FR-007**: `account/reauthenticate.html` MUST be rewritten to fill `{% block reauthenticate_content %}` with Cotton form components. It MUST render the reauthentication form's password field and a "Confirm" submit button via `<c-form>` and `<c-button>`. No raw allauth `{% element %}` tags are permitted.
- **FR-008**: All user-visible strings in every rewritten template MUST be wrapped in `{% trans %}` or `{% blocktrans %}` for internationalisation, consistent with existing DAC addon templates.
- **FR-009**: All allauth `{% element %}`, `{% endelement %}`, and `{% slot %}` tags MUST be eliminated from the five templates covered by this spec (`password_change.html`, `password_set.html`, `base_reauthenticate.html`, `reauthenticate.html`) and replaced with equivalent Cotton components.
- **FR-010**: Integration tests covering the acceptance scenarios for US1–US4 MUST be added to `tests/test_addons/test_allauth/test_password_change_view.py`.

### Key Entities

- **ChangePasswordForm**: The allauth form for changing a known password. Relevant fields: `oldpassword` (current password), `password1` (new password), `password2` (new-password confirmation). Used by `password_change.html`.
- **SetPasswordForm**: The allauth form for setting a password for a social-only account. Relevant fields: `password1` (new password), `password2` (new-password confirmation). Used by `password_set.html`.
- **ReauthenticateForm**: The allauth form for password-based reauthentication. Contains a single password field. Used by `reauthenticate.html`.
- **reauthentication_alternatives**: A list of alternative reauthentication options (e.g., passkey, MFA code) provided by the allauth view as template context. Each item has `url` and `description` attributes.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Both password management templates (`password_change.html`, `password_set.html`) render with the DAC Account Center sidebar and "Account Center" root breadcrumb present, verified by automated Cotton rendering tests that assert these structural elements.
- **SC-002**: All allauth `{% element %}` and `{% endelement %}` / `{% slot %}` tags are eliminated from the four rewritten templates (`password_change.html`, `password_set.html`, `base_reauthenticate.html`, `reauthenticate.html`) and replaced with Cotton components, verified by a grep over the override template files.
- **SC-003**: The automated test suite passes with zero failures for the new `test_password_change_view.py` module, covering at minimum the acceptance scenarios for each user story (US1–US4).
- **SC-004**: A developer can verify the correct rendering of every form variant (change password, set password, reauthenticate with and without alternatives) without starting a server — purely from the integration tests in `test_password_change_view.py` (HTTP client + `cotton_render_string` for the alternatives-only state).

## Assumptions

- `dac/base.html` (from spec 005) and `account/base_manage.html` (corrected in spec 006) are fully implemented and provide the `page.content`, `title`, `page.breadcrumbs`, and `breadcrumbs` blocks consumed by the password management templates.
- `account/base_entrance.html` is already implemented and extends `allauth/layouts/entrance.html`; only the allauth `{% element %}` tag usage inside `base_reauthenticate.html` and `reauthenticate.html` is in scope — no change to `base_entrance.html` itself is needed.
- The allauth context variables (`form`, `redirect_field`, `reauthentication_alternatives`) are provided by the corresponding allauth views; the templates do not need to fetch or transform this data.
- The Cotton components used by these templates (`<c-form.card>`, `<c-form>`, `<c-button>`, `<c-group>`, `<c-entrance.section>`) are available through `django-mvp`, `django-cotton-bs5`, or existing DAC custom components. `<c-form.card>` is the preferred form wrapper for management pages.
- The `account_reset_password` URL is registered by allauth when `allauth.account` is in `INSTALLED_APPS`; `password_change.html` may use `{% url 'account_reset_password' %}` freely.
- MFA reauthentication templates (`mfa/reauthenticate.html`, `mfa/webauthn/reauthenticate.html`) are explicitly out of scope. They extend `account/base_reauthenticate.html` and will benefit indirectly from the base template rewrite, but their own `{% block reauthenticate_content %}` overrides are addressed in a dedicated MFA template spec.
- Screenshots are out of scope for this spec; visual verification is done via Playwright tests in a separate screenshot module if required by the project constitution.
