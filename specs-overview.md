# Specs Overview: django-accounts-center

This document catalogues proposed future feature specifications for the `django-accounts-center` package,
ordered by recommended implementation priority. Each entry describes the scope and intent of a prospective
spec in the same narrative style used in individual `spec.md` files, enabling them to be promoted directly
into a `speckit.specify` workflow.

**Completed to date**: Spec 001 (allauth signup page) and Spec 002 (allauth login page) are fully
implemented and merged. The allauth addon (`dac.addons.allauth`) now overrides all signup-flow templates
(`account/signup.html`, `account/signup_closed.html`, `account/signup_by_passkey.html`) and all
login-flow templates (`account/login.html`, `account/request_login_code.html`,
`account/confirm_login_code.html`, `socialaccount/login.html`, `socialaccount/login_cancelled.html`,
`socialaccount/login_redirect.html`) with Cotton-based components.

---

## Spec 003 — Allauth Password Reset Flow

The password reset flow is the second-most-trafficked user journey in any email-based authentication
system. When a user forgets their credentials, they must be guided through a multi-step process that
feels as polished and trustworthy as the login page itself. This spec is responsible for modernising all
password-reset templates provided by django-allauth, replacing the `{% element %}` component syntax
with Cotton components consistent with the rest of the entrance page suite.

The flow covers four standard templates: `account/password_reset.html` (the email-input form where
users request a reset link), `account/password_reset_done.html` (the confirmation screen shown after
the reset email is dispatched), `account/password_reset_from_key.html` (the new-password form
accessed via the emailed link, including the invalid-token error branch), and
`account/password_reset_from_key_done.html` (the success confirmation shown after the password is
changed). All four are entrance-style pages and must use the `<c-entrance>` shell.

When `ACCOUNT_EMAIL_VERIFICATION_BY_CODE_ENABLED = True`, allauth exposes a fifth template,
`account/confirm_password_reset_code.html`, which extends `account/base_confirm_code.html` and
presents a short-lived numeric code instead of a link. This template must also be in scope, as it is
part of the same user journey and must carry consistent styling. The existing `base_confirm_code.html`
base template (already overriding allauth's defaults) delegates most rendering to Cotton components and
should be validated as part of this spec.

Key scenarios include: a user who requests a reset for an unrecognised email address (allauth silently
accepts and still shows the "done" page to prevent email enumeration); a user who clicks an expired or
already-used reset link and is shown the invalid-token branch with a clear call-to-action to request
a new link; a user who successfully sets a new password and is redirected or shown a confirmation
message; and a user who completes the code-based reset flow when that allauth feature is active.
Screenshot tests must cover the four standard templates across desktop, tablet, and mobile viewports.

---

## Spec 004 — Allauth Email Verification Flow

Email verification is a gate that most allauth-powered applications place between signup and first
use. The pages in this flow are entrance-style pages shown to anonymous users immediately after
registration or when they attempt to access a protected resource without a verified email. This spec
is responsible for modernising all email-verification templates, replacing the `{% element %}` syntax
with Cotton components and ensuring visual consistency with the signup and login pages.

The scope covers four templates. `account/verification_sent.html` is the informational page shown
after signup when `ACCOUNT_EMAIL_VERIFICATION = "mandatory"`, telling the user to check their inbox;
it carries no form and should be rendered using `<c-entrance.text>` and informational Cotton elements.
`account/email_confirm.html` is the confirmation page reached by clicking the link in the
verification email; it presents a single confirm button to finalise ownership of the address, and must
handle both the `can_confirm` (valid key) and invalid-key branches gracefully.
`account/confirm_email_verification_code.html` is the code-based variant activated when
`ACCOUNT_EMAIL_VERIFICATION_BY_CODE_ENABLED = True`; it extends `account/base_confirm_code.html` and
must be validated against the base template's Cotton structure. `account/account_inactive.html` is
the error page shown when allauth blocks login because the account has been deactivated by an
administrator; though brief, it must use the `<c-entrance>` shell rather than the raw
`allauth/layouts/entrance.html` it currently extends.

Key scenarios include: a user who signs up and is directed to the verification-sent page; a user who
clicks a valid email link and is confirmed and redirected; a user who clicks an expired or reused
link and receives a clear error message with guidance; a user who completes code-based verification
by entering a short-lived code; and a developer who deactivates an account and sees the
account-inactive page rendered correctly within the entrance shell.

---

## Spec 005 — Allauth Core Session and Reauthentication Pages

Several short but important templates support the session lifecycle for authenticated users: the
logout confirmation page, the reauthentication challenge, and the "you must verify your email to
continue" gate. These pages are each visited frequently and must carry the same level of visual
polish as the rest of the allauth template suite. This spec is responsible for modernising all three
using Cotton components, choosing the appropriate base template for each (entrance shell for
gate-style pages, manage shell for account-management-adjacent pages).

`account/logout.html` is the confirmation form displayed when a user initiates sign-out; it presents
a single "Sign Out" button and must use the manage-page shell (`<c-manage>` or the existing
`base_manage.html` override) since it is typically reached from inside the authenticated application.
`account/reauthenticate.html` is the password-challenge form shown when allauth requires the user
to re-confirm their identity before a sensitive action; it extends `account/base_reauthenticate.html`
and must render the password field and confirm button using `<c-form>` and `<c-button>`.
`account/verified_email_required.html` is the gate page shown when a user attempts to access a
resource protected by `@verified_email_required` but has not yet completed email verification; it
contains explanatory text and a link to the email management page, and is best rendered using the
manage-page shell since the user is already logged in.

Key scenarios include: an authenticated user clicking "Sign Out" and being presented with the
confirmation form; a user whose session requires reauthentication entering their password and
being redirected back to the original action; a user with an unverified email address hitting a
protected page and seeing the verified-email-required gate with clear instructions for completing
verification.

---

## Spec 006 — Allauth Email Address Management

Logged-in users in allauth-powered applications often need to manage their email addresses: adding
a new address, changing their primary address, removing old addresses, or resending verification to
an unverified pending address. These management pages sit inside the authenticated account area and
must use the manage-page shell (`base_manage_email.html`) rather than the entrance shell. This spec
is responsible for modernising both email management templates using Cotton components.

`account/email.html` is the primary email management page, rendered at `account_email`. It lists
all email addresses associated with the account as radio-button options, each labelled with their
verification status (verified/unverified) and primary status. It also provides "Make Primary",
"Re-send Verification", and "Remove" action buttons, and — when `can_add_email` is `True` — an
inline form for adding a new email address. The current template is densely constructed using
`{% element %}` and must be rebuilt using `<c-form>`, `<c-button>`, and appropriate badge or tag
components for the status indicators, while preserving the full action surface.

`account/email_change.html` is the simplified variant shown when allauth is configured for
single-email mode (`ACCOUNT_MAX_EMAIL_ADDRESSES = 1`); it renders the current email (read-only),
optionally a pending-change address with a re-send-verification button, and a form for entering a
new address. It must be rebuilt using Cotton form and button components, with the pending-state
conditional clearly handled.

Key scenarios include: a user viewing their list of email addresses with each one's status clearly
indicated; a user making a different address primary; a user removing a secondary address; a user
adding a new address and receiving a verification email; a user in single-email mode changing their
address and seeing the pending-change state; and a user resending verification to a pending address.

---

## Spec 007 — Allauth Password Management Pages

Managing passwords for authenticated users involves two similar but contextually distinct pages:
changing an existing password (when the user already has one) and setting an initial password (for
accounts created via social login that have never had a password). Both pages sit inside the
authenticated account area and use the manage-password shell (`base_manage_password.html`). This
spec is responsible for modernising both templates using Cotton components.

`account/password_change.html` renders at `account_change_password` and presents a three-field
form (current password, new password, new password confirmation) along with a "Forgot Password?"
fallback link for users who cannot recall their current password. It must be rebuilt using `<c-form>`
and `<c-button>`, keeping the forgot-password link accessible and clearly separated from the submit
action.

`account/password_set.html` renders at `account_set_password` and is shown to social-account users
who have no existing password and wish to add one. It presents a simpler two-field form (new
password + confirmation) without a current-password field and without a forgot-password link.
The distinction between "change" and "set" must be visually clear; both pages use the same
underlying base template and should share a consistent layout.

Key scenarios include: an authenticated user navigating to the change-password page and successfully
updating their credentials; a user who cannot remember their current password following the
forgot-password link; a social-login user who has never set a password seeing the set-password page
rather than the change-password page; and validation error states (mismatched passwords, incorrect
current password) rendering inline field errors without losing entered values.

---

## Spec 008 — Allauth Social Account Connections

Users who authenticate via OAuth social providers need a management page to view, connect, and
disconnect their linked third-party accounts. Additionally, when an OAuth flow fails (provider error,
user denial, misconfiguration), allauth renders a dedicated error page. This spec is responsible for
modernising both social account management templates using Cotton components and the manage-page shell.

`socialaccount/connections.html` renders at `socialaccount_connections` and presents the list of
connected social accounts as radio-button options alongside a "Remove" action button, plus — when
additional providers are available — a section with buttons to connect new accounts. The current
template uses `{% element %}` extensively and must be rebuilt with `<c-form>`, `<c-button>`, and
provider badge or avatar components that are consistent with the provider-list snippets used on the
login and signup pages. The template must react correctly to the `SOCIALACCOUNT_ONLY` setting: when
only social authentication is permitted, the "disconnect" affordance must be disabled or hidden to
prevent users from locking themselves out.

`socialaccount/authentication_error.html` is the error page shown when a third-party OAuth flow
fails. It is an entrance-style page (the user is not yet authenticated) and must use the
`<c-entrance>` shell. The page content is a brief explanatory message with no form, similar in
structure to `account/account_inactive.html`.

Key scenarios include: an authenticated user viewing their connected providers; a user disconnecting
a social account when they still have a password fallback; a user attempting to disconnect their
only connected account when `SOCIALACCOUNT_ONLY = True` (the disconnect affordance must be
disabled); a user connecting a new social provider from the connections page; and a user being
redirected to the authentication-error page after a failed OAuth handshake.

---

## Spec 009 — Allauth MFA Authentication and Reauthentication Pages

When a user has multi-factor authentication enabled, allauth intercepts the standard login flow and
inserts an additional verification step. Depending on which MFA methods are active (TOTP, recovery
code, or WebAuthn), the user is presented with a code-entry form before gaining access. A similar
gate appears during reauthentication for sensitive actions. When the developer enables the "trust
this browser" feature, a third prompt asks the user whether to suppress future MFA challenges on the
current device. All three pages are entrance-style (they appear mid-login, before the authenticated
application shell is available) and must use the `<c-entrance>` shell. This spec is responsible for
modernising these three templates.

`mfa/authenticate.html` is the primary MFA challenge shown after credentials are validated but
before the session is established. It renders a code-entry form and, when `"webauthn"` is in
`MFA_SUPPORTED_TYPES`, includes a section for alternative WebAuthn authentication options and a
cancel/logout link. `mfa/reauthenticate.html` is the MFA variant of the reauthentication challenge
(parallel to `account/reauthenticate.html`) and renders an authenticator-code form in place of
the password field. `mfa/trust.html` renders the "Trust this Browser?" prompt, which carries a
trust-period selector and two primary actions ("Trust" and "Don't Trust") with a cancel/sign-out
fallback; the trust duration displayed (`trust_until|timeuntil:trust_from`) must be formatted
clearly for users.

Key scenarios include: a user with TOTP enabled being intercepted after login and entering a
six-digit code; a user entering a recovery code on the same page when they do not have their
authenticator device; a user with WebAuthn seeing the hardware-key prompt and an alternative
code-entry fallback; a user choosing to trust their browser and not being challenged again on that
device; and a user cancelling MFA and being signed out cleanly.

---

## Spec 010 — Allauth MFA Management Dashboard

The MFA index page is the central control panel for all multi-factor authentication methods configured
on a user's account. It presents the status of each supported MFA type (TOTP authenticator app,
recovery codes, WebAuthn security keys) and provides links to activate, deactivate, or manage each
method. This spec is responsible for modernising `mfa/index.html` using Cotton components and the
manage-page shell, replacing the `{% element panel %}` constructs with an appropriate card or panel
Cotton component.

The page must react correctly to `MFA_SUPPORTED_TYPES`: if `"totp"` is in the list, an
authenticator-app panel is shown; if `"recovery_codes"` is in the list, a recovery-code panel is
shown; if `"webauthn"` is in the list, a security-keys panel is shown. Each panel displays the
current activation state and an activate or deactivate action button. The layout must degrade
gracefully if fewer than three methods are supported, producing a clean single- or two-panel view
rather than orphaned empty sections.

Key scenarios include: a user who has no MFA methods active seeing all available panels with
"Activate" calls to action; a user with TOTP already active seeing the "Deactivate" button and the
remaining usage count of recovery codes; a user with only WebAuthn configured on a deployment
where TOTP is disabled, seeing only the WebAuthn panel; and a developer who has `MFA_SUPPORTED_TYPES
= ["totp"]` seeing no recovery-code or WebAuthn panels.

---

## Spec 011 — Allauth TOTP Authenticator App Setup

TOTP (Time-based One-Time Password) is the most widely used MFA method and is the first MFA type
most users will encounter in an allauth deployment. The setup flow is two pages: one to scan the QR
code and enter a verification code (activation), and one to confirm deactivation. Both pages extend
`mfa/totp/base.html` and sit within the authenticated account manage shell. This spec is responsible
for modernising both TOTP templates using Cotton components.

`mfa/totp/activate_form.html` is the most complex of the two. It presents a QR code image (rendered
as an SVG data URI), a read-only secret field for users who prefer to enter the key manually rather
than scan, and a verification-code input. All three elements must be laid out clearly, with the QR
code and secret presented as setup aids and the code input as the primary form action. The QR code
image must be rendered accessibly (respecting the `alt` attribute from the form field) and the
secret field must be selectable/copyable. `mfa/totp/deactivate_form.html` is a simple confirmation
form asking the user to confirm they want to remove their authenticator app; it must warn the user
clearly if deactivating TOTP will leave them without any remaining MFA method.

Key scenarios include: a user scanning the QR code and entering a valid TOTP code to activate;
a user who cannot scan the QR code manually entering the secret into their authenticator app; a user
entering an invalid or expired TOTP code during activation and seeing a clear inline error; a user
successfully activating TOTP and being redirected to the MFA management dashboard; and a user
deactivating TOTP and being warned that this reduces their account security.

---

## Spec 012 — Allauth MFA Recovery Codes

Recovery codes are the backstop that allows a user to regain access to their account when their
primary MFA device is unavailable. Django-allauth provides two management pages for recovery codes:
a viewing/download page and a code-regeneration confirmation page. Both extend
`mfa/recovery_codes/base.html` and sit within the authenticated account manage shell. This spec is
responsible for modernising both templates using Cotton components.

`mfa/recovery_codes/index.html` shows the count of remaining unused codes out of the total, and —
depending on which permissions allauth grants via `can_view_codes`, `can_download_codes`, and
`can_generate_codes` — optionally renders a read-only textarea of unused codes, a download button,
and a link to regenerate all codes. The layout must make the security implications of these actions
clear: viewing and downloading codes is safe, but regenerating codes invalidates all previous ones.
`mfa/recovery_codes/generate.html` is the regeneration confirmation form; it must clearly warn the
user that proceeding will invalidate all existing recovery codes and is destructive.

Key scenarios include: a user with several unused codes seeing the count and downloading their codes
for safe storage; a user who has used most of their codes being prompted to regenerate; a user who
confirms regeneration seeing a fresh set of codes immediately; a developer who has disabled code
viewing (`can_view_codes = False`) seeing only the count and the download/generate actions; and a
user who has no recovery codes at all (because they have not yet generated any) being directed to
generate their first set.

---

## Spec 013 — Allauth WebAuthn / Security Keys Management

WebAuthn (also known as passkeys or FIDO2 security keys) is the most advanced MFA method supported
by django-allauth. The WebAuthn management interface allows users to register new security keys,
edit their names, delete keys, and complete a WebAuthn-specific reauthentication challenge. Because
WebAuthn relies on JavaScript Web APIs, these pages carry embedded JS data scripts and client-side
event handling that must be preserved exactly when templates are modernised. This spec is responsible
for modernising all WebAuthn management templates using Cotton components while leaving the JS
plumbing intact.

The scope covers five templates. `mfa/webauthn/authenticator_list.html` is the overview page that
lists all registered security keys in a table with edit and delete affordances, plus an "Add Security
Key" button. `mfa/webauthn/add_form.html` is the registration form that triggers the browser's
WebAuthn credential-creation API on button click; it includes the `json_script` data island and a
`data-allauth-onload` script reference. `mfa/webauthn/edit_form.html` is a simple name-change form
for an existing authenticator. `mfa/webauthn/reauthenticate.html` is the WebAuthn-specific
reauthentication prompt, parallel to `account/reauthenticate.html` but triggering the browser's
credential-get API. `mfa/webauthn/signup_form.html` is the passkey signup form shown mid-registration
when `MFA_PASSKEY_SIGNUP_ENABLED = True`, requiring the same JS infrastructure as the add form.

Key scenarios include: a user registering a hardware security key by tapping it when prompted by
the browser; a user naming or renaming an authenticator for easy identification; a user deleting a
security key they no longer own; a user completing a WebAuthn reauthentication challenge for a
sensitive action; and a new user registering via passkey during the signup flow.

---

## Spec 014 — Allauth Phone Number Management

Phone number management is an optional django-allauth feature gated behind
`ACCOUNT_SIGNUP_FIELDS` including `"phone"` and the presence of an SMS backend. When enabled, users
can add, change, and verify their phone number through two templates. Because phone support is a
less common deployment choice, this spec is lower priority than the core account and MFA flows, but
must still be completed to achieve full template coverage for all allauth-supported features.

`account/phone_change.html` is the manage-style page for editing a user's phone number. It renders
the current phone number (read-only, with a "Re-send Verification" button if it is unverified and
a pending-status indicator), plus a form field for entering a new phone number. The layout is very
similar to `account/email_change.html` and should share the same Cotton component patterns for
consistency. `account/confirm_phone_verification_code.html` extends `account/base_confirm_code.html`
and is the code-entry page shown after a verification SMS is sent; like `confirm_email_verification_code.html`,
it delegates most rendering to the base template and requires only block-level customisation
(title, recipient display, action URL, and extra tags).

Key scenarios include: a user with no phone number on file seeing the add-phone form; a user who
has a verified phone number seeing it displayed read-only before the change form; a user who has a
pending (unverified) phone number being offered a re-send button; a user who adds a phone number
and is redirected to the code-entry page; and a user who enters an invalid or expired code and
sees a clear inline error before retrying.

---

## Spec 015 — Allauth User Sessions Management

The user sessions feature (`allauth.usersessions`) gives authenticated users visibility into all
active login sessions on their account — showing IP addresses, browser details, and timestamps —
and allows them to terminate sessions they do not recognise. This is a valuable security feature
for power users and privacy-conscious deployments. This spec is responsible for modernising
`usersessions/usersession_list.html` using Cotton components and the manage-page shell.

The template renders a table of active sessions with columns for start time, IP address, user-agent
or browser details, and a "currently active" indicator for the session in use. It also provides an
action button that signs the user out of all other sessions (preserving the current one) or — if
there is only one session — redirects to the standard logout page. The table structure must be
rebuilt using whatever table or list Cotton component is available from the django-mvp component
library, falling back to a plain `<table>` with Bootstrap styling if a dedicated component does not
yet exist. Humanised timestamps (via `|naturaltime` or `|timesince`) must be preserved.

Key scenarios include: a user with a single active session seeing their current session clearly
indicated with no "sign out other sessions" option available; a user with multiple sessions across
devices seeing each session listed with its IP address and approximate start time; a user clicking
"Sign Out Other Sessions" and having all sessions except the current one terminated immediately;
and a developer who has not installed `allauth.usersessions` seeing no sessions management link
in the navigation (the page should not be reachable from the account menu if the app is not
installed).
