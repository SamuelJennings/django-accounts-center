# Feature Specification: Social Account Connections Templates

**Feature Branch**: `009-socialaccount-connections`
**Created**: 2026-05-21
**Status**: In Progress

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Developer Wires Social Account Management into the DAC Layout (Priority: P1) **[Developer]**

A developer enabling allauth social account management in their DAC-based project expects the "Account Connections" page to inherit the full DAC management layout — Account Center sidebar, breadcrumb trail rooted at "Account Center", and consistent card-stack content area — without writing any structural HTML. They do this by installing `dac.addons.allauth` and defining the allauth social account URL patterns; the override templates handle the rest.

**Why this priority**: `socialaccount/base_manage.html` currently extends `allauth/layouts/manage.html` instead of `dac/base.html`. This single deviation means no socialaccount management page ever renders inside the DAC UI shell. Fixing it unblocks the end-user story and all downstream rendering.

**Independent Test**: Can be tested by rendering `socialaccount/connections.html` in isolation using Cotton rendering tests and asserting that the DAC sidebar, breadcrumbs, and card-stack are present in the output.

**Acceptance Scenarios**:

1. **Given** `socialaccount/base_manage.html` in the DAC addon, **When** it is rendered as a base template, **Then** it extends `dac/base.html` (not `allauth/layouts/manage.html`), inheriting the full DAC management layout.
2. **Given** `socialaccount/connections.html` which extends through `socialaccount/base_manage.html`, **When** rendered, **Then** the Account Center sidebar, breadcrumb trail, and card-stack content area are all present.
3. **Given** `socialaccount/connections.html`, **When** rendered, **Then** its content appears inside `{% block page.content %}` (not the generic `{% block content %}`), placing it within the card-stack.

---

### User Story 2 — End User Manages Connected Social Accounts with a Consistent UI (Priority: P2) **[End User]**

A logged-in user navigates to the "Account Connections" page, which lists all their connected third-party accounts with a disconnect option for each, and shows a section for adding new connections to other providers. On the page they see the same sidebar, the same breadcrumb trail, and the same card-stack layout as all other DAC management pages.

**Why this priority**: This is the primary end-user value of the feature — visual integration of social account self-service within the DAC UI shell. Without the base template fix, the user sees raw allauth markup disconnected from the rest of the account centre.

**Independent Test**: Can be tested by rendering `socialaccount/connections.html` with representative context objects (a list of connected accounts, an empty-connections state) and asserting that the provider badges, remove form, empty-state message, and provider-list section are present with the correct structure.

**Acceptance Scenarios**:

1. **Given** a user with one connected social account, **When** `socialaccount/connections.html` is rendered, **Then** the account appears in a list with a provider badge and a "Remove" button to disconnect it.
2. **Given** a user with no connected social accounts, **When** `socialaccount/connections.html` is rendered with an empty `form.accounts`, **Then** an informational message is shown stating no accounts are connected, and the "Add a Third-Party Account" section is still rendered.
3. **Given** any logged-in user, **When** `socialaccount/connections.html` is rendered, **Then** the "Add a Third-Party Account" section includes the provider list (via `socialaccount/snippets/provider_list.html`) and no allauth `{% element %}` tags appear in the rendered output.
4. **Given** `socialaccount/authentication_error.html`, **When** rendered, **Then** a heading and explanatory paragraph are present using Cotton components (no `{% element %}` tags).

---

### User Story 3 — Developer Verifies Templates via Automated Cotton Tests (Priority: P3) **[Developer]**

A developer running the test suite expects all social account management template overrides to be covered by Cotton rendering tests. The tests prove that the correct components are rendered (provider badges, remove form, empty-state message, error page) for each branch of the social account management logic.

**Why this priority**: Without automated tests, regressions in block names or Cotton component usage go undetected until a browser. Tests also document the expected context variables for future maintainers.

**Independent Test**: Running `pytest tests/test_addons/test_allauth/test_social_connections_view.py --no-cov` passes with zero failures. Each test targets a specific acceptance scenario from US1 and US2.

**Acceptance Scenarios**:

1. **Given** a test that renders `socialaccount/connections.html` with a list of connected accounts, **When** the test asserts that the DAC sidebar, breadcrumbs, provider badge, and "Remove" button are present, **Then** the assertions pass.
2. **Given** a test that renders `socialaccount/connections.html` with an empty account list, **When** the test asserts that the empty-state message and "Add a Third-Party Account" section are present, **Then** the assertions pass.
3. **Given** a test that renders `socialaccount/authentication_error.html`, **When** the test asserts that the heading and explanatory paragraph are present as Cotton-component output, **Then** the assertions pass.

---

### Edge Cases

- What happens when a user removes their last social account and has no password set? Allauth prevents the disconnect at the view layer; the template itself does not need to handle this case.
- What happens when no social providers are configured? The `socialaccount/snippets/provider_list.html` include renders an empty section; the template renders without error.
- What happens when `socialaccount/authentication_error.html` is rendered without a specific error code? The page renders its static explanatory text regardless; no conditional content depends on error detail.
- What happens when form submission fails on the connections page? Allauth re-renders the page with form errors; the Cotton form components render errors inline — no special template handling is required.

## Clarifications

### Session 2026-05-21

- Q: Should `connections.html` use the original allauth radio-select-then-remove pattern (one shared form) or render a per-account individual form with its own "Remove" button? → A: Per-account individual form — consistent with the per-address pattern used in `email.html` (spec 006).
- Q: Should the connected-accounts list use a `<c-list>` (matching `email.html`) or a separate `<c-card>` per account? → A: `<c-list>` — one list item per account with an inline remove form, mirrors the existing email address list pattern exactly.
- Q: Should the page title and breadcrumb use "Social Account Connections" (new DAC string) or "Account Connections" (matching the allauth original `{% trans "Account Connections" %}`)? → A: "Account Connections" — reuse the allauth i18n key to stay consistent with existing translations.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: `socialaccount/base_manage.html` MUST extend `dac/base.html` (not `allauth/layouts/manage.html`). This single change propagates the DAC layout to all templates that inherit through this base without requiring changes to `connections.html` itself.
- **FR-002**: `socialaccount/connections.html` MUST be fully rewritten as a clean Cotton template. It MUST override `{% block title %}` with `{% trans "Account Connections" %}` (reusing the allauth i18n key), append an "Account Connections" item to `{% block page.breadcrumbs %}`, and place all content inside `{% block page.content %}` (not `{% block content %}`). A full rewrite is warranted because the existing template uses `{% block content %}` and allauth `{% element %}` tags throughout.
- **FR-003**: The rewritten `socialaccount/connections.html` MUST render each connected account as an individual item inside a `<c-list>` wrapper, with one `<c-list.item>` per account. Each list item MUST display a Cotton badge for the provider name and contain an inline Cotton form that POSTs to `{% url 'socialaccount_connections' %}` with the account's `pk` submitted as a hidden field. A "Remove" button rendered via `<c-button>` MUST be present within each item's form. There MUST NOT be a shared radio-select-then-remove form spanning multiple accounts.
- **FR-004**: The rewritten `socialaccount/connections.html` MUST conditionally render an empty-state message when `form.accounts` is falsy, and the `<c-list>` of connected accounts when `form.accounts` is truthy. Both branches MUST remain in `{% block page.content %}`.
- **FR-005**: The rewritten `socialaccount/connections.html` MUST include the "Add a Third-Party Account" section in all cases, using `{% include "socialaccount/snippets/provider_list.html" with process="connect" %}` and `{% include "socialaccount/snippets/login_extra.html" %}`. These inclusions are preserved from the original template.
- **FR-006**: `socialaccount/authentication_error.html` MUST be rewritten to replace all allauth `{% element %}` tags with Cotton equivalents. It MUST continue to extend `socialaccount/base_entrance.html`, override `{% block title %}` with the localised "Third-Party Login Failure" string, and place its heading and explanatory paragraph inside `{% block content %}` using Cotton components (consistent with the entrance layout pattern).
- **FR-007**: All user-visible strings in every rewritten template MUST be wrapped in `{% trans %}` or `{% blocktrans %}` for internationalisation, consistent with existing DAC addon templates.
- **FR-008**: *(Covered by FR-002 and FR-006.)* All allauth `{% element %}`, `{% endelement %}`, and `{% slot %}` tags MUST be eliminated from the two rewritten templates (`connections.html`, `authentication_error.html`) and replaced with equivalent Cotton components. Compliance is verified by a post-implementation grep over the three modified files (SC-002).
- **FR-009**: Integration tests covering the acceptance scenarios for US1–US3 MUST be added to `tests/test_addons/test_allauth/test_social_connections_view.py`.

### Key Entities

- **SocialAccount**: An allauth model representing a user's connected social account. Key attributes relevant to rendering: `pk` (identifier used in the radio form field), `provider` (string), and the associated `get_provider_account()` object which provides `get_brand().name` for the badge label.
- **SocialAccountsForm**: The allauth form for disconnecting a social account. Contains a single `account` radio field whose choices are the user's connected accounts. The form is submitted with a hidden `action` value to identify the disconnect action.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: `socialaccount/connections.html` renders with the DAC Account Center sidebar, "Account Center" root breadcrumb, and "Account Connections" leaf breadcrumb present, verified by automated Cotton rendering tests that assert these structural elements.
- **SC-002**: All allauth `{% element %}` and `{% endelement %}` / `{% slot %}` tags are eliminated from `connections.html` and `authentication_error.html` and replaced with Cotton components, verified by a grep over the override template files.
- **SC-003**: The automated test suite passes with zero failures for the new `test_social_connections_view.py` module, covering at minimum the acceptance scenarios for each user story (US1–US3).
- **SC-004**: A developer can verify the correct rendering of every conditional branch (connected accounts present, no accounts connected, authentication error page) without starting a server — purely from the Cotton rendering tests.

## Assumptions

- `dac/base.html` (from spec 005) and `account/base_manage.html` (corrected in spec 006) are fully implemented and provide the `page.content`, `title`, `page.breadcrumbs`, and `breadcrumbs` blocks; `socialaccount/base_manage.html` only needs its `extends` line changed to `dac/base.html`.
- `socialaccount/base_entrance.html` already correctly extends `allauth/layouts/entrance.html`; no change to this file is required.
- The allauth context variables (`form`, `form.accounts`, `form.fields.account.choices`) are provided by the `SocialAccountDisconnectView`; the templates do not need to fetch or transform this data.
- The Cotton components used by `connections.html` (`<c-badge>`, `<c-card>`, `<c-form>`, `<c-button>`, `<c-group>`) and `authentication_error.html` (`<c-text>`) are available through `django-mvp`, `django-cotton-bs5`, or existing DAC custom components.
- The `socialaccount_connections` URL is registered by allauth when `allauth.socialaccount` is in `INSTALLED_APPS`; templates may use `{% url 'socialaccount_connections' %}` freely.
- `socialaccount/login.html`, `socialaccount/signup.html`, and `socialaccount/login_cancelled.html` already use Cotton components and are not in scope for this spec.
- `socialaccount/login_redirect.html` is a standalone HTML redirect page with no DAC layout dependency and is explicitly out of scope.
- Screenshots are required per Constitution Principle XIII (Multi-Viewport Screenshot Coverage); pytest-playwright screenshot tests covering 3 page states × 3 viewports = 9 PNGs are written as part of this feature and live in the root `screenshots/` directory.
- The `socialaccount/snippets/provider_list.html` and `socialaccount/snippets/login_extra.html` includes are preserved as-is; their internal markup is not in scope for this spec.
