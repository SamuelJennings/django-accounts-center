# Feature Specification: Allauth Password Reset Flow

**Feature Branch**: `003-allauth-password-reset`  
**Created**: 2026-05-11  
**Status**: Refined  
**Refined**: 2026-05-11 — Updated FR-001, FR-002, FR-003, FR-005, FR-006, FR-010 to match implemented template changes: `<c-entrance.text>` used for all informational paragraphs; submit button on `password_reset.html` labelled "Send email" (was "Reset My Password"); submit button on `password_reset_from_key.html` labelled "Confirm" (was "Change Password"); `confirm_password_reset_code.html` only overrides `title_` (not `head_title_`) and uses fail-silent URL pattern for action URLs.  

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Standard Email-Link Password Reset (Priority: P1) **[End User]**

A registered user who has forgotten their password navigates to the "Forgot Password?" link on the
login page. They are presented with a clean email-input form, submit their address, see a
confirmation screen telling them to check their inbox, click the link in the email, enter and
confirm a new password on the reset form, and are shown a success confirmation. The entire journey
must feel as polished and trustworthy as the login page.

**Why this priority**: This is the primary recovery path for locked-out users. A confusing or
visually inconsistent reset flow erodes trust and generates support tickets.

**Independent Test**: Navigate to the password-reset URL, submit a valid registered email, follow
the emailed link, set a new password, and verify the success page is displayed. Can be fully
validated with a live Django test client or Playwright screenshot test.

**Acceptance Scenarios**:

1. **Given** a registered user on the `account/password_reset.html` page, **When** they submit their email address, **Then** they are redirected to `account/password_reset_done.html` with a confirmation message, regardless of whether the email is registered.
2. **Given** a user on `account/password_reset_done.html`, **When** they view the page, **Then** they see a clear message instructing them to check their email, rendered within the `<c-entrance>` shell.
3. **Given** a user who has clicked a valid reset link, **When** they arrive at `account/password_reset_from_key.html`, **Then** they see a new-password form (two fields: new password and confirmation) rendered using Cotton form components.
4. **Given** a user on `account/password_reset_from_key.html` who clicks the Cancel button, **When** the cancel form is submitted, **Then** the user is logged out of the mid-reset session and redirected to the login page.
5. **Given** a user who has submitted a valid new password, **When** the form is accepted, **Then** they are shown `account/password_reset_from_key_done.html` confirming their password has been changed.

---

### User Story 2 — Invalid or Expired Reset Link (Priority: P1) **[End User]**

A user clicks a password-reset link from an old email (already used or expired). Instead of a blank
error or an unhandled exception, they are presented with the invalid-token branch of
`account/password_reset_from_key.html`: a clear message explaining the link is no longer valid and
a prominent call-to-action to request a new reset link.

**Why this priority**: Without a clear recovery path, users with expired links are completely stuck.
This is the second most common support scenario after the happy path.

**Independent Test**: Construct a request with an invalid/expired key token and assert the invalid-
token branch is rendered with a link back to `account/password_reset.html`.

**Acceptance Scenarios**:

1. **Given** a user who navigates to a reset URL with an invalid or already-used token, **When** the page renders, **Then** they see the invalid-token error branch (not the new-password form) with an explanation and a link to request a fresh reset email.
2. **Given** the invalid-token branch, **When** a user clicks the "request a new link" call-to-action, **Then** they are taken to `account/password_reset.html` to begin the flow again.

---

### User Story 3 — Email Enumeration Protection (Priority: P2) **[End User]**

A user submits a password-reset request for an email address that is not registered in the system.
Allauth silently accepts the request and displays the same "check your email" confirmation page as
for a valid address, preventing account enumeration.

**Why this priority**: This is a security requirement — leaking whether an email is registered
allows targeted attacks. allauth handles this at the application layer; the template must not
contradict it.

**Independent Test**: Submit a reset request for a non-existent email address and assert that the
response is `account/password_reset_done.html` with no error message.

**Acceptance Scenarios**:

1. **Given** a user submits the password-reset form with an unrecognised email address, **When** the form is processed, **Then** they are shown `account/password_reset_done.html` with the same wording as for a valid address — no error, no difference in response.

---

### User Story 4 — Code-Based Password Reset (Priority: P2) **[End User]**

When the Django deployment has `ACCOUNT_EMAIL_VERIFICATION_BY_CODE_ENABLED = True`, allauth routes
password reset confirmation through `account/confirm_password_reset_code.html`. The user enters a
short-lived numeric code delivered to their email instead of following a link. This page must extend
`account/base_confirm_code.html` and carry consistent styling with the rest of the code-entry flow.

**Why this priority**: Not all deployments use this feature, but those that do must present a
consistent code-entry experience across all flows (login codes, email verification codes, and
password-reset codes).

**Independent Test**: With `ACCOUNT_EMAIL_VERIFICATION_BY_CODE_ENABLED = True`, complete a
password-reset flow and assert the code-entry page renders correctly, inheriting structure from
`base_confirm_code.html`.

**Acceptance Scenarios**:

1. **Given** `ACCOUNT_EMAIL_VERIFICATION_BY_CODE_ENABLED = True` and a user who has submitted the password-reset form, **When** allauth dispatches the numeric code, **Then** the user is shown `account/confirm_password_reset_code.html` with a code-entry field, consistent with the login-code and email-verification-code pages.
2. **Given** a user on the code-entry page who submits a valid code, **When** the code is verified, **Then** they are taken to the new-password form (`account/password_reset_from_key.html`).
3. **Given** a user who submits an expired or incorrect code, **When** validation fails, **Then** an inline error is displayed and the code-entry field retains focus.

---

### User Story 5 — Developer Template Integration (Priority: P1) **[Developer]**

A developer installs `dac.addons.allauth` into a Django project. After configuring allauth, all
five password-reset templates are automatically served by the addon without any additional template
directories being added. Every template renders without errors at a standard browser viewport, uses
the `<c-entrance>` shell, and contains zero instances of the `{% element %}` syntax.

**Why this priority**: Seamless drop-in integration is the core value proposition of the package.
If any template fails silently or falls back to an allauth default, the developer has no indication
something is wrong.

**Independent Test**: Boot the example Django app, navigate each of the five password-reset URL
endpoints, and assert HTTP 200 responses with valid HTML containing `<c-entrance>` wrapper markup.

**Acceptance Scenarios**:

1. **Given** a Django project with `dac.addons.allauth` installed, **When** the developer navigates to any of the five password-reset URLs, **Then** each page returns HTTP 200 with the `<c-entrance>` shell rendered.
2. **Given** the addon templates directory, **When** a developer inspects any of the five password-reset templates, **Then** zero `{% element %}` tags are present.
3. **Given** the example app running, **When** screenshot tests execute for the four standard templates, **Then** all tests pass across desktop (1440 px), tablet (768 px), and mobile (390 px) viewports.

---

### Edge Cases

- What happens when the reset link token has been tampered with (not just expired, but malformed)? → Allauth normalises this to the same invalid-key branch; the template must handle it identically.
- What happens when `ACCOUNT_EMAIL_VERIFICATION_BY_CODE_ENABLED = True` but the user navigates directly to the link-based reset URL? → Allauth redirects to the code flow; the template does not need to handle this case.
- What happens when a user submits mismatched passwords on `password_reset_from_key.html`? → Form validation errors must be displayed inline without clearing the fields.
- What happens when `base_confirm_code.html` is rendered for the password-reset code context versus the login-code context? → The page title and recipient display differ; the base template must accept these as block overrides.
- What happens when a logged-in user navigates to `password_reset.html` or `password_reset_done.html`? → The `already_logged_in` snippet is rendered above the main content, exactly as allauth's originals do.
- What happens when `can_resend` is `False` on the code-entry page? → The "Request new code" button is hidden; only the "Confirm" and "Cancel" buttons appear.
- What happens when `can_change` is `True` on `base_confirm_code.html`? → A collapsible change-form section is rendered below the confirm form, allowing the user to change their email/phone before resending.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The addon MUST provide an override for `account/password_reset.html` that renders: the `already_logged_in` snippet when `user.is_authenticated` is true; a description paragraph and a trailing "contact us" paragraph rendered via `<c-entrance.text>` (description with `center` modifier, contact-us with `small` modifier); and an email-input form using `<c-form>` with a "Send email" submit button (inside `<c-button.stack>`, with `icon="send"` and `variant="primary"`), including `{{ redirect_field }}` as a hidden input inside the form body — all within a `<c-entrance>` shell.
- **FR-002**: The addon MUST provide an override for `account/password_reset_done.html` that renders: the `already_logged_in` snippet when `user.is_authenticated` is true; and a "check your spam folder" informational paragraph rendered via `<c-entrance.text center>` — within a `<c-entrance>` shell. No form or button is present.
- **FR-003**: The addon MUST provide an override for `account/password_reset_from_key.html` that renders both branches within a `<c-entrance>` shell: (a) the valid-token branch renders the new-password form with `{{ redirect_field }}` as a hidden input, a "Confirm" submit button (inside `<c-button.stack>`, with `icon="submit"` and `variant="primary"`), and a secondary "Cancel" button (`icon="x-circle"`) that signs the user out and redirects to the login page; (b) the invalid-token branch renders an explanatory `<c-entrance.text>` block containing an inline link to request a new reset.
- **FR-004**: The Cancel action on `account/password_reset_from_key.html` MUST replicate the allauth mechanism: a hidden `<form>` that POSTs to `account_logout` with `next` → `account_login`, triggered by the Cancel button, so that the mid-reset session is terminated on cancel.
- **FR-005**: The addon MUST provide an override for `account/password_reset_from_key_done.html` that renders a "Your password is now changed." confirmation via `<c-entrance.text center>` within a `<c-entrance>` shell. No button, link, or further action is present.
- **FR-006**: The addon MUST provide an override for `account/confirm_password_reset_code.html` that extends `account/base_confirm_code.html` and customises the `title_` block (page heading), the `recipient` block (email link display), and the `action_url` / `action_url_resend` blocks using a fail-silent `{% url ... as var %}{{ var }}` pattern so the template renders correctly in contexts where the code-based URL is not registered. The `head_title_` block is not overridden.
- **FR-007**: The existing `account/base_confirm_code.html` override MUST be fully rewritten to replace all `{% element %}` syntax with Cotton components. The rewritten base template must faithfully replicate the allauth original's full structure: the `can_resend` conditional "Request new code" button, the `cancel_url` / logout-from-stage conditional cancel button, the hidden `<form id="resend">` element, the hidden logout-from-stage `<form>` when `cancel_url` is absent, the `can_change` collapsible change-form section, and `{{ redirect_field }}` in all relevant form bodies.
- **FR-008**: All five templates MUST contain zero instances of `{% element %}` syntax after implementation.
- **FR-009**: Screenshot tests MUST cover five distinct page states at desktop (1440 px), tablet (768 px), and mobile (390 px) viewports (15 screenshots total): `password_reset.html`, `password_reset_done.html`, `password_reset_from_key.html` valid-token form state, `password_reset_from_key.html` invalid-token error state, and `password_reset_from_key_done.html`.
- **FR-010**: All six modified templates MUST conform to the component usage patterns documented in `contracts/component-interface.md`. Specifically: primary user-facing forms MUST use `<c-form>` (not raw `<form>`); button groups MUST use `<c-button>` and `<c-button.stack>`; the `<c-entrance>` shell MUST wrap each page body; descriptive and informational text MUST use `<c-entrance.text>` (with optional `center` and `small` modifiers) rather than raw `<p>` tags. Any deviation MUST be justified in a PR comment and reflected in an update to the contracts document. Validated by code review against `contracts/component-interface.md`.

### Key Entities

- **Password Reset Request**: A user-initiated flow keyed by email address; allauth generates a signed URL token or numeric code and dispatches it by email.
- **Reset Token**: A short-lived credential embedded in the reset URL (link-based flow) or delivered as a numeric code (code-based flow); becomes invalid after a single use or expiry.
- **Reset Flow Variant**: Either "link-based" (default) or "code-based" (when `ACCOUNT_EMAIL_VERIFICATION_BY_CODE_ENABLED = True`); determines which fifth template is used.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: All five password-reset template URLs return HTTP 200 with no template errors when the addon is installed.
- **SC-002**: Zero `{% element %}` tags appear in any of the five overridden template files.
- **SC-003**: Screenshot tests pass for all five page states at all three viewport sizes (15 screenshots total: 5 states × 3 viewports), including both the valid-token form and the invalid-token error branch of `password_reset_from_key.html`.
- **SC-004**: The invalid-token branch is reachable via a direct test-client request and renders a visible link to `account/password_reset` without any server error.
- **SC-005**: A full end-to-end password-reset flow (request → done → follow link → set password → success) can be completed using the Django test client without encountering any rendering exception.
- **SC-006**: The code-entry page (`confirm_password_reset_code.html`) renders identically in structure to the login-code and email-verification-code pages when inspected side-by-side.

## Clarifications

### Session 2026-05-11

- Q: Does `password_reset_from_key_done.html` need a "Sign In" CTA or any outbound action? → A: Informational only — no button, no link. Replicate the allauth original (heading + "Your password is now changed." paragraph, no further action).
- Q: What is the general principle for Cotton replicas of allauth templates? → A: Replicate allauth exactly. If the original template has a UI element or conditional, the Cotton override must have it too. No additions or omissions beyond the component syntax change.
- Q: Should screenshot tests cover both states of `password_reset_from_key.html` (valid-token form and invalid-token error) separately? → A: Yes — both states screenshotted separately, giving 5 states × 3 viewports = 15 screenshots total.
- Q: Should the Cancel button/logout mechanism on `password_reset_from_key.html` have an explicit acceptance scenario? → A: Yes — add a Cancel scenario to User Story 1.
- Q: Should `redirect_field` be called out explicitly in the requirements? → A: Yes — document it in FR-001 and FR-003; it is part of the allauth originals and must not be omitted.
- Q: Does `base_confirm_code.html` still need to be converted to Cotton components, or has it already been done? → A: The existing DAC override still uses `{% element %}` syntax throughout — it must be fully rewritten as Cotton components as part of this spec, not merely validated.

## Assumptions

- All five Cotton overrides replicate allauth's original templates exactly: every UI element, conditional, and paragraph present in the allauth source must appear in the Cotton version. No additions or omissions beyond the component syntax change.
- The four standard templates are entrance-style pages (pre-authentication) and must use `<c-entrance>` rather than any manage-page shell.
- `confirm_password_reset_code.html` requires only block-level customisation of `base_confirm_code.html` (title, recipient hint, action URL, and any extra tags); the base template's Cotton structure does not need to be rewritten.
- The Cotton components `<c-form>`, `<c-button>`, and `<c-entrance>` are already available in the addon and have been validated by the signup and login template implementations.
- Allauth's email-enumeration protection (silent acceptance for unrecognised emails) is handled at the view layer; templates do not need to implement or work around it.
- Performance and load requirements match existing entrance-page templates; no additional caching or optimisation is in scope.
- The `base_confirm_code.html` override already exists but still uses `{% element %}` syntax and must be fully rewritten as Cotton components as part of this spec.
- Mobile-responsive layout is inherited from the `<c-entrance>` shell and Bootstrap utilities; no custom breakpoint CSS is expected.
