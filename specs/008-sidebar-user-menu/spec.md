# Feature Specification: Sidebar User Menu Component

**Feature Branch**: `008-sidebar-user-menu`
**Created**: 2026-05-18
**Status**: Refined
**Refined**: 2026-05-18 — Component redesigned as zero-config drop-in: all props removed; user data read directly from `request.user`; avatar URL resolution delegated entirely to `<c-avatar>`; `show_account_center` and `show_logout` suppression props removed (items always rendered when URLs are available).
**Refined**: 2026-05-18 — Testing strategy clarified: all component tests compose Cotton template strings inline in the test body; no external template files are required. Screenshot/E2E tests are explicitly out of scope for this component.
**Input**: User description: "I would like to create a 'user menu' component that sits in the footer of the app sidebar. This component should show the users avatar on the left, the display name to the top, and optional text underneath (e.g. email, position, role, company, etc). The component should act as a dropup element that opens to reveal a list of menu items for the user to select. By default, we will have 2 menu items: 1) a logout button and 2) a link to the accounts-center dashboard page where users can manage their accounts."

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Developer Drops the User Menu into the Sidebar Footer (Priority: P1) **[Developer]**

A developer building a Django application with DAC includes the `<c-dac.user-menu>` component in their sidebar footer slot. The component requires zero configuration: it reads the logged-in user's data directly from `request.user`, rendering their username (via `{{ request.user }}`), email address (via `{{ request.user.email }}`), and avatar (delegated entirely to `<c-avatar>`). Clicking the trigger reveals a dropup panel containing, by default, a link to the Account Center dashboard and a logout button.

**Why this priority**: This is the primary integration touch-point. The component is designed as a drop-in: a developer adds a single `<c-dac.user-menu />` tag and gets a fully functional, styled user menu with zero required configuration. If this contract is broken, the feature fails at its most basic level.

**Independent Test**: Can be tested by rendering a sidebar template that includes `<c-dac.user-menu />` with a mock authenticated request and asserting that the username, email, avatar element, Account Center link, and Logout button are all present in the output.

**Acceptance Scenarios**:

1. **Given** a sidebar template that includes `<c-dac.user-menu />`, **When** the page is rendered for a logged-in user, **Then** the component appears at the bottom of the sidebar and displays the user's avatar, username, and email address with no additional props required.
2. **Given** the component with no attributes, **When** rendered for a logged-in user, **Then** `{{ request.user }}` (username) appears in the trigger button with a `text-truncate` class applied.
3. **Given** the component with no attributes, **When** rendered for a logged-in user, **Then** `{{ request.user.email }}` appears as a muted secondary line below the username in the trigger button.
4. **Given** a logged-in user, **When** the component is rendered, **Then** `<c-avatar size="sm" />` is rendered inside the trigger; the avatar component resolves the user's photo URL via its own `avatar_url` template tag.
5. **Given** a developer who includes the component, **When** the page is rendered, **Then** the default Account Center link points to the `account-center` named URL, and the logout action targets the allauth logout URL.

---

### User Story 2 — End User Opens the Dropup and Navigates (Priority: P1) **[End User]**

A logged-in user sees the user menu trigger at the bottom of the sidebar. They click on it and a panel expands upward above the trigger, revealing their user information at the top followed by a list of actionable menu items. They can click the Account Center link to manage their account, or click Logout to sign out.

**Why this priority**: The dropup interaction is the core user-facing behaviour. If the panel does not open, or the default items are missing or broken, the component provides no functional value to the end user.

**Independent Test**: Can be tested by rendering the component with a representative authenticated user context and asserting that the dropup panel markup is present in the DOM, the Account Center and Logout items are rendered with correct link targets.

**Acceptance Scenarios**:

1. **Given** a user viewing the sidebar, **When** they click the user menu trigger at the bottom, **Then** a dropup panel opens above the trigger containing the Account Center link and Logout action.
2. **Given** the open dropup panel, **When** rendered, **Then** the panel contains an "Account Center" link that navigates to the account management dashboard.
3. **Given** the open dropup panel, **When** rendered, **Then** the panel contains a "Log out" button that triggers the logout action.
4. **Given** the open dropup panel, **When** the user clicks anywhere outside the panel, **Then** the panel closes without navigating away from the current page.
5. **Given** the open dropup panel, **When** the user selects "Log out", **Then** they are signed out and redirected appropriately.

---

### User Story 3 — Developer Adds Custom Menu Items to the Dropup (Priority: P2) **[Developer]**

A developer wants to add application-specific actions to the user menu — for example, a link to a settings page, a profile editor, or an upgrade prompt. They pass additional menu items as slot content inside the `<c-dac.user-menu>` component, and these items appear between the user info row and the default Logout button in the dropup panel.

**Why this priority**: Custom items are a power-developer feature. Without them, the component is only useful for projects that need no customisation. The design must ensure custom items do not displace the default items or break the layout.

**Independent Test**: Can be tested by rendering `<c-dac.user-menu>` with custom slot content (e.g., a "Settings" link) and asserting that the custom item appears in the dropup panel between the user info row and the Logout button.

**Acceptance Scenarios**:

1. **Given** a developer who adds a custom link inside the component's default slot, **When** the page is rendered, **Then** that link appears in the dropup panel between the user info row and the Logout button.
2. **Given** multiple custom items passed in the default slot, **When** rendered, **Then** all custom items appear in the order they were defined, between the user info row and Logout.
3. **Given** no custom slot content, **When** rendered, **Then** the dropup contains only the user info row, the Account Center link, and the Logout button — no empty spacers or invisible elements.

---

### ~~User Story 4 — Developer Overrides Default Menu Items (Priority: P3)~~ **[Removed]**

~~A developer wants to disable or replace one or both of the default menu items (Account Center link and Logout button). They can pass component attributes to suppress either default item and rely solely on their own custom slot content for the menu.~~

**Removed (2026-05-18)**: The `show_account_center` and `show_logout` suppression props were removed in the zero-config redesign. The component is intentionally opinionated: the Account Center link and Logout button are always rendered when their respective URLs are available. Graceful URL degradation (via `{% url '...' as var %}`) remains the only mechanism for item absence — if a URL is not registered in the host application, the corresponding item is silently omitted.

---

### User Story 5 — Developer Verifies the Component via Automated Tests (Priority: P3) **[Developer]**

A developer running the project test suite expects the user menu component to be covered by unit tests that validate rendering, default item presence, avatar presence, and customisation via slot content. All tests render Cotton template strings composed directly in the test body using the `cotton_render_string_soup` / `cotton_render_string_soup_authenticated` fixtures — no external template files are written for testing purposes.

**Why this priority**: Without automated tests, regressions in Cotton component rendering, URL resolution, or slot handling go undetected until a browser session. Tests also document the expected component behaviour for future maintainers.

**Independent Test**: Running `pytest tests/test_components/test_dac_base.py::TestDacUserMenu` with zero failures. No external template files, no Playwright, no live server.

**Testing approach**: Each test passes a template string such as `"<c-dac.user-menu />"` directly to `cotton_render_string_soup_authenticated(...)`. For the custom-slot test, the template string includes slot content inline (e.g., `"<c-dac.user-menu><c-dropdown.item text='Settings' href='#' /></c-dac.user-menu>"`). No test-specific `.html` files are created.

**Acceptance Scenarios**:

1. **Given** a test composing the string `"<c-dac.user-menu />"`  and rendering it with a mock authenticated user whose `__str__` returns `"testuser"`, **When** the test asserts that `"testuser"` appears in the trigger button, **Then** the assertion passes — without any external template file.
2. **Given** the same inline string and a mock user whose `.email` is `"test@example.com"`, **When** the test asserts that the email appears as a muted span in the trigger button, **Then** the assertion passes.
3. **Given** the same inline string, **When** the test asserts that the `<c-avatar>` wrapper element (class `avatar`) is present inside the trigger, **Then** the assertion passes.
4. **Given** the same inline string with the `account-center` URL registered, **When** the test asserts that the Account Center link and Logout form are present, **Then** both assertions pass.
5. **Given** the same inline string with the URL conf switched to a minimal conf (no `account-center` or `account_logout` URLs), **When** the test asserts that neither the Account Center link nor the Logout form appear, **Then** both assertions pass.

---

### Edge Cases

- What happens when the user's display name is not set or is very long? `{{ request.user }}` uses Django's `User.__str__`, which returns `username`. Long names are truncated visually via `text-truncate` CSS applied to the name span.
- What happens when the user is not authenticated? The component is only intended for use with authenticated users; if rendered for an anonymous user, `{% if request.user.is_authenticated %}` prevents any output — no exception is raised.
- What happens when the `account-center` URL is not registered in the host application? The component uses `{% url 'account-center' as var %}` — the item is silently omitted.
- What happens when the `account_logout` URL is not registered? Same pattern — `{% url 'account_logout' as var %}` — the Logout form is silently omitted.
- What happens when the avatar image URL is broken or inaccessible? `<c-avatar>` is responsible for its own fallback rendering; `<c-dac.user-menu>` passes no `src` — avatar URL resolution and fallback are entirely within the avatar component.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The component MUST render a trigger element positioned at the bottom of the sidebar that displays the user's circular avatar, username (`{{ request.user }}`), and email address (`{{ request.user.email }}`).
- **FR-002**: The avatar MUST be rendered using `<c-avatar size="sm" />` with no `src` attribute. The avatar component resolves the user's photo URL internally via its own `avatar_url` template tag; fallback rendering (e.g., SVG icon) is entirely the avatar component's responsibility.
- **FR-003**: The trigger element MUST open a dropup panel when activated, expanding upward above the trigger without navigating away from the current page.
- **FR-004**: The dropup panel MUST include, by default, a link to the Account Center dashboard (`account-center` named URL).
- **FR-005**: The dropup panel MUST include, by default, a Logout action that signs the user out via the allauth logout mechanism (POST form, CSRF-protected).
- **FR-006**: Developers MUST be able to inject custom menu items into the dropup panel via the component's default slot; custom items appear between the Account Center link and the Logout button.
- **FR-007**: The component MUST NOT raise an exception when rendered for an anonymous user; `{% if request.user.is_authenticated %}` wraps all output.
- **FR-008**: When the `account-center` URL cannot be reversed, the Account Center menu item MUST be silently omitted (using `{% url ... as var %}` assignment form).
- **FR-009**: When the `account_logout` URL cannot be reversed, the Logout form MUST be silently omitted.
- **FR-010**: The username MUST be visually truncated (via `text-truncate`) rather than wrapping and breaking the sidebar layout.
- **FR-011**: The component accepts NO configuration props. All user data is sourced directly from `request.user`. The only developer-controlled input is the default slot for custom menu items.

### Key Entities

- **UserMenuTrigger**: The always-visible footer element in the sidebar. Contains the circular avatar (`<c-avatar size="sm" />`), username (`{{ request.user }}`), and email (`{{ request.user.email }}`). Activates the dropup on interaction.
- **UserMenuDropup**: The panel that opens upward above the trigger. Contains the configurable menu items, the Account Center link, and the Logout button.
- **UserMenuItem**: An individual action in the dropup panel. Has a label and either a URL (link) or a form action (logout). Can carry an icon.
- **AvatarElement**: `<c-avatar size="sm" />` rendered with no `src`. The avatar component resolves the user's photo URL via its own `avatar_url` template tag and falls back to an SVG icon when no photo is found.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A developer can integrate the user menu into a sidebar footer by adding a single component tag and zero additional configuration, within 5 minutes of reading the component documentation.
- **SC-002**: The component renders correctly for both authenticated users with and without a profile picture, with no layout breakage in either case.
- **SC-003**: All five user stories have corresponding automated unit tests; every test renders the component via an inline template string (no external template files); the full test suite passes with zero failures. Screenshot / E2E tests are explicitly **not required** for this component.
- **SC-004**: The component gracefully handles all defined edge cases (anonymous user, missing URL, very long name) without raising unhandled exceptions. Avatar fallback for broken images is delegated to `<c-avatar>`.
- **SC-005**: The dropup panel is accessible: the trigger is keyboard-focusable, the panel can be dismissed without a mouse, and all interactive items are reachable via keyboard navigation.
- **SC-006**: Custom menu items injected via the default slot appear in the correct position within the dropup on first render, with no additional developer configuration required.

## Assumptions

- The host application uses Bootstrap 5 (via `django-mvp`) for styling and interactivity; the dropup behaviour is implemented using Bootstrap's existing Dropdown component.
- The component is part of the `dac` Cotton component library (`dac/templates/cotton/dac/`) and follows the existing naming conventions established by `dac.manage` and `dac.form_field`.
- The logged-in user object is available in the template context as `request.user`, consistent with Django's `AuthenticationMiddleware`.
- `{{ request.user }}` renders the user's username (Django's `User.__str__` returns `username`).
- `{{ request.user.email }}` provides the email address displayed as a secondary line in the trigger.
- The `<c-avatar>` component from django-mvp handles all avatar URL resolution and rendering via its own `avatar_url` template tag. `<c-dac.user-menu>` passes no `src` to `<c-avatar>` — all avatar decisions are delegated to the avatar component.
- The `account-center` named URL is provided by the `dac` package's URL configuration; the component attempts to reverse this URL and silently omits the item if the URL is not registered.
- Allauth is installed and its logout URL is available; the Logout button submits a POST request to the allauth logout endpoint following allauth's standard CSRF-protected logout pattern.
- Mobile sidebar behaviour (collapsed/off-canvas) is out of scope for this spec; the component is designed for the expanded desktop sidebar.
- The component accepts **no configuration props**. Developers who want user data from a different source (e.g., a non-`request.user` user object) must override the component template in their project.
- **Testing strategy**: All automated tests for this component compose Cotton template strings directly in the test body (e.g., `"<c-dac.user-menu />"`) and pass them to the `cotton_render_string_soup` / `cotton_render_string_soup_authenticated` fixtures. No external `.html` template files are created for test purposes.
- **No screenshots**: This component does not require Playwright screenshot tests or any form of visual regression testing. The `screenshots/` test module is out of scope for this feature.
