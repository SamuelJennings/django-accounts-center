# Feature Specification: Allauth Login Page

**Feature Branch**: `002-allauth-login-page`
**Created**: 2026-05-08
**Status**: Refined
**Refined**: 2026-05-09 — Added three `socialaccount` templates to scope: `socialaccount/login.html`, `socialaccount/login_cancelled.html`, and `socialaccount/login_redirect.html`. Each must be rewritten using Cotton components consistent with the rest of the entrance page suite.
**Refined**: 2026-05-08 — Four clarifications applied: (1) social buttons above email/password form (mirroring signup page); (2) passkey login in scope — FR-008 expanded, FR-015 added, User Story 6 added; (3) both login-by-code templates (`request_login_code.html` and `confirm_login_code.html`) require `<c-entrance>` shell — FR-013 updated, screenshot permutations split; (4) signup cross-link placed at bottom of card after all content. FR-012 restructured to group permutations by overridden template, making per-template screenshot coverage explicit.
**Input**: User description: "The login page is a critical page for any django project that allows users to create and manage accounts. The most used 3rd party authentication app is by far django-allauth. This spec is responsible for modernising the login template provided by django-allauth. The login form must be reactive to django-allauth settings provided by the developer (e.g. only shows social accounts when this app is available, shows a message when signup is not available, etc.). Django-allauth provides its own \"component-like\" syntax in its default templates, however, we will NOT be using this, instead opting to use the component system defined by django-cotton and the prebuilt component in the django-mvp package. See spec 001-allauth-signup-page for a similar spec that targetted the signup page."

## Clarifications

### Session 2026-05-08

- Q: When both social provider buttons AND the email/password form are present on the login page, what is the intended visual layout order? → A: Social buttons at the top, horizontal divider ("or"), email/password form below — mirroring the signup page layout (FR-002 confirmed as-is).
- Q: Should the DAC login page template handle the passkey login option (`PASSKEY_LOGIN_ENABLED`)? → A: Yes, in scope — show "Sign in with a passkey" button when `PASSKEY_LOGIN_ENABLED` is `True`; grouped with the login-by-code button below the email/password form.
- Q: The login-by-code flow uses two separate allauth templates — `account/request_login_code.html` (email input) and `account/confirm_login_code.html` (code entry). Should both be overridden with a Cotton/`<c-entrance>` template? → A: Both templates must use the `<c-entrance>` shell — both are user-facing entrance pages and both require consistent styling.
- Q: Where should the "Don't have an account? Sign up" link be rendered on the login page? → A: At the bottom of the card, matching the placement used on the signup page (after all form content, passwordless alternatives, and social buttons).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Developer Enables the Allauth Addon (Priority: P1) **[Developer]**

A developer has an existing Django project using django-allauth and wants a polished, ready-made login page without writing custom templates. They install `django-accounts-center`, add both `"dac"` and `"dac.addons.allauth"` to their `INSTALLED_APPS`, and the login page is immediately available — adapting automatically to whatever allauth settings they have configured (email-only, username+email, social providers, login-by-code, etc.) without any further template work.

**Why this priority**: This is the foundational integration experience for the login page. If enabling the addon requires more than adding two app entries, the package provides little value over hand-rolled templates. The login page is typically the highest-traffic page in any authenticated application.

**Independent Test**: Can be fully tested by creating a fresh Django project with django-allauth installed, adding `"dac"` and `"dac.addons.allauth"` to `INSTALLED_APPS`, and visiting `/account-center/login/` — the page should render with fields matching the active allauth settings, with no additional configuration.

**Acceptance Scenarios**:

1. **Given** a Django project with only `"dac"` in `INSTALLED_APPS` (allauth addon not enabled), **When** the developer visits `/account-center/login/`, **Then** allauth's own default templates are used — `dac.addons.allauth` has no effect until enabled.
2. **Given** a developer adds both `"dac"` and `"dac.addons.allauth"` to `INSTALLED_APPS` with allauth configured for email-only login (`ACCOUNT_AUTHENTICATION_METHOD = "email"`), **When** the login page is visited, **Then** the form renders a single email field and a password field with no username field.
3. **Given** `"dac.addons.allauth"` is enabled and allauth is configured with `ACCOUNT_AUTHENTICATION_METHOD = "username"`, **When** the login page is visited, **Then** the login field label reads "Username" (not "Email").
4. **Given** `"dac.addons.allauth"` is enabled and `allauth.socialaccount` is in `INSTALLED_APPS` but no social providers are configured, **When** the login page renders, **Then** no social login buttons appear.
5. **Given** `"dac.addons.allauth"` is enabled and at least one social provider is configured (e.g. Google), **When** the login page renders, **Then** social login buttons appear clearly separated from the email/password form.

---

### User Story 2 - End User Logs In via Email or Username and Password (Priority: P1) **[End User]**

A returning visitor arrives at the login page to access their account. They enter their credentials, submit the form, and are either taken directly to their destination or prompted for additional verification — all within a modern, visually polished UI.

**Why this priority**: This is the primary end-user flow. Login is the highest-traffic authenticated action in most applications; any friction or visual defect directly impacts retention and user confidence.

**Independent Test**: Can be fully tested by visiting the login page as an anonymous user, submitting valid credentials, and confirming redirection to the correct next step.

**Acceptance Scenarios**:

1. **Given** an anonymous user on the login page, **When** they submit a valid email and password with `ACCOUNT_EMAIL_VERIFICATION = "none"`, **Then** they are authenticated and redirected to `LOGIN_REDIRECT_URL`.
2. **Given** an anonymous user who submits an invalid password, **When** the page re-renders, **Then** a clear error message is shown — not revealing whether the email/username exists — without losing the submitted identifier value.
3. **Given** an anonymous user who submits a valid email for an account that has not yet verified their email address, **When** the page re-renders (or they are redirected), **Then** a clear message is shown directing them to verify their email.
4. **Given** `ACCOUNT_SESSION_REMEMBER` is `None` (allauth default), **When** the login form renders, **Then** a "Remember me" checkbox is visible.
5. **Given** `ACCOUNT_SESSION_REMEMBER` is `True` or `False`, **When** the login form renders, **Then** no "Remember me" checkbox is shown (session duration is fixed by configuration).
6. **Given** an anonymous user on the login page, **When** they click "Forgot password?", **Then** they are directed to the allauth password reset page.
7. **Given** signup is open (`is_open_for_signup()` returns `True`), **When** the login page renders, **Then** a "Don't have an account? Sign up" link is visible at the bottom of the card — after all form content, passwordless alternatives, and social buttons.
8. **Given** signup is closed (`is_open_for_signup()` returns `False`), **When** the login page renders, **Then** no signup link is shown.

---

### User Story 3 - End User Logs In via Social Account (Priority: P2) **[End User]**

A returning visitor prefers to authenticate using an existing social account (e.g. Google, GitHub). They click the provider button on the login page, are redirected to the provider's OAuth flow, and return to the application as an authenticated user.

**Why this priority**: Social login is a significant conversion factor for returning users and is a first-class allauth feature. The login page must fully support it to avoid users being stranded or confused.

**Independent Test**: Can be fully tested by configuring a social provider in allauth settings, visiting the login page, clicking the social button, completing the OAuth flow, and confirming successful authentication.

**Acceptance Scenarios**:

1. **Given** a login page with Google configured as a social provider, **When** the user clicks "Continue with Google", **Then** they are redirected to Google's OAuth consent screen.
2. **Given** multiple social providers configured, **When** the login page renders, **Then** each provider has its own distinctly labelled button, stacked vertically above a horizontal divider with the email/password form below.
3. **Given** `SOCIALACCOUNT_ONLY = True` is set (email/password login disabled), **When** the login page renders, **Then** only social provider buttons are shown — no email/password form, no login-by-code option.

---

### User Story 4 - End User Logs In via Email Code (Passwordless) (Priority: P2) **[End User]**

A returning visitor prefers not to enter a password. When `ACCOUNT_LOGIN_BY_CODE_ENABLED = True`, they see a "Sign in with a code" option on the login page. They click it, receive an email with a short-lived code, enter the code on a dedicated confirmation page, and are authenticated without a password.

**Why this priority**: Passwordless login by email code is a modern, security-friendly alternative to passwords. When the developer has enabled it, the login page must surface the option clearly, and the confirmation page must be styled consistently using Cotton components.

**Independent Test**: Can be fully tested by setting `ACCOUNT_LOGIN_BY_CODE_ENABLED = True`, visiting `/account-center/login/`, and confirming the login-by-code option is visible; then requesting a code, visiting the confirmation page, and confirming it renders using the `<c-entrance>` shell.

**Acceptance Scenarios**:

1. **Given** `ACCOUNT_LOGIN_BY_CODE_ENABLED = True`, **When** the login page renders, **Then** a "Sign in with a code" option is clearly visible alongside the password form.
2. **Given** `ACCOUNT_LOGIN_BY_CODE_ENABLED = False` (default), **When** the login page renders, **Then** no login-by-code option is shown.
3. **Given** a user who requests a login code, **When** they are directed to the code confirmation page, **Then** the page renders within the `<c-entrance>` shell using Cotton components, consistent with the main login UI.
4. **Given** the login-by-code confirmation page, **When** the user submits an expired or invalid code, **Then** a clear error message is shown inline without losing the email field value.

---

### User Story 6 - End User Logs In via Passkey (Priority: P2) **[End User]**

A returning visitor who previously enrolled a passkey sees a "Sign in with a passkey" option on the login page when `PASSKEY_LOGIN_ENABLED` is `True` (i.e. `allauth.mfa` is installed and WebAuthn passkey authentication is configured). They click the button, their device/browser handles the WebAuthn ceremony, and they are authenticated without a password or a separate code.

**Why this priority**: Passkey login is the most seamless form of passwordless authentication when the infrastructure is present. When the developer has enabled it, the login page must surface the option clearly alongside login-by-code. The WebAuthn script must also be injected correctly — a missing script silently breaks the flow.

**Independent Test**: Can be fully tested by setting `PASSKEY_LOGIN_ENABLED = True` (via `allauth.mfa` with WebAuthn enabled), visiting `/account-center/login/`, and confirming the passkey sign-in button is visible; then completing a WebAuthn assertion and confirming successful authentication.

**Acceptance Scenarios**:

1. **Given** `PASSKEY_LOGIN_ENABLED = True`, **When** the login page renders, **Then** a "Sign in with a passkey" button is visible, grouped below the email/password form (and alongside login-by-code if also enabled).
2. **Given** `PASSKEY_LOGIN_ENABLED = False` (default), **When** the login page renders, **Then** no passkey sign-in button is shown.
3. **Given** `PASSKEY_LOGIN_ENABLED = True`, **When** the login page renders, **Then** the WebAuthn login script (`mfa/webauthn/snippets/login_script.html`) is injected into the page's `extra_js` block with the passkey button ID, enabling the browser's WebAuthn API to be invoked on click.
4. **Given** `SOCIALACCOUNT_ONLY = True`, **When** the login page renders, **Then** no passkey sign-in button is shown (social-only mode disables all non-social login paths).

---

### User Story 7 - End User Is Redirected Through Social OAuth Confirmation Page (Priority: P2) **[End User]**

When a social OAuth flow involves an intermediate confirmation step (`socialaccount/login.html` — shown when allauth needs the user to explicitly confirm connecting or signing in via a provider), or when the OAuth flow redirects through `socialaccount/login_redirect.html`, the user sees a page consistent with the `<c-entrance>` shell. If the user cancels the OAuth flow, `socialaccount/login_cancelled.html` informs them clearly with a link back to the login page.

**Why this priority**: These three templates are part of the social login journey and are visible to end users when social authentication is in use. Leaving them with `{% element %}` syntax creates visual inconsistency between steps of the same flow.

**Independent Test**: Can be fully tested by configuring a social provider, initiating an OAuth flow that triggers the confirmation page, completing or cancelling the flow, and verifying each page renders with the `<c-entrance>` shell.

**Acceptance Scenarios**:

1. **Given** a social login flow that requires explicit confirmation (e.g. connecting an account), **When** the `socialaccount/login.html` page renders, **Then** the page uses the `<c-entrance>` shell and Cotton components instead of `{% element %}` syntax.
2. **Given** a social OAuth flow that uses a redirect-through page (`socialaccount/login_redirect.html`), **When** the page renders, **Then** a meta-refresh redirect fires immediately and the intermediate page is visually consistent with the entrance shell if displayed.
3. **Given** a user who cancels a social OAuth flow, **When** `socialaccount/login_cancelled.html` renders, **Then** the page uses the `<c-entrance>` shell, displays a clear "Login Cancelled" message, and includes a link back to the sign-in page.

---

### User Story 5 - Already Authenticated User Visits Login (Priority: P3) **[End User]**

A logged-in user navigates to the login page (e.g. from a bookmark or stale tab). Instead of seeing the login form again, they are redirected away or shown a message indicating they are already signed in.

**Why this priority**: This is a UX polish concern — allauth handles the redirect by default, but the page should not break or confuse an authenticated user.

**Independent Test**: Can be fully tested by logging in, then visiting `/account-center/login/` directly and confirming the redirect or appropriate message.

**Acceptance Scenarios**:

1. **Given** an authenticated user visiting the login page, **When** the page loads, **Then** they are redirected to the configured `LOGIN_REDIRECT_URL` or a "You are already signed in" message is displayed.

---

### Edge Cases

- What happens when allauth is installed but `INSTALLED_APPS` is missing `allauth.account`? The page must not crash — it should fail gracefully with a developer-visible configuration error.
- What happens if a social provider's OAuth credentials are misconfigured? The social button appears normally; errors from the OAuth flow are handled by allauth on the callback URL, not the login page.
- What happens when both `SOCIALACCOUNT_ONLY = True` and `ACCOUNT_LOGIN_BY_CODE_ENABLED = True`? Social-only mode takes precedence — no login-by-code option is shown since email/password login is fully disabled.
- What happens when a user's account is rate-limited by allauth? Allauth's built-in rate limiting returns an error response; the login page template is not involved in enforcing rate limits.
- What if the login page is visited with a `next` query parameter? The redirect after successful login must honour the `next` parameter, delegating entirely to allauth's standard redirect logic.
- What if `ACCOUNT_AUTHENTICATION_METHOD = "username_email"`? The login field must accept either a username or an email address; the field label and placeholder should reflect this dual-mode input.
- What happens when both `PASSKEY_LOGIN_ENABLED = True` and `LOGIN_BY_CODE_ENABLED = True`? Both buttons must be shown, stacked vertically below the email/password form. The passkey button appears first (faster/higher-trust path), the code button second.
- What happens when `PASSKEY_LOGIN_ENABLED = True` but `allauth.mfa` is not properly installed? The context variable `PASSKEY_LOGIN_ENABLED` will be `False`; the button simply will not render — no error on the login page itself.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The login form's identifier field MUST adapt its label and placeholder to the active `ACCOUNT_AUTHENTICATION_METHOD` setting: `"email"` → "Email address", `"username"` → "Username", `"username_email"` → "Username or Email".
- **FR-002**: The login page MUST display social account provider buttons when `allauth.socialaccount` is in `INSTALLED_APPS` and at least one provider is configured. Social buttons MUST appear at the top of the page, followed by a horizontal divider labelled "or", with the email/password form rendered below.
- **FR-003**: Social provider buttons MUST NOT appear when `allauth.socialaccount` is absent from `INSTALLED_APPS` or when no social providers have been configured.
- **FR-004**: The login form MUST display a "Remember me" checkbox only when `ACCOUNT_SESSION_REMEMBER` is `None` (allauth's default). When the setting is `True` or `False`, no checkbox is shown and session duration is determined entirely by configuration.
- **FR-005**: A "Forgot password?" link MUST always be displayed below the password field whenever the password field is visible. The link navigates to the allauth password reset page.
- **FR-006**: A "Don't have an account? Sign up" link MUST be shown at the very bottom of the entrance card — after all form fields, the submit button, the "Forgot password?" link, any passwordless alternatives, and any social buttons — when `is_open_for_signup()` returns `True`. It MUST be hidden when signup is closed. This mirrors the cross-link placement on the signup page.
- **FR-007**: The login form MUST display per-field validation errors inline, immediately below the offending field, without losing values in other fields. Non-field (form-level) errors MUST be displayed as a danger alert above the fields; this is handled automatically by `<c-form.render>` — page templates MUST NOT duplicate this logic with their own `{% if form.non_field_errors %}` block.
- **FR-008**: The login page MUST display passwordless sign-in alternatives below the email/password form when either `PASSKEY_LOGIN_ENABLED` or `LOGIN_BY_CODE_ENABLED` is `True`. If any alternative is present, they MUST be grouped in a `<c-button.stack>` beneath a horizontal "or" divider. Within the stack, the passkey button ("Sign in with a passkey") MUST appear before the code button ("Send me a sign-in code") when both are enabled. Both the passkey button and the code button MUST be hidden when `SOCIALACCOUNT_ONLY = True`.
- **FR-009**: The login page shell MUST be delivered via the shared `<c-entrance>` Cotton component (located at `dac/templates/cotton/entrance/index.html`), the same component used by the signup page. The allauth layout template (`allauth/layouts/entrance.html`) is shared with the signup page and already delegates to `<c-entrance>`; the login page template (`account/login.html`) MUST focus solely on its content block and MUST NOT contain card, container, or logo markup.
- **FR-010**: The entrance layout's two override points — `<c-entrance.background>` and `<c-entrance.logo>` — are inherited from the signup page implementation (FR-009 in spec 001). The login page MUST NOT redefine or duplicate these components; it benefits from them automatically via the shared `<c-entrance>` shell.
- **FR-011**: The page MUST present a modern, visually consistent design that integrates with the rest of the `django-accounts-center` UI system (shared base layout, consistent typography, spacing, and colour usage). Visual quality MUST be validated by automated pytest-playwright screenshot tests (see FR-012); developer code-review judgment is supplementary, not a substitute.
- **FR-012**: Per constitution Principle XIII, every allauth template overridden by this spec MUST be covered by at least one screenshot permutation. Automated pytest-playwright tests MUST capture screenshots at three canonical viewports — desktop (1440×900), tablet (768×1024), and mobile (390×844) — and persist them under `docs/_static/{desktop,tablet,mobile}/`. Permutations are grouped below by the template they capture; all seven MUST each have a full set of three viewport screenshots:

  **`account/login.html`** (five permutations covering all visually distinct states of the main login page):
  - `login-page-social-disabled` — `SOCIALACCOUNT_ENABLED=False` (email/password form only, no social buttons)
  - `login-page-social-enabled` — `SOCIALACCOUNT_ENABLED=True` with at least one provider configured (social buttons above divider + email/password form)
  - `login-page-social-only` — `SOCIALACCOUNT_ONLY=True` (social buttons only, no email/password form)
  - `login-page-login-by-code` — `ACCOUNT_LOGIN_BY_CODE_ENABLED=True` (login page with "Send me a sign-in code" button visible below the form)
  - `login-page-passkey-enabled` — `PASSKEY_LOGIN_ENABLED=True` (login page with "Sign in with a passkey" button visible below the form)

  **`account/request_login_code.html`** (one permutation — the email-input step of the passwordless code flow):
  - `login-request-code-page` — `ACCOUNT_LOGIN_BY_CODE_ENABLED=True` (user enters email to request a code)

  **`account/confirm_login_code.html`** (one permutation — the code-entry step of the passwordless code flow):
  - `login-confirm-code-page` — `ACCOUNT_LOGIN_BY_CODE_ENABLED=True` (user enters the emailed code to complete authentication)

  Screenshot files MUST follow the naming pattern `<page-name>-<config-slug>.png`. Tests MUST use `@pytest.mark.parametrize` or a shared viewport fixture to avoid logic duplication across viewport sizes. The `docs/_static/desktop/`, `docs/_static/tablet/`, and `docs/_static/mobile/` directories MUST be created by test setup if they do not exist. Implementing agents MUST visually inspect the generated screenshot files before marking any UI task complete. Per constitution Principle XIII v1.1.2, screenshot tests MUST live in the root `screenshots/` directory (e.g. `screenshots/test_login_screenshots.py`), NOT inside `tests/`; they are excluded from plain `pytest` runs (which use `testpaths = ["tests"]`) and regenerated explicitly with `pytest screenshots/`.
- **FR-013**: Both login-by-code page templates MUST use the `<c-entrance>` Cotton component as their page shell and MUST use Cotton form/button components for their content. Neither MUST contain raw Bootstrap layout markup (containers, rows, card HTML). Both must be consistent in structure and visual style with `account/login.html`:
  - `account/request_login_code.html` — the page where the user enters their email address to request a sign-in code.
  - `account/confirm_login_code.html` — the page where the user enters the code received by email. The DAC override MUST extend `account/base_entrance.html` **directly**, bypassing allauth's `account/base_confirm_code.html`. `base_confirm_code.html` is shared with other confirmation flows (email verification, phone verification) and still uses `{% element %}` syntax; modifying it is out of scope for this spec. The override must preserve the code-input form, resend capability, and inline error handling using Cotton components.
- **FR-014**: The login page MUST redirect or gracefully handle the case where the requesting user is already authenticated, delegating entirely to allauth's standard redirect logic.
- **FR-015**: When `PASSKEY_LOGIN_ENABLED` is `True`, the login page template MUST inject the allauth WebAuthn login script (`mfa/webauthn/snippets/login_script.html`) into the `extra_js` block with the passkey button's element ID. This MUST be done conditionally — the script MUST NOT be injected when `PASSKEY_LOGIN_ENABLED` is `False`, to avoid loading unnecessary JavaScript.
- **FR-016**: Three `socialaccount` entrance templates MUST be rewritten using Cotton components, replacing all `{% element %}` syntax:
  - `socialaccount/login.html` — the intermediate confirmation page shown when allauth requires the user to explicitly confirm signing in or connecting via a social provider. Extends `socialaccount/base_entrance.html`. Renders a confirmation form with a "Continue" submit button. Conditionally shows either a "Connect" or "Sign In Via" heading depending on the `process` context variable (`"connect"` vs `"login"`).
  - `socialaccount/login_cancelled.html` — the page shown when a user cancels an OAuth flow. Extends `socialaccount/base_entrance.html`. Shows a "Login Cancelled" message and a link back to the sign-in page.
  - `socialaccount/login_redirect.html` — the intermediate redirect page during an OAuth flow. Does NOT extend `socialaccount/base_entrance.html`; it is a standalone page with a meta-refresh redirect (`http-equiv="refresh"`). The page MUST preserve the meta-refresh redirect and use a minimal but visually consistent layout. No `<c-entrance>` shell is used here — the page is ephemeral and shown only for an instant before the redirect fires.
  All three templates already exist as placeholder overrides in `dac/addons/allauth/templates/socialaccount/` and currently use `{% element %}` syntax; they MUST be fully rewritten by this spec.

### Key Entities *(include if feature involves data)*

- **Login Form**: The form presented to the user at the login page. Its identifier field (username, email, or username-or-email) is determined by `ACCOUNT_AUTHENTICATION_METHOD`. May additionally show a "remember me" checkbox depending on `ACCOUNT_SESSION_REMEMBER`.
- **Social Provider**: An OAuth2/OpenID Connect identity provider (e.g. Google, GitHub, Facebook) configured in `SOCIALACCOUNT_PROVIDERS`. Determines which, if any, social login buttons are displayed.
- **Allauth Configuration**: The collection of Django settings and installed apps that control allauth behaviour — authentication method, session persistence, login-by-code, social account support, and signup availability.
- **Cotton Component**: A reusable, file-based UI component from the django-cotton system (provided by django-mvp) that encapsulates markup and logic for a specific UI element (e.g. a form field, a provider button, a card).
- **`<c-entrance>` Component** (`dac/templates/cotton/entrance/index.html`): The shared entrance page shell component, defined in spec 001. Accepts a `title` slot (rendered as an `<h4>` inside the card header) and responsive-width attrs. The login page template uses this component identically to the signup page template.
- **`<c-entrance.background>` Component** (`dac/templates/cotton/entrance/background.html`): Shared background component defined in spec 001. Controls the full-page background style. The login page inherits this without modification.
- **`<c-entrance.logo>` Component** (`dac/templates/cotton/entrance/logo.html`): Shared logo component defined in spec 001. Renders the site logo inside the card header. The login page inherits this without modification.
- **Login-by-Code Request Page** (`account/request_login_code.html`): The entrance page where the user enters their email address to request a sign-in code. Uses `<c-entrance>` shell and Cotton form components.
- **Login-by-Code Confirmation Page** (`account/confirm_login_code.html`): The page where the user enters the emailed code to complete authentication. Uses `<c-entrance>` shell and Cotton form components. Both pages form a two-step entrance flow distinct from the main login page.
- **`PASSKEY_LOGIN_ENABLED` Context Variable**: An allauth template context boolean that is `True` when `allauth.mfa` is installed and WebAuthn passkey authentication is enabled. Controls visibility of the "Sign in with a passkey" button and injection of the WebAuthn script.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A developer with a working allauth installation can have a fully functional, styled login page in production with no more than 5 lines of new configuration (URL wiring + settings), assuming the `dac.addons.allauth` addon is already installed for the signup page.
- **SC-002**: The login page correctly adapts its identifier field label and form structure for all documented `ACCOUNT_AUTHENTICATION_METHOD` values (`"email"`, `"username"`, `"username_email"`) — verified by automated tests covering each value.
- **SC-003**: A returning user can complete the full login flow (visit page → enter credentials → submit → land on destination) in under 30 seconds on a standard broadband connection.
- **SC-004**: The login page renders without errors or visible layout defects across all allauth configuration permutations, including zero social providers, one provider, multiple providers, and login-by-code enabled — confirmed by both automated integration tests and committed viewport screenshots.
- **SC-005**: A full set of pytest-playwright viewport screenshots (desktop 1440×900, tablet 768×1024, mobile 390×844) exists under `docs/_static/` for each of the visually distinct settings permutations defined in FR-012 (original seven) plus the new permutations for FR-016 (`socialaccount/login.html` and `socialaccount/login_cancelled.html`). All viewport screenshot files are committed to the repository alongside the implementation and remain non-stale on every subsequent UI-touching pull request. (`socialaccount/login_redirect.html` is exempt from screenshot coverage as it is an ephemeral redirect-only page.)
- **SC-006**: All Cotton component boundaries in the login page are documented, enabling developers to identify and override any sub-component within their own project templates.

## Assumptions

- The allauth login page is delivered via the `dac.addons.allauth` addon. Both `"dac"` and `"dac.addons.allauth"` must be present in `INSTALLED_APPS` for any allauth-specific template overrides or login page logic to take effect.
- This spec targets **django-allauth v65+** (new-style API). The legacy v0.x API is not supported. The minimum allauth version will be enforced as a package dependency.
- The `<c-entrance>` shell component, `<c-entrance.background>`, and `<c-entrance.logo>` are fully implemented by spec 001 (Allauth Signup Page). This spec depends on those components existing and requires no further changes to them.
- The `django-mvp` package is a dependency and its Cotton component library is available at render time.
- django-cotton is installed and configured as a template engine in the host project's `TEMPLATES` setting.
- The allauth layout template (`allauth/layouts/entrance.html`) is shared between the signup and login pages. No modifications to the layout template are required by this spec.
- This spec covers six page-level template overrides in total: `account/login.html`, `account/request_login_code.html`, `account/confirm_login_code.html`, `socialaccount/login.html`, `socialaccount/login_cancelled.html`, and `socialaccount/login_redirect.html`. The first three were already implemented by the initial tasks; the last three are newly in-scope via this refinement (2026-05-09).
- Multi-factor authentication (MFA) prompt after login is out of scope for this page; allauth redirects to the MFA challenge automatically post-login, and that page is a separate concern.
- The reauthentication page (`account/reauthenticate.html`) is out of scope for this spec iteration; it is a distinct template with a distinct user flow and will be addressed in a separate spec.
- Social account connection (linking a social account to an existing user after login) is out of scope for this spec, **except** for the `socialaccount/login.html` confirmation step which is already a placeholder override in `dac.addons.allauth` and must be rewritten as part of this spec (see FR-016).
- Other `socialaccount` entrance templates not listed in FR-016 (`authentication_error.html`, `signup.html`) are out of scope for this spec iteration.
- Rate limiting and brute-force protection for the login endpoint are delegated to allauth's built-in `ACCOUNT_RATE_LIMITS` mechanism and the host project's infrastructure. The login page component itself imposes no additional rate-limiting logic.
- Accessibility (WCAG 2.1 AA) is assumed as a baseline but a detailed accessibility audit is out of scope for this spec iteration.
- The developer is responsible for providing OAuth credentials for any social providers; the login page simply reflects what is configured.
- Passkey login (`PASSKEY_LOGIN_ENABLED`) requires `allauth.mfa` to be installed and WebAuthn/FIDO2 to be properly configured in the host project (including a registered passkey for the user). The login page template's only responsibility is to conditionally render the button and inject the WebAuthn script — it has no dependency on the WebAuthn backend implementation itself.
