# Feature Specification: User Sessions Management Templates

**Feature Branch**: `010-usersessions-templates`
**Created**: 2026-05-22
**Status**: Draft

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Developer Wires Sessions Management into the DAC Layout (Priority: P1) **[Developer]**

A developer enabling `allauth.usersessions` in their DAC-based project expects the "Sessions" page to inherit the full DAC management layout — Account Center sidebar, breadcrumb trail rooted at "Account Center", and consistent card-stack content area — without writing any structural HTML. They do this by installing `dac.addons.allauth` and defining the allauth user sessions URL patterns; the override templates handle the rest.

**Why this priority**: `usersessions/base_manage.html` currently extends `allauth/layouts/manage.html` instead of `dac/base.html`. This single deviation means the Sessions management page never renders inside the DAC UI shell. Fixing it is a one-line change that unblocks the end-user story and all downstream rendering. This is the same defect class as spec 006 (`account/`), spec 007 (`account/`), and spec 009 (`socialaccount/`).

**Independent Test**: Can be tested by rendering `usersessions/usersession_list.html` in isolation using Cotton rendering tests and asserting that the DAC sidebar, breadcrumbs, and card-stack are present in the output.

**Acceptance Scenarios**:

1. **Given** `usersessions/base_manage.html` in the DAC addon, **When** it is rendered as a base template, **Then** it extends `dac/base.html` (not `allauth/layouts/manage.html`), inheriting the full DAC management layout.
2. **Given** `usersessions/usersession_list.html` which extends through `usersessions/base_manage.html`, **When** rendered, **Then** the Account Center sidebar, breadcrumb trail, and card-stack content area are all present.
3. **Given** `usersessions/usersession_list.html`, **When** rendered, **Then** its content appears inside `{% block page.content %}` (not the generic `{% block content %}`), placing it within the card-stack.

---

### User Story 2 — End User Views and Signs Out Active Sessions (Priority: P2) **[End User]**

A logged-in user navigates to the "Sessions" page and sees a table of all their active sessions — each row showing when the session started, the originating IP address, the browser/user agent, and optionally when it was last seen. The current session is visually indicated with a "Current" badge. If the user has more than one active session, a "Sign Out Other Sessions" button is available. If they have only one session, a "Sign Out" button is shown instead. The page renders with the same sidebar, breadcrumb trail, and card-stack layout as all other DAC management pages.

**Why this priority**: This is the primary end-user value of the feature — a user-friendly session management interface inside the DAC UI shell. The existing template uses `{% element %}` tags throughout, producing raw allauth markup with no DAC layout context.

**Independent Test**: Can be tested by rendering `usersessions/usersession_list.html` with representative context objects (a list of sessions including one marked as current, and the `show_last_seen_at` flag in both states) and asserting that the session table rows, "Current" badge, and sign-out button are present with the correct structure.

**Acceptance Scenarios**:

1. **Given** a user with multiple active sessions, **When** `usersessions/usersession_list.html` is rendered, **Then** each session appears as a table row with its started-at time, IP address, and browser/user agent displayed.
2. **Given** a user with multiple active sessions, **When** the template is rendered, **Then** the current session's row contains a "Current" badge and the action button reads "Sign Out Other Sessions".
3. **Given** a user with only one active session (the current one), **When** the template is rendered, **Then** the action button reads "Sign Out".
4. **Given** the `show_last_seen_at` context variable is `True`, **When** the template is rendered, **Then** a "Last Seen" column is present in the table header and each session row shows the last-seen-at time.
5. **Given** `usersessions/usersession_list.html`, **When** rendered, **Then** no allauth `{% element %}`, `{% endelement %}`, or `{% slot %}` tags appear in the rendered HTML output.

---

### User Story 3 — Developer Verifies Templates via Automated Tests (Priority: P3) **[Developer]**

A developer running the test suite expects all user sessions management template overrides to be covered by automated integration tests. The tests prove that the correct layout and components are rendered for each branch of the sessions logic (multiple sessions, single session, last-seen-at enabled/disabled).

**Why this priority**: Without automated tests, regressions in block names or Cotton component usage go undetected until a browser. Tests also document the expected context variables (`sessions`, `session_count`, `show_last_seen_at`) for future maintainers.

**Independent Test**: Running `pytest tests/test_addons/test_allauth/test_usersessions_view.py --no-cov` passes with zero failures. Each test targets a specific acceptance scenario from US1 and US2.

**Acceptance Scenarios**:

1. **Given** a test that renders `usersessions/usersession_list.html` with a list of sessions, **When** the test asserts the DAC sidebar, breadcrumb, session table rows, "Current" badge, and "Sign Out Other Sessions" button are present, **Then** the assertions pass.
2. **Given** a test that renders `usersessions/usersession_list.html` with a single session, **When** the test asserts the "Sign Out" button text is present (not "Sign Out Other Sessions"), **Then** the assertion passes.
3. **Given** a test that renders `usersessions/usersession_list.html` with `show_last_seen_at=True`, **When** the test asserts the "Last Seen" column header is present, **Then** the assertion passes.

---

### Edge Cases

- What happens when a user has no active sessions? The view always includes at least the current session; an empty session list is not a practical runtime state. No empty-state branch is required.
- What happens when `show_last_seen_at` is `False` (the default)? The "Last Seen" column MUST be omitted from both the table header and every data row; no placeholder or empty cell should appear.
- What happens when `session.ip` is empty (e.g., a session created without IP tracking)? The IP cell renders an empty string; no special handling is required in the template.
- What happens when a user submits the sign-out form? Allauth's `ListUserSessionsView.form_valid()` handles the POST and adds a flash message via `sessions_logged_out.txt`; the template itself does not need to handle this case beyond rendering the form correctly.

## Clarifications

### Session 2026-05-22

- Q: Should the sign-out form support per-session selection (radio buttons per row) or bulk sign-out of all other sessions at once? → A: Bulk sign-out only — one button signs out all other sessions at once; no per-row controls.
- Q: How should the Browser (user agent) column display the `user_agent` string? → A: Truncated raw string — display `session.user_agent` as-is with a CSS truncation class (e.g. `text-truncate`) to cap column width; no parsing required.
- Q: What Bootstrap variant should the sign-out `<c-button>` use? → A: `primary` — standard blue call-to-action; no special severity signal.
- Q: Should the Sessions page render a visible heading in `{% block page.header %}`? → A: Yes — render `{% trans "Sessions" %}` in `{% block title %}`. Research (Decision 6) confirmed that `{% block page.header %}` wraps the breadcrumbs toolbar region, not a heading slot; the heading appears via `{% block title %}` inside `<c-mvp.toolbar>`, consistent with all other DAC management pages.
- Q: What Bootstrap variant should the `<c-badge>` use for the "Current" session indicator? → A: `success` — green; affirms the current session is active with high visual distinction.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: `usersessions/base_manage.html` MUST extend `dac/base.html` (not `allauth/layouts/manage.html`). This single change propagates the DAC layout to all templates that inherit through this base.
- **FR-002**: `usersessions/usersession_list.html` MUST be fully rewritten as a clean Cotton template. It MUST override `{% block title %}` with `{% trans "Sessions" %}` (the visible page heading — `{% block page.header %}` is NOT overridden; it wraps the breadcrumbs toolbar and is not the heading slot), append a "Sessions" item to `{% block page.breadcrumbs %}`, and place all content inside `{% block page.content %}` (not `{% block content %}`). A full rewrite is warranted because the existing template uses `{% block content %}` and allauth `{% element %}` tags throughout.
- **FR-003**: The rewritten `usersessions/usersession_list.html` MUST render the sessions list as an HTML table inside a `<c-card>` wrapper. The table MUST use Bootstrap table classes and include columns for: Started At (formatted with `|naturaltime`), IP Address, Browser (user agent displayed as a truncated raw string using a CSS truncation class such as `text-truncate` — no parsing required), and optionally Last Seen (only when `show_last_seen_at` is `True`). A fifth column MUST render either a `<c-badge variant="success">` with text "Current" for the current session's row or an empty cell for other sessions.
- **FR-004**: The sign-out form MUST use bulk sign-out only — no per-session selection (no radio buttons or checkboxes). The form MUST POST to `{% url 'usersessions_list' %}` when `session_count > 1`, or to `{% url 'account_logout' %}` when `session_count` is 1. The form MUST include a CSRF token and render its submit button via `<c-button variant="primary">`: with text "Sign Out Other Sessions" when `session_count > 1`, or "Sign Out" when `session_count` is 1.
- **FR-005**: All user-visible strings in the rewritten template MUST be wrapped in `{% trans %}` or `{% blocktrans %}` for internationalisation, consistent with existing DAC addon templates.
- **FR-006**: All allauth `{% element %}`, `{% endelement %}`, and `{% slot %}` tags MUST be eliminated from the rewritten `usersessions/usersession_list.html` and replaced with equivalent Cotton components or standard HTML. Compliance is verified by a post-implementation grep over the modified files.
- **FR-007**: Integration tests covering the acceptance scenarios for US1–US3 MUST be added to `tests/test_addons/test_allauth/test_usersessions_view.py`.

### Key Entities

- **UserSession**: An allauth model representing an active user session. Key attributes relevant to rendering: `created_at` (datetime), `ip` (string), `user_agent` (string), `last_seen_at` (datetime, optional), `is_current` (bool).
- **ManageUserSessionsForm**: The allauth form for signing out other sessions. Submitted as a POST with no body fields beyond CSRF; the view handles all session logic.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: `usersessions/usersession_list.html` renders with the DAC Account Center sidebar, "Sessions" heading text rendered via `{% block title %}`, "Account Center" root breadcrumb, and "Sessions" leaf breadcrumb present, verified by automated integration tests that assert these structural elements.
- **SC-002**: All allauth `{% element %}` and `{% endelement %}` / `{% slot %}` tags are eliminated from `usersessions/usersession_list.html`, verified by a grep over the modified template file.
- **SC-003**: The automated test suite passes with zero failures for the new `test_usersessions_view.py` module, covering at minimum the acceptance scenarios for each user story (US1–US3).
- **SC-004**: A developer can verify the correct rendering of every conditional branch (multiple sessions, single session, `show_last_seen_at` enabled/disabled) without starting a server — purely from the integration tests.

## Assumptions

- `dac/base.html` (from spec 005) and `account/base_manage.html` (corrected in spec 006) are fully implemented and provide the `page.content`, `title`, `page.breadcrumbs`, and `page.header` blocks.
- `usersessions/base_manage.html` only needs its `extends` line changed to `dac/base.html`; no other changes are required to this file.
- The allauth context variables (`sessions`, `session_count`, `show_last_seen_at`) are provided by `ListUserSessionsView`; the templates do not need to fetch or transform this data.
- No `<c-table>` Cotton component exists in the project; the table MUST be rendered using raw Bootstrap HTML (`<table class="table">`) inside a `<c-card>`.
- The Cotton components used by `usersession_list.html` (`<c-card>`, `<c-badge>`, `<c-button>`, `<c-breadcrumbs.item>`) are available through `django-mvp`, `django-cotton-bs5`, or existing DAC custom components.
- The `usersessions_list` URL is registered by allauth when `allauth.usersessions` is in `INSTALLED_APPS`; templates may use `{% url 'usersessions_list' %}` freely.
- Screenshots are required per Constitution Principle XIII (Multi-Viewport Screenshot Coverage); pytest-playwright screenshot tests covering 2 page states × 2 viewports = 4 PNGs are written as part of this feature and live in the root `screenshots/` directory (states: multiple-sessions, single-session; viewports: desktop 1440×900, mobile 390×844).
- `usersessions/messages/sessions_logged_out.txt` is a plain-text flash message template; it does not use `{% element %}` tags and is out of scope for this spec.
