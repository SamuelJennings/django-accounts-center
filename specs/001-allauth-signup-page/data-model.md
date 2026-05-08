# Data Model: Allauth Signup Page

**Feature**: 001-allauth-signup-page  
**Phase**: 1 — Design  
**Date**: 2026-05-07

> **Note**: This feature is entirely template-driven. There are **no new Django models or database tables**. The entities described below are runtime objects whose structure and behaviour are defined by django-allauth and the project's settings — not by any code in `django-accounts-center`.

---

## Runtime Entities

### 1. `SignupForm`

**Source**: `allauth.account.forms.SignupForm` (or a custom class configured via `ACCOUNT_SIGNUP_FORM_CLASS`)

**Responsibility**: Holds and validates signup field data. Its field set is determined entirely by the active allauth configuration at startup.

| Configuration Setting | Effect on Form |
|---|---|
| `ACCOUNT_USERNAME_REQUIRED = True` | Adds `username` field |
| `ACCOUNT_EMAIL_REQUIRED = True` | Adds `email` field |
| `ACCOUNT_EMAIL_CONFIRMATION_REQUIRED = True` | Adds `email2` (confirm email) field |
| `ACCOUNT_SIGNUP_PASSWORD_ENTER_TWICE = True` | Adds `password2` (confirm password) field |
| `ACCOUNT_SIGNUP_FORM_CLASS = "myapp.forms.MySignupForm"` | Appends or replaces fields with custom form |

**Template access**: `{{ form }}` — rendered via `<c-form.crispy />` (which applies `{{ form|crispy }}`).

**Validation outcomes**:

- Per-field errors: `{{ field.errors }}` (rendered automatically by crispy-bootstrap5)
- Non-field errors: `{{ form.non_field_errors }}` (must be explicitly rendered, e.g., via `<c-alert>`)

---

### 2. `SocialProvider`

**Source**: `allauth.socialaccount.providers.base.Provider` subclasses registered via `SOCIALACCOUNT_PROVIDERS`

**Responsibility**: Represents a configured OAuth2/OpenID Connect identity provider. Each provider exposes a name and a login/signup URL.

| Attribute | Type | Description |
|---|---|---|
| `provider.name` | `str` | Human-readable display name (e.g., "Google", "GitHub") |
| `provider.id` | `str` | Machine-readable identifier (e.g., "google", "github") |
| `provider.get_brands()` | `list` | For OpenID providers — returns brand objects with `openid_url` |

**Template access**: Retrieved via `{% get_providers as socialaccount_providers %}` (from `{% load socialaccount %}`).

**Login/signup URL**: `{% provider_login_url provider process="signup" as href %}`.

**Guard**: The `{% load socialaccount %}` template tag must only be used in templates that are conditionally included when `SOCIALACCOUNT_ENABLED` is `True`. Placing it in a always-rendered template will cause a `TemplateSyntaxError` when `allauth.socialaccount` is absent.

---

### 3. `AllauthConfiguration`

**Source**: Django settings + `allauth.account.app_settings`

**Responsibility**: Represents the collection of allauth settings that control the signup page's visible fields and available actions. All of the relevant boolean flags are injected into template context by `get_entrance_context_data()`.

| Context Variable | Type | Default | Description |
|---|---|---|---|
| `SOCIALACCOUNT_ENABLED` | `bool` | `False` | `True` when `allauth.socialaccount` is in `INSTALLED_APPS` |
| `SOCIALACCOUNT_ONLY` | `bool` | `False` | `True` when password signup is disabled entirely |
| `PASSKEY_SIGNUP_ENABLED` | `bool` | `False` | `True` when MFA passkey signup is configured |
| `LOGIN_BY_CODE_ENABLED` | `bool` | `False` | `True` when email login codes are enabled |

**Signup availability**: Controlled via `get_adapter(request).is_open_for_signup(request)`. When `False`, allauth renders `account/signup_closed.html` — there is no template variable for this state; the template selection itself is the signal.

---

### 4. Template Component Hierarchy (Conceptual)

The signup page is composed of the following Cotton component tree at runtime:

```text
allauth/layouts/entrance.html
└── mvp/entrance.html
    └── mvp/base.html  (HTML shell: CSS, JS, fonts)
        └── [body.login-page]
            └── [.login-box container]
                ├── <c-messages>               # Django flash messages
                └── account/signup.html
                    └── <c-card>               # Outer card container
                        ├── [card-header]      # "Sign Up" heading + login link
                        ├── [social section]   # Above <c-form>, outside <form> element
                        │   ├── <c-button>     # One per social provider (conditional)
                        │   └── <c-card.divider>  # "or" separator (conditional)
                        ├── <c-form>           # <form> element (hidden if SOCIALACCOUNT_ONLY)
                        │   ├── <c-alert>      # Non-field errors (conditional)
                        │   ├── <c-form.crispy>  # Crispy-bootstrap5 field rendering
                        │   ├── [redirect_field] # Hidden input
                        │   └── <c-button>     # Submit button
                        ├── <c-card.divider>   # Passkey separator (conditional)
                        └── <c-button>         # Passkey signup link (conditional)
```

---

## State Transitions (Template Logic)

The signup template has the following conditional rendering logic:

```
signup.html rendering:
├── IF SOCIALACCOUNT_ENABLED AND socialaccount_providers:
│   ├── Render social provider buttons (one per provider)
│   └── IF NOT SOCIALACCOUNT_ONLY:
│       └── Render "or" divider (<c-card.divider text="or">)
├── IF NOT SOCIALACCOUNT_ONLY:
│   └── Render email/password form
├── IF PASSKEY_SIGNUP_ENABLED:
│   ├── Render passkey divider
│   └── Render passkey signup button
└── ALWAYS: Render "Already have an account?" link
```

`signup_closed.html` rendering (separate template, no conditional):

```
signup_closed.html:
└── <c-card>
    ├── [card-header] "Sign Up Closed"
    └── [card-body] "We are sorry, but the sign up is currently closed."
```
