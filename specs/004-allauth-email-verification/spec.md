# Feature Specification: Allauth Email Verification Flow

**Feature Branch**: `004-allauth-email-verification`  
**Created**: 2026-05-11  
**Status**: Refined  
**Refined**: 2026-05-11 — Updated FR-001 and FR-005 to specify `<c-entrance.text center>` modifier; updated FR-002 to specify `"Confirm"` button label with `icon="check-circle"` and test guidance (assert non-empty text + icon element, not specific values).  

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Standard Email Verification (Priority: P1) **[End User]**

A user signs up for an account on a site where `ACCOUNT_EMAIL_VERIFICATION = "mandatory"`. After
registration they are redirected to `account/verification_sent.html`, which informs them to check
their inbox. They click the link in the email, arrive at `account/email_confirm.html`, press the
single confirm button, and their address is verified. The entire journey must feel as polished and
consistent with the signup and login pages.

**Why this priority**: Email verification is the mandatory gate between signup and first use for the
majority of allauth deployments. A confusing or visually broken verification page causes users to
abandon registration.

**Independent Test**: Navigate to the verification-sent URL and assert the informational page
renders; then craft a valid confirmation URL, follow it, submit the confirm form, and assert the
address is verified. Can be fully validated with a Django test client.

**Acceptance Scenarios**:

1. **Given** a user who has just registered with mandatory email verification, **When** they are redirected to `account/verification_sent.html`, **Then** they see a clear instructional message rendered within the `<c-entrance>` shell with no form present.
2. **Given** a user who has received a verification email and clicked the link, **When** they arrive at `account/email_confirm.html` with a valid key (`can_confirm = True`), **Then** they see a single confirm button within a `<c-form>` inside the `<c-entrance>` shell.
3. **Given** a user on `account/email_confirm.html` with a valid key, **When** they submit the confirm form, **Then** their email address is marked verified and allauth redirects them according to the configured post-verification URL.

---

### User Story 2 — Invalid or Expired Verification Link (Priority: P1) **[End User]**

A user clicks a verification link from an old email (already used, expired, or belonging to a
different account). Instead of an unhandled error, they are presented with the invalid-key branch
of `account/email_confirm.html`: a clear message explaining the link is no longer valid and
guidance on how to proceed.

**Why this priority**: Expired links are a common real-world occurrence. Users who arrive at a
broken link with no recovery path are likely to contact support or abandon the flow entirely.

**Independent Test**: Construct a request to the email-confirm URL with an invalid key and assert
that the invalid-key branch renders with an explanatory message rather than raising an exception.

**Acceptance Scenarios**:

1. **Given** a user who navigates to the email-confirm URL with an invalid, expired, or already-used key (`can_confirm = False`), **When** the page renders, **Then** they see the invalid-key branch with an explanatory message and no confirm button.
2. **Given** a user on the invalid-key branch, **When** they follow any provided guidance link, **Then** they are directed to a page where they can take a next step (such as requesting a new verification email from their account).

---

### User Story 3 — Code-Based Email Verification (Priority: P2) **[End User]**

When the deployment has `ACCOUNT_EMAIL_VERIFICATION_BY_CODE_ENABLED = True`, allauth routes
email verification through `account/confirm_email_verification_code.html`. The user enters a
short-lived numeric code delivered to their inbox instead of following a link. This page must extend
`account/base_confirm_code.html` and carry consistent styling with the rest of the code-entry flow.

**Why this priority**: Not all deployments use this feature, but those that do must present a
consistent code-entry experience across all flows (login codes, password-reset codes, and
email-verification codes).

**Independent Test**: With `ACCOUNT_EMAIL_VERIFICATION_BY_CODE_ENABLED = True`, trigger the
email-verification code flow and assert the code-entry page renders correctly, inheriting structure
from `base_confirm_code.html`.

**Acceptance Scenarios**:

1. **Given** `ACCOUNT_EMAIL_VERIFICATION_BY_CODE_ENABLED = True` and a user who has registered, **When** allauth dispatches the numeric verification code, **Then** the user is shown `account/confirm_email_verification_code.html` with a code-entry field, consistent in structure with the login-code and password-reset-code pages.
2. **Given** a user on the code-entry page who submits a valid code, **When** the code is verified, **Then** their email address is marked verified and allauth redirects them.
3. **Given** a user who submits an expired or incorrect code, **When** validation fails, **Then** an inline error is displayed and the code-entry field retains focus.

---

### User Story 4 — Account Inactive Error Page (Priority: P2) **[End User]**

An administrator deactivates a user account. When that user subsequently attempts to log in,
allauth redirects them to `account/account_inactive.html`. The page must render within the
`<c-entrance>` shell (not the raw `allauth/layouts/entrance.html` layout) and display a brief but
clear message explaining their account is inactive.

**Why this priority**: A deactivated-account page that falls back to an unstyled or inconsistent
layout breaks the visual contract of the application and reflects poorly on the site operator.

**Independent Test**: Boot the example app with a deactivated user and assert that the
`account_inactive` URL returns HTTP 200 with the `<c-entrance>` shell rendered.

**Acceptance Scenarios**:

1. **Given** a deactivated user account, **When** allauth redirects to `account/account_inactive.html`, **Then** the page renders within the `<c-entrance>` shell with an explanatory message.
2. **Given** the rendered `account_inactive.html`, **When** the HTML is inspected, **Then** it does not extend `allauth/layouts/entrance.html` directly; it uses the Cotton `<c-entrance>` component.

---

### User Story 5 — Developer Template Integration (Priority: P1) **[Developer]**

A developer installs `dac.addons.allauth` into a Django project. After configuring allauth, all
four email-verification templates are automatically served by the addon without any additional
template directories being added. Every template renders without errors at standard browser
viewports, uses the `<c-entrance>` shell, and contains zero instances of the `{% element %}` syntax.

**Why this priority**: Seamless drop-in integration is the core value proposition of the package.
If any template fails silently or falls back to an allauth default, the developer has no indication
something is wrong.

**Independent Test**: Boot the example Django app, navigate each of the four email-verification
URL endpoints (including both branches of `email_confirm.html`), and assert HTTP 200 responses with
valid HTML containing the `<c-entrance>` wrapper.

**Acceptance Scenarios**:

1. **Given** a Django project with `dac.addons.allauth` installed, **When** the developer navigates to any of the four email-verification URLs, **Then** each page returns HTTP 200 with the `<c-entrance>` shell rendered.
2. **Given** the addon templates directory, **When** a developer inspects any of the four email-verification templates, **Then** zero `{% element %}` tags are present.
3. **Given** the example app running, **When** screenshot tests execute across desktop (1440 px), tablet (768 px), and mobile (390 px) viewports, **Then** all tests pass for all covered page states.

---

### Edge Cases

- What happens when a verification link is clicked by a user who is already logged in and already verified? → `can_confirm = False`; the invalid-key branch is shown. The template must handle this identically to an expired link.
- What happens when the verification link token is malformed (not merely expired)? → Allauth normalises this to the same invalid-key branch; the template must handle it identically.
- What happens when `ACCOUNT_EMAIL_VERIFICATION_BY_CODE_ENABLED = True` but the user navigates directly to the link-based confirmation URL? → Allauth handles the redirect; the template does not need to handle this case.
- What happens when `can_resend` is `False` on the code-entry page? → The "Request new code" button is hidden; only the "Confirm" and "Cancel" buttons appear (inherited from `base_confirm_code.html`).
- What happens when `can_change` is `True` on `base_confirm_code.html`? → A collapsible change-form section is rendered below the confirm form, inherited from `base_confirm_code.html`.
- What happens when `account_inactive.html` is visited by a user whose account has been reactivated? → Allauth prevents the redirect from happening at the view layer; the template does not need to guard against this.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The addon MUST provide an override for `account/verification_sent.html` that renders an informational message (no form, no submit button) within a `<c-entrance>` shell, using `<c-entrance.text center>` for descriptive paragraphs, consistent with the visual style of the signup and login pages.
- **FR-002**: The addon MUST provide an override for `account/email_confirm.html` that handles both branches within a `<c-entrance>` shell: (a) the valid-key branch (`can_confirm = True`) renders a confirm form using `<c-form>` and `<c-button>` with a primary submit button labelled `"Confirm"` with `icon="check-circle"` (inside `<c-button.stack>`, `variant="primary"`); (b) the invalid-key branch renders an explanatory `<c-entrance.text>` block with guidance on next steps, and no form or submit button. Integration tests for the confirm button MUST assert that button text is non-empty and that an icon element is rendered — they MUST NOT assert the specific label string or icon name, as these may change independently of the template structure.
- **FR-003**: The `account/email_confirm.html` override MUST replicate the allauth original exactly in all conditionals and UI elements: every element, paragraph, and branch present in the allauth source must appear in the Cotton version. No additions or omissions beyond the component syntax change.
- **FR-004**: The addon MUST provide an override for `account/confirm_email_verification_code.html` that extends `account/base_confirm_code.html` and customises the `title_` block (page heading), the `recipient` block (email address display), and the `action_url` / `action_url_resend` blocks using a fail-silent `{% url ... as var %}{{ var }}` pattern so the template renders correctly in contexts where the code-based URL is not registered. The `head_title_` block is not overridden.
- **FR-005**: The addon MUST provide an override for `account/account_inactive.html` that uses the `<c-entrance>` Cotton component shell rather than extending `allauth/layouts/entrance.html` directly. The page content is a brief explanatory message rendered via `<c-entrance.text center>`, with no form or interactive controls.
- **FR-006**: All four templates MUST contain zero instances of `{% element %}` syntax after implementation.
- **FR-007**: Screenshot tests MUST cover five distinct page states at desktop (1440 px), tablet (768 px), and mobile (390 px) viewports (15 screenshots total): `verification_sent.html`, `email_confirm.html` valid-key branch, `email_confirm.html` invalid-key branch, `confirm_email_verification_code.html`, and `account_inactive.html`.
- **FR-008**: All four template overrides MUST conform to the component usage patterns documented in `contracts/component-interface.md`. Specifically: primary user-facing forms MUST use `<c-form>` (not raw `<form>`); button groups MUST use `<c-button>` and `<c-button.stack>`; the `<c-entrance>` shell MUST wrap each page body; descriptive and informational text MUST use `<c-entrance.text>` rather than raw `<p>` tags. Any deviation MUST be justified in a PR comment and reflected in an update to the contracts document.

### Key Entities

- **Email Verification Token**: A signed URL token or numeric code confirming ownership of an email address; becomes invalid after a single use or expiry.
- **Account Status**: Whether a user account is active or has been deactivated by an administrator; determines whether the user is directed to `account_inactive.html` after a login attempt.
- **Verification Flow Variant**: Either "link-based" (default) or "code-based" (when `ACCOUNT_EMAIL_VERIFICATION_BY_CODE_ENABLED = True`); determines whether the code-entry template is used instead of the link-confirmation template.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: All four email-verification template URLs return HTTP 200 with no template errors when the addon is installed.
- **SC-002**: Zero `{% element %}` tags appear in any of the four overridden template files.
- **SC-003**: Screenshot tests pass for all five page states at all three viewport sizes (15 screenshots total: 5 states × 3 viewports), including both the valid-key form and the invalid-key error branch of `email_confirm.html`.
- **SC-004**: Both branches of `email_confirm.html` are reachable via a direct test-client request and render without any server error; the invalid-key branch displays an explanatory message with no form.
- **SC-005**: `account_inactive.html` renders the `<c-entrance>` shell wrapper; a string search of the template file finds no direct extension of `allauth/layouts/entrance.html`.
- **SC-006**: The code-entry page (`confirm_email_verification_code.html`) inherits the same block structure from `account/base_confirm_code.html` as `account/confirm_login_code.html` and `account/confirm_password_reset_code.html`; a source inspection of the three files confirms each overrides `title_`, `recipient`, `action_url`, `action_url_resend`, `extra_tags`, and `change_title` — and none override `head_title_`.

## Clarifications

### Session 2026-05-11

- Q: What label and icon should the confirm button on `email_confirm.html` use? → A: `"Confirm"` label with `icon="check-circle"`. Integration tests must assert non-empty button text and a rendered icon element — not the specific label or icon name.
- Q: Which `<c-entrance.text>` modifier should `verification_sent.html` and `account_inactive.html` use? → A: `center` modifier on all `<c-entrance.text>` paragraphs on both pages, consistent with `password_reset_done.html` and `password_reset_from_key_done.html` in Spec 003.

## Assumptions

- All four Cotton overrides replicate allauth's original templates exactly: every UI element, conditional, and paragraph present in the allauth source must appear in the Cotton version. No additions or omissions beyond the component syntax change.
- The four templates are entrance-style pages (pre-authentication or gate-context) and must use `<c-entrance>` rather than any manage-page shell.
- `confirm_email_verification_code.html` requires only block-level customisation of `base_confirm_code.html` (title, recipient hint, action URLs, and any extra tags); the base template's Cotton structure does not need to be rewritten as part of this spec (it was fully rewritten in Spec 003).
- The Cotton components `<c-form>`, `<c-button>`, `<c-entrance>`, and `<c-entrance.text>` are already available in the addon and have been validated by the signup, login, and password-reset template implementations.
- Performance and load requirements match existing entrance-page templates; no additional caching or optimisation is in scope.
- This spec does not add any functionality beyond what the standard allauth templates provide. Any context variable referenced in the allauth originals is assumed to be available to the Cotton overrides.
