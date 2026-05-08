# Feature Specification: Allauth Signup Page

**Feature Branch**: `001-allauth-signup-page`  
**Created**: 2026-05-07  
**Status**: Refined  
**Refined**: 2026-05-07 — Added Principle XIII multi-viewport screenshot requirements; FR-010 now mandates automated pytest-playwright screenshot tests (three viewports × four settings permutations). Clarification Q5 updated to reflect constitution v1.1.0 superseding the original "developer judgment only" position.  
**Refined**: 2026-05-08 — Entrance layout architecture finalised: the entrance page shell is now a first-class Cotton component (`<c-entrance>`) with two overridable sub-components (`<c-entrance.background>` for background styling, `<c-entrance.logo>` for the logo). The allauth layout template (`allauth/layouts/entrance.html`) delegates entirely to `<c-entrance>`, passing a `title` slot and responsive-width attrs. Individual page templates (e.g. `signup.html`) focus purely on their content block. Logo override is via template replacement, not a prop. FR-008 and FR-009 updated accordingly.  
**Refined**: 2026-05-08 — Passkey signup flow added: when both `MFA_PASSKEY_SIGNUP_ENABLED` and `ACCOUNT_EMAIL_VERIFICATION_BY_CODE_ENABLED` are `True`, allauth exposes a `/account-center/signup/passkey/` endpoint served by `signup_by_passkey.html`. User Story 6 added. FR-012 added (passkey signup template must use Cotton components). FR-011 and SC-007 updated with two additional screenshot permutations: `signup-page-passkey-enabled` (signup page with passkey option visible) and `signup-by-passkey-page` (the `/signup/passkey/` page itself).  
**Refined**: 2026-05-08 — Constitution v1.1.2 (Principle XIII PATCH): FR-011 updated to mandate that screenshot tests live in the root `screenshots/` directory (not `tests/`), excluded from plain `pytest` runs, and regenerated explicitly with `pytest screenshots/`.  
**Input**: User description: "The signup page is the most crucial page for any django project that wants to allow users to create and manage accounts. The most used 3rd party authentication app is by far django-allauth. This spec is responsible for creating a beautiful, modern and stylish signup page that supports ALL of django-allauth's signup options. The signup form must be reactive to django-allauth settings provided by the developer (e.g. only shows social accounts when this app is available, shows a message when signup is not available, etc.). Django-allauth provides its own "component-like" syntax in its default templates, however, we will NOT be using this, instead opting to use the component system defined by django-cotton and the prebuilt component in the django-mvp package."

## Clarifications

### Session 2026-05-07

- Q: When both social provider buttons AND the email/password form are present, what is the intended visual layout order? → A: Social buttons at the top, horizontal divider ("or"), email/password form below.
- Q: Does the signup page need to handle custom Django User models (`AUTH_USER_MODEL`) — rendering extra fields from a custom model? → A: Delegate entirely to allauth's form machinery; render all fields from allauth's form as-is with no direct `AUTH_USER_MODEL` introspection.
- Q: Should rate limiting or brute-force protection for the signup endpoint be an explicit requirement of this spec? → A: Defer to allauth's built-in rate limiting and host project infrastructure; document as an assumption.
- Q: Which major version of django-allauth should this spec target? → A: Target allauth v65+ (new-style API, current stable).
- Q: How should visual quality (FR-010) be formally validated? → A: ~~No formal visual validation — developer judgment only.~~ *(Superseded by constitution Principle XIII, v1.1.0, 2026-05-07)* Automated pytest-playwright screenshot tests are now required at three canonical viewport sizes (desktop 1440×900, tablet 768×1024, mobile 390×844) for each visually distinct settings permutation. Screenshots must be persisted under `docs/_static/{desktop,tablet,mobile}/` and committed alongside the code.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Developer Enables the Allauth Addon (Priority: P1) **[Developer]**

A developer has an existing Django project using django-allauth and wants a polished, ready-made signup page without writing custom templates. They install `django-accounts-center`, add both `"dac"` and `"dac.addons.allauth"` to their `INSTALLED_APPS`, and the signup page is immediately available — adapting automatically to whatever allauth settings they have configured (email-only, username+email, social providers, etc.) without any further template work.

**Why this priority**: This is the foundational integration experience. The allauth addon (`dac.addons.allauth`) is the primary delivery mechanism for all allauth-specific template overrides and page logic. If enabling it requires more than adding two app entries, the package provides little value over hand-rolled templates.

**Independent Test**: Can be fully tested by creating a fresh Django project with django-allauth installed, adding `"dac"` and `"dac.addons.allauth"` to `INSTALLED_APPS`, and visiting `/account-center/signup/` — the page should render with fields matching the active allauth settings, with no additional configuration.

**Acceptance Scenarios**:

1. **Given** a Django project with only `"dac"` in `INSTALLED_APPS` (allauth addon not enabled), **When** the developer visits `/account-center/signup/`, **Then** allauth's own default templates are used — `dac.addons.allauth` has no effect until enabled.
2. **Given** a developer adds both `"dac"` and `"dac.addons.allauth"` to `INSTALLED_APPS` with allauth configured for email-only signup, **When** the signup page is visited, **Then** it renders with only an email and password field — no username field.
3. **Given** `"dac.addons.allauth"` is enabled and allauth is configured for username + email + password, **When** the developer visits the signup page, **Then** all three fields appear with appropriate labels.
4. **Given** `"dac.addons.allauth"` is enabled and `allauth.socialaccount` is in `INSTALLED_APPS` but no social providers are configured, **When** the signup page renders, **Then** no social account login buttons appear.
5. **Given** `"dac.addons.allauth"` is enabled and at least one social provider is configured (e.g. Google), **When** the signup page renders, **Then** social login buttons appear clearly separated from the email/password form.

---

### User Story 2 - End User Creates Account via Email/Password (Priority: P1) **[End User]**

A new visitor arrives at the signup page intending to create an account. They fill in the form, submit, and are either taken to the email verification step (if required) or directly to their account — all within a modern, visually polished UI.

**Why this priority**: This is the primary end-user flow. The page's quality directly impacts signup conversion rates.

**Independent Test**: Can be fully tested by visiting the signup page as an anonymous user, submitting valid credentials, and confirming redirection to the correct next step.

**Acceptance Scenarios**:

1. **Given** an anonymous user on the signup page, **When** they submit a valid email and password, **Then** the account is created and they are redirected to the email verification notice page if `ACCOUNT_EMAIL_VERIFICATION = "mandatory"`.
2. **Given** an anonymous user on the signup page, **When** they submit a valid email and password with `ACCOUNT_EMAIL_VERIFICATION = "none"`, **Then** the account is created and they are redirected to the `LOGIN_REDIRECT_URL`.
3. **Given** an anonymous user who submits an invalid form (e.g. mismatched passwords, invalid email format), **When** the page re-renders, **Then** each field shows its specific error message inline without losing other field values.
4. **Given** an anonymous user who submits an email address already registered, **When** the page re-renders, **Then** a clear error is shown on the email field.

---

### User Story 3 - End User Signs Up via Social Account (Priority: P2) **[End User]**

A visitor prefers to sign up using an existing social account (e.g. Google, GitHub). They click the provider button on the signup page, are redirected to the provider's OAuth flow, and return to the application as a newly created, authenticated user.

**Why this priority**: Social signup is a significant conversion booster and is a first-class allauth feature that the page must fully support.

**Independent Test**: Can be fully tested by configuring a social provider in allauth settings, visiting the signup page, clicking the social button, completing the OAuth flow, and confirming account creation.

**Acceptance Scenarios**:

1. **Given** a signup page with Google configured as a social provider, **When** the user clicks "Continue with Google", **Then** they are redirected to Google's OAuth consent screen.
2. **Given** a user who completes OAuth with a new social account, **When** allauth processes the callback, **Then** a new user account is created and the user is logged in and redirected appropriately.
3. **Given** multiple social providers configured, **When** the signup page renders, **Then** each provider has its own distinctly labelled button.

---

### User Story 4 - Signup Disabled Message (Priority: P2) **[End User]**

A visitor arrives at the signup page when the application administrator has disabled new signups (e.g. closed beta). Instead of a broken page or generic error, the user sees a clear, friendly message explaining that signup is currently unavailable.

**Why this priority**: Handling disabled-signup gracefully is important for closed-beta, invite-only, or maintenance scenarios.

**Independent Test**: Can be fully tested by setting `ACCOUNT_ALLOW_SIGNUPS = False` (or the allauth equivalent), then visiting `/account-center/signup/` and confirming the message is shown instead of the form.

**Acceptance Scenarios**:

1. **Given** `ACCOUNT_ALLOW_SIGNUPS = False`, **When** an anonymous user visits the signup page, **Then** the registration form is hidden and a clear "Signup is currently unavailable" message is displayed.
2. **Given** `ACCOUNT_ALLOW_SIGNUPS = False`, **When** the page renders, **Then** social account buttons are also hidden (signup via any method is disabled).

---

### User Story 5 - Already Authenticated User Visits Signup (Priority: P3) **[End User]**

A logged-in user navigates to the signup page (e.g. from a bookmark or stale tab). Instead of seeing the signup form again, they are redirected away or shown a message indicating they already have an account.

**Why this priority**: This is a UX polish concern — allauth handles the redirect by default, but the page should not break or confuse an authenticated user.

**Independent Test**: Can be fully tested by logging in, then visiting `/account-center/signup/` directly and confirming the redirect or appropriate message.

**Acceptance Scenarios**:

1. **Given** an authenticated user visiting the signup page, **When** the page loads, **Then** they are redirected to the configured `LOGIN_REDIRECT_URL` or a "You are already signed in" message is displayed.

---

### User Story 6 - End User Signs Up via Passkey (Priority: P2) **[End User]**

A visitor on the signup page sees a "Sign up with a passkey" option when both `MFA_PASSKEY_SIGNUP_ENABLED` and `ACCOUNT_EMAIL_VERIFICATION_BY_CODE_ENABLED` are `True`. They follow this flow to the dedicated passkey signup page (`/account-center/signup/passkey/`), register their device credential, and are onboarded without a traditional password.

**Why this priority**: Passkey signup is a first-class allauth feature when the relevant settings are active; the signup page must surface the option and the dedicated passkey page must be styled consistently using Cotton components.

**Independent Test**: Can be fully tested by setting `MFA_PASSKEY_SIGNUP_ENABLED = True` and `ACCOUNT_EMAIL_VERIFICATION_BY_CODE_ENABLED = True`, visiting `/account-center/signup/`, and confirming the passkey signup option is visible; then visiting `/account-center/signup/passkey/` and confirming the page renders using the `<c-entrance>` shell.

**Acceptance Scenarios**:

1. **Given** `MFA_PASSKEY_SIGNUP_ENABLED = True` and `ACCOUNT_EMAIL_VERIFICATION_BY_CODE_ENABLED = True`, **When** the signup page renders, **Then** a "Sign up with a passkey" option is visible alongside or below the email/password form.
2. **Given** either `MFA_PASSKEY_SIGNUP_ENABLED = False` or `ACCOUNT_EMAIL_VERIFICATION_BY_CODE_ENABLED = False`, **When** the signup page renders, **Then** no passkey signup option is shown.
3. **Given** a user who clicks the passkey signup option, **When** they are directed to `/account-center/signup/passkey/`, **Then** the page renders within the `<c-entrance>` shell using Cotton components, consistent with the rest of the signup UI.
4. **Given** the passkey signup page (`signup_by_passkey.html`), **When** it renders, **Then** it uses the same `<c-entrance>` layout shell and Cotton form components as the main signup page — no raw Bootstrap markup in the template.

---

### Edge Cases

- What happens when allauth is installed but `INSTALLED_APPS` is missing `allauth.account`? The page must not crash — it should fail gracefully with a developer-visible configuration error.
- What happens if a social provider's OAuth credentials are misconfigured? The social button appears normally; errors from the OAuth flow are handled by allauth on the callback URL, not the signup page.
- What happens when the form contains custom fields added via allauth's `ACCOUNT_SIGNUP_FORM_CLASS`? Custom fields must be rendered alongside standard fields.
- What happens when only social providers are available and email signup is fully disabled? The signup page shows only social buttons and hides the email/password form.
- What if no allauth configuration is present at all (misconfigured project)? The component should surface a clear developer error rather than a silent broken UI.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The signup page MUST render a username/email/password form whose visible fields are driven entirely by the active django-allauth `ACCOUNT_*` settings (e.g. `ACCOUNT_USERNAME_REQUIRED`, `ACCOUNT_EMAIL_REQUIRED`).
- **FR-002**: The signup page MUST display social account provider buttons when `allauth.socialaccount` is in `INSTALLED_APPS` and at least one provider is configured. Social buttons MUST appear at the top of the page, followed by a horizontal divider labelled "or", with the email/password form rendered below.
- **FR-003**: Social provider buttons MUST NOT appear when `allauth.socialaccount` is absent from `INSTALLED_APPS` or when no social providers have been configured.
- **FR-004**: The signup page MUST display a "signup unavailable" message and hide all signup forms when allauth's signup-allowed setting evaluates to `False`.
- **FR-005**: The signup form MUST display per-field validation errors inline, immediately below the offending field, without losing values in other fields. Non-field (form-level) errors MUST be displayed as a danger alert above the fields; this is handled automatically by `<c-form.crispy>` — page templates MUST NOT duplicate this logic with their own `{% if form.non_field_errors %}` block.
- **FR-006**: The signup page MUST render all fields provided by allauth's form (including those from `ACCOUNT_SIGNUP_FORM_CLASS`) without any direct introspection of `AUTH_USER_MODEL`. Custom User model support is the developer's responsibility via a compatible `ACCOUNT_SIGNUP_FORM_CLASS`; the page remains model-agnostic.
- **FR-007**: The signup page MUST redirect or gracefully handle the case where the requesting user is already authenticated.
- **FR-008**: The signup page shell MUST be delivered via a dedicated `<c-entrance>` Cotton component (located at `dac/templates/cotton/entrance/index.html`). This component owns the full entrance layout: full-viewport centred container, responsive column width (configured via attrs passed from the allauth layout template), and a styled card. The card renders a `<c-entrance.logo>` sub-component followed by an optional `title` slot, then the page's `{{ slot }}` content. The allauth layout template (`allauth/layouts/entrance.html`) MUST delegate entirely to `<c-entrance>` — it MUST NOT duplicate layout markup. Individual page templates (e.g. `signup.html`) MUST focus solely on their content block and MUST NOT contain card, container, or logo markup.
- **FR-009**: The entrance layout MUST expose two dedicated override points via Cotton component template replacement (no props needed): (1) **`<c-entrance.background>`** (`cotton/entrance/background.html`) — controls the full-page background style (colour, gradient, image). Developers override this file to change the background without touching any other component. (2) **`<c-entrance.logo>`** (`cotton/entrance/logo.html`) — renders the site logo inside the card header. Developers override this file to change the logo; there is no `src` prop — the override is template-level.
- **FR-010**: The page MUST present a modern, visually consistent design that integrates with the rest of the `django-accounts-center` UI system (shared base layout, consistent typography, spacing, and colour usage). Visual quality MUST be validated by automated pytest-playwright screenshot tests (see FR-011); developer code-review judgment is supplementary, not a substitute.
- **FR-011**: Per constitution Principle XIII, the signup page MUST have automated pytest-playwright tests that capture screenshots at three canonical viewports — desktop (1440×900), tablet (768×1024), and mobile (390×844) — and persist them under `docs/_static/{desktop,tablet,mobile}/`. The following settings permutations each produce visually distinct output and MUST each have a full set of three viewport screenshots:
  - `signup-page-social-disabled` — `SOCIALACCOUNT_ENABLED=False` (default email/password form only)
  - `signup-page-social-enabled` — `SOCIALACCOUNT_ENABLED=True` with at least one provider configured (social buttons above divider + email/password form)
  - `signup-page-social-only` — `SOCIALACCOUNT_ONLY=True` (social buttons only, no email/password form)
  - `signup-page-signup-closed` — `is_open_for_signup()` returns `False` (closed message card, no form)
  - `signup-page-passkey-enabled` — `MFA_PASSKEY_SIGNUP_ENABLED=True` and `ACCOUNT_EMAIL_VERIFICATION_BY_CODE_ENABLED=True` (signup page with passkey signup option visible)
  - `signup-by-passkey-page` — screenshot of `/account-center/signup/passkey/` with passkey settings enabled
  Screenshot files MUST follow the naming pattern `<page-name>-<config-slug>.png`. Tests MUST use `@pytest.mark.parametrize` or a shared viewport fixture to avoid logic duplication across viewport sizes. The `docs/_static/desktop/` and `docs/_static/mobile/` directories MUST be created by test setup if they do not exist. Implementing agents MUST visually inspect the generated screenshot files before marking any UI task complete. Per constitution Principle XIII v1.1.2, screenshot tests MUST live in the root `screenshots/` directory (e.g. `screenshots/test_signup_screenshots.py`), NOT inside `tests/`; they are excluded from plain `pytest` runs (which use `testpaths = ["tests"]`) and regenerated explicitly with `pytest screenshots/`.
- **FR-012**: The `signup_by_passkey.html` allauth template override MUST use the `<c-entrance>` Cotton component as its page shell and MUST use Cotton form/button components for its content. It MUST NOT contain raw Bootstrap layout markup (containers, rows, card HTML). The template must be consistent in structure and visual style with `signup.html`.

### Key Entities *(include if feature involves data)*

- **Signup Form**: The form presented to the user at the signup page. Its fields (username, email, password, custom fields) are determined by the active allauth configuration.
- **Social Provider**: An OAuth2/OpenID Connect identity provider (e.g. Google, GitHub, Facebook) configured in `SOCIALACCOUNT_PROVIDERS`. Determines which, if any, social login buttons are displayed.
- **Allauth Configuration**: The collection of Django settings and installed apps that control allauth behaviour — signup availability, required fields, email verification mode, and social account support.
- **Cotton Component**: A reusable, file-based UI component from the django-cotton system (provided by django-mvp) that encapsulates markup and logic for a specific UI element (e.g. a form field, a provider button, a card).
- **`<c-entrance>` Component** (`dac/templates/cotton/entrance/index.html`): The entrance page shell component. Accepts a `title` slot (rendered as an `<h4>` inside the card header) and responsive-width attrs forwarded to `<c-col>`. Renders `<c-entrance.background>` → container → responsive column → card → `<c-entrance.logo>` → title → `{{ slot }}`.
- **`<c-entrance.background>` Component** (`dac/templates/cotton/entrance/background.html`): Wraps the entire entrance page and controls the background style only. Default: `bg-primary-subtle bg-gradient`. Developers override this file to change the page background without modifying any other component.
- **`<c-entrance.logo>` Component** (`dac/templates/cotton/entrance/logo.html`): Renders the site logo at the top of the entrance card. Default: DAC SVG logo at 120px height. Accepts `height`, `alt`, and `class` vars. Developers override the template file to change the logo; there is no `src` prop.
- **`<c-button.stack>` Component** (`mvp/templates/cotton/button/stack.html`): A Bootstrap `vstack` wrapper with a configurable `gap` (default 2) and optional `class`. Used in page content blocks to stack one or more `<c-button>` elements as a full-width vertical group.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A developer with a working allauth installation can have a fully functional, styled signup page in production with no more than 5 lines of new configuration (URL wiring + settings).
- **SC-002**: The signup page correctly adapts its visible fields and controls for all documented allauth field combinations (email-only, username-only, username+email, password confirmation, custom fields) — verified by automated tests covering each combination.
- **SC-003**: A new user can complete the full signup flow (visit page → fill form → submit → confirm account or receive verification email) in under 90 seconds on a standard broadband connection.
- **SC-004**: The signup page renders without errors or visible layout defects across all allauth configuration permutations, including zero social providers, one provider, and multiple providers — confirmed by both automated integration tests and committed viewport screenshots.
- **SC-007**: A full set of pytest-playwright viewport screenshots (desktop 1440×900, tablet 768×1024, mobile 390×844) exists under `docs/_static/` for each of the six visually distinct settings permutations defined in FR-011 (four original permutations plus `signup-page-passkey-enabled` and `signup-by-passkey-page`). All eighteen screenshot files are committed to the repository alongside the implementation and remain non-stale on every subsequent UI-touching pull request.
- **SC-005**: When signup is disabled, 100% of anonymous visitors to the signup URL see the unavailability message rather than a form or an unhandled error page.
- **SC-006**: All Cotton component boundaries in the signup page are documented, enabling developers to identify and override any sub-component within their own project templates.

## Assumptions

- The allauth signup page is delivered via the `dac.addons.allauth` addon. Both `"dac"` and `"dac.addons.allauth"` must be present in `INSTALLED_APPS` for any allauth-specific template overrides or signup page logic to take effect.
- This spec targets **django-allauth v65+** (new-style API). The legacy v0.x API is not supported. The minimum allauth version will be enforced as a package dependency.
- The django-accounts-center package assumes django-allauth is installed and properly configured in the host project; it is not responsible for allauth setup or migrations.
- The `django-mvp` package is a dependency and its Cotton component library is available at render time.
- django-cotton is installed and configured as a template engine in the host project's `TEMPLATES` setting.
- Mobile responsiveness is assumed to be provided by the base layout and shared Cotton components from django-mvp; this spec does not mandate a specific CSS framework but assumes the mvp package's default styling.
- Multi-factor authentication (MFA) enrollment during signup is out of scope for this page; MFA is handled post-login by allauth's MFA flow.
- The signup page does not handle password reset or login — those are separate pages in django-accounts-center.
- Social account connection (linking a social account to an existing user) is distinct from social signup and is out of scope for this spec.
- The developer is responsible for providing OAuth credentials for any social providers; the signup page simply reflects what is configured.
- Rate limiting and brute-force protection for the signup endpoint are delegated to allauth's built-in `ACCOUNT_RATE_LIMITS` mechanism and the host project's infrastructure (e.g. reverse proxy, WAF). The signup page component itself imposes no additional rate-limiting logic.
- Accessibility (WCAG 2.1 AA) is assumed as a baseline but detailed accessibility audit is out of scope for this spec iteration.
