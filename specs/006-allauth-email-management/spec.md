# Feature Specification: Allauth Email Management Templates

**Feature Branch**: `006-allauth-email-management`
**Created**: 2026-05-12
**Status**: Draft

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Developer Wires Email Templates into the DAC Layout (Priority: P1) **[Developer]**

A developer enabling allauth email management in their DAC-based project expects all email-management pages (the email address list, the email change form, and the "verified email required" gate page) to inherit the same DAC management layout — Account Center sidebar, breadcrumb trail rooted at "Account Center", and consistent card-stack content area — without writing any structural HTML. They do this by installing `dac.addons.allauth` and defining the allauth email URL patterns; the override templates handle the rest.

**Why this priority**: The template inheritance chain (`base_manage.html` → `dac/base.html`) is the load-bearing structure that every other email template depends on. If the chain is broken, no email management page renders in the DAC UI. All other stories and requirements are blocked until this is correct.

**Independent Test**: Can be tested by rendering each email management template in isolation using Cotton rendering tests and asserting that the DAC sidebar, breadcrumbs, and card-stack are present in the output.

**Acceptance Scenarios**:

1. **Given** the template `account/base_manage.html` in the DAC addon, **When** it is rendered as a base template, **Then** it extends `dac/base.html` (not `allauth/layouts/manage.html`), inheriting the full DAC management layout.
2. **Given** a page that extends through `account/base_manage_email.html` → `account/base_manage.html`, **When** rendered, **Then** the Account Center sidebar, breadcrumb trail, and card-stack content area are all present.
3. **Given** `account/email_change.html`, **When** rendered, **Then** its content appears inside the `page.content` block (not the generic `content` block), placing it within the card-stack.
4. **Given** `account/verified_email_required.html`, **When** rendered, **Then** its content also appears inside the `page.content` block within the DAC management layout.

---

### User Story 2 — End User Manages Email Addresses with a Consistent UI (Priority: P2) **[End User]**

A logged-in user navigates to the "Manage email" page, which displays a list of their email addresses with badge indicators for primary/verified status and a per-address actions dropdown. If they have fewer emails than the allowed maximum, an "Add email" form is shown below the list. From the same menu they can navigate to the email change page. On every email management page they see the same sidebar, the same breadcrumb trail, and the same card-stack layout as all other DAC management pages.

**Why this priority**: This is the primary end-user value of the feature — consistent, accessible management of email addresses within the DAC UI shell. Without this, users see raw allauth markup disconnected from the rest of the account centre.

**Independent Test**: Can be tested by rendering `account/email.html` and `account/email_change.html` with representative context objects (email address list, form) and asserting badge indicators, action buttons, and form fields are present with the correct structure.

**Acceptance Scenarios**:

1. **Given** a user with two email addresses (one primary/verified, one unverified), **When** `account/email.html` is rendered, **Then** both addresses appear in a list with "Primary" and "Verified"/"Unverified" badges, and a three-dots dropdown per address for per-address actions.
2. **Given** a user who has not reached the maximum email count, **When** `account/email.html` is rendered with `can_add_email=True`, **Then** an "Add email" form with a submit button appears below the email list.
3. **Given** a user with no email addresses on file, **When** `account/email.html` is rendered with `emailaddresses=[]`, **Then** the warning snippet `account/snippets/warn_no_email.html` is included instead of the list.
4. **Given** a user who is changing their email and has a pending (unverified) new address, **When** `account/email_change.html` is rendered, **Then** the pending address is shown as disabled with a "Re-send Verification" button and (if a current address also exists) a "Cancel Change" button.
5. **Given** a user who is blocked because their email is unverified, **When** `account/verified_email_required.html` is rendered, **Then** a card explains that verification is required and includes a link to the email management page.

---

### User Story 3 — Developer Verifies Templates via Automated Cotton Tests (Priority: P3) **[Developer]**

A developer running the test suite expects all email management template overrides to be covered by Cotton rendering tests. The tests prove that the correct components are rendered (badges, dropdowns, forms, buttons) for each branch of the email management logic (has emails, no emails, can add, pending change, etc.).

**Why this priority**: Without automated tests, regressions in the template inheritance chain or component usage go undetected until a browser. Tests also document the expected context variables and rendering branches for future maintainers.

**Independent Test**: Running `pytest tests/test_addons/test_allauth/test_email_management_view.py --no-cov` passes with 0 failures. Each test targets a specific acceptance scenario from US1 and US2.

**Acceptance Scenarios**:

1. **Given** a test that renders `account/email.html` with a list of email addresses, **When** the test asserts that the rendered output contains badge elements and a dropdown component, **Then** the assertions pass.
2. **Given** a test that renders `account/email_change.html` with a pending email address, **When** the test asserts that "Re-send Verification" and "Cancel Change" buttons are present, **Then** the assertions pass.
3. **Given** a test that renders `account/verified_email_required.html`, **When** the test asserts that the page content explains verification is required and links to `account_email`, **Then** the assertions pass.

---

### Edge Cases

- What happens when a user has exactly the maximum allowed number of email addresses? The `can_add_email` flag is `False`, so the "Add email" form must not render; only the list and per-address dropdowns are shown.
- What happens when an email address is both primary and unverified? Both the "Primary" and "Unverified" badges appear together; no per-address "Make primary" action is shown (it is already primary), but "Re-send verification" is shown.
- What happens when a primary email address is targeted by the remove action? The remove button is rendered with a `disabled` CSS class so the user cannot accidentally delete their primary address.
- What happens when `account/email_change.html` is rendered with neither `current_emailaddress` nor `new_emailaddress`? Only the change-to form field and submit button render; no current/pending address rows appear.
- What happens when `verified_email_required.html` is accessed but the `account_email` URL is not registered? A `NoReverseMatch` is raised at render time — correct allauth URL configuration is a host-project responsibility, not a template defect.

## Clarifications

### Session 2026-05-12

- Q: Should `email_change.html` keep its indirect inheritance chain (`email_change.html → base_manage_email.html → base_manage.html → dac/base.html`) or be converted to extend `dac/base.html` directly? → A: Keep the indirect chain — only `base_manage.html` needs its `extends` line changed.
- Q: Should `verified_email_required.html` wrap its paragraphs in an explicit `<c-card>` inside `{% block page.content %}`, or place them directly in the block and rely on the base `card.stack` for structure? → A: Wrap in an explicit `<c-card>` — consistent with other DAC management pages.
- Q: Should `email.html` receive a full Cotton rewrite or only corrections? → A: Corrections only — only functional errors in the management flow are fixed (e.g. wrong button `name` values, incorrect form actions). Cosmetic or structural Cotton improvements that do not affect behaviour are out of scope.
- Q: Should `email_change.html` keep `<c-form.card>` or switch to nested `<c-form>` + `<c-card>`? → A: Keep `<c-form.card>` — it is the preferred wrapper for management-page forms. Nested `<c-form>` + `<c-card>` is only acceptable when `<c-form.card>` cannot provide the required functionality.
- Q: Should `email_change.html` receive only a block-name fix or a full rewrite? → A: Full rewrite — its `{% block content %}` defect means it never rendered inside the DAC layout; a clean Cotton structure is warranted.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: `account/base_manage.html` MUST extend `dac/base.html` (not `allauth/layouts/manage.html`). This single change propagates the DAC layout to all templates that inherit through this base without requiring changes to `base_manage_email.html` or `email_change.html`.
- **FR-002**: `account/base_manage_email.html` MUST continue to extend `account/base_manage.html` unchanged, preserving the full indirect chain (`email_change.html → base_manage_email.html → base_manage.html → dac/base.html`). No content changes are required to this file.
- **FR-003**: `account/email.html` MUST be corrected where it deviates from functional correctness — specifically: each per-address form action MUST target `{% url "account_email" %}`, each action button MUST submit the correct `name` attribute (`action_primary`, `action_send`, `action_remove`, `action_add`), and page content MUST reside in `{% block page.content %}`. The buttons `action_send` and `action_primary` MUST always be present in the rendered dropdown markup for every email address, regardless of whether that address is verified or primary — they MUST NOT be conditionally omitted via `{% if %}` guards that hide them for certain address states. Cosmetic or structural changes that do not affect the management flow are out of scope.
- **FR-004**: `account/email.html` MUST render each email address using Cotton badge components for primary/verified status and a Cotton dropdown component for per-address actions (Make primary, Re-send verification, Remove). These are already present; any deviation from this structure that breaks the management flow MUST be corrected.
- **FR-005**: `account/email.html` MUST conditionally render an "Add email" Cotton form below the email list only when `can_add_email` is `True`. This behaviour MUST be preserved through any corrections.
- **FR-006**: `account/email_change.html` MUST be fully rewritten as a clean Cotton template. It MUST override `{% block title %}` with the localised "Email Address" string, append an "Email Address" item to `{% block page.breadcrumbs %}`, and place all form content inside `{% block page.content %}` (not `{% block content %}`). A full rewrite is warranted because the existing template's `{% block content %}` override means its form never rendered inside the DAC management layout.
- **FR-007**: The rewritten `account/email_change.html` MUST use `<c-form.card>` as the form wrapper (the preferred component for management-page forms) and `<c-button>` / `<c-button.stack>` for actions. It MUST render: a disabled current-email field when `current_emailaddress` is set, a disabled pending-address field with "Re-send Verification" and (conditionally) "Cancel Change" buttons when `new_emailaddress` is set, and the change-to email form field. No raw allauth `{% element %}` tags are permitted.
- **FR-008**: `account/verified_email_required.html` MUST use `{% block page.content %}` (not `{% block content %}`), override `{% block title %}`, and wrap its explanatory paragraphs in an explicit `<c-card>` component inside `page.content`, matching the card-surface pattern used by all other DAC management pages.
- **FR-009**: `account/verified_email_required.html` MUST include a link to the email management page (`account_email` URL) within the card body, allowing users to navigate directly to their email settings.
- **FR-010**: All user-visible strings in every template MUST be wrapped in `{% trans %}` or `{% blocktrans %}` for internationalisation.
- **FR-011**: Integration tests covering the acceptance scenarios for US1, US2, and US3 MUST be added to `tests/test_addons/test_allauth/test_email_management_view.py`.

### Key Entities

- **EmailAddress**: An allauth model representing a user's email address. Key attributes relevant to rendering: `email` (string), `primary` (bool), `verified` (bool).
- **EmailAddressRadio**: A context object provided by the `EmailView` combining an `EmailAddress` with a radio-button `checked` state and a unique `id`. Used only in `email.html`.
- **AddEmailForm**: The allauth form for adding a new email address. Rendered with a single email field and an action button.
- **ChangeEmailForm**: The allauth form for changing the primary email address. Rendered with a single email field and an action button.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: All three email management templates (`email.html`, `email_change.html`, `verified_email_required.html`) render with the DAC Account Center sidebar and "Account Center" root breadcrumb present, verified by automated Cotton rendering tests that assert these structural elements.
- **SC-002**: All allauth `{% element %}` and `{% endelement %}` / `{% slot %}` tags are eliminated from the three email management templates and replaced with equivalent Cotton components, verified by a grep over the override template files.
- **SC-003**: The automated test suite passes with zero failures for the new `test_email_management_view.py` module, covering at minimum the acceptance scenarios for each user story (US1–US3).
- **SC-004**: A developer can verify the correct rendering of every conditional branch (no emails, can add email, pending email change, verified-email-required gate) without starting a server — purely from the Cotton rendering tests.

## Assumptions

- `dac/base.html` (from spec 005) is fully implemented and provides the `page.content`, `title`, `page.breadcrumbs`, and `page.header` blocks consumed by these email management templates.
- The allauth context variables (`emailaddresses`, `emailaddress_radios`, `can_add_email`, `current_emailaddress`, `new_emailaddress`, `form`) are provided by the corresponding allauth views; the templates do not need to fetch or transform this data.
- The Cotton components used by `email.html` and `email_change.html` (`c-badge`, `c-dropdown`, `c-dropdown.item`, `c-card`, `c-list-group`, `c-list-group.item`, `c-form.card`, `c-form`, `c-button`, `c-button.stack`) are available through `django-mvp`, `django-cotton-bs5`, or existing DAC custom components. `c-form.card` is the preferred form wrapper for management pages; `c-form` is the fallback when `c-form.card` lacks the needed functionality.
- The `account_email` URL is registered by allauth when `allauth.account` is in `INSTALLED_APPS`; templates may use `{% url "account_email" %}` freely.
- The existing JavaScript files (`account/js/account.js`, `account/js/onload.js`) required for the delete-confirmation modal in `email.html` are provided by allauth and are loaded via `{% block extra_js %}` — this is intentional and not a violation of the Cotton-only requirement.
- Screenshots are out of scope for this spec; visual verification is done via Playwright tests in a separate screenshot module if required by the project constitution.
- The `email.html` template already extends `dac/base.html` and uses Cotton components. Only functional correctness errors in the management flow are in scope (e.g. wrong button `name` values, incorrect form `action` URLs). Structural or cosmetic refactoring is explicitly out of scope.
