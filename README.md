# Django Accounts Center

A complete, polished account-management UI for [django-allauth](https://docs.allauth.org/),
built on the [django-mvp](https://github.com/SamuelJennings/django-mvp) app shell
(DaisyUI 5 + Tailwind CSS v4 + django-cotton).

## How it works

dac does **not** fork allauth's page templates. Instead it overrides allauth's
three **layouts** and its ~22 **element** templates:

- `allauth/layouts/entrance.html` — login, signup, password reset, sign-in
  codes, … render as a centered card (no app shell) with your site logo.
- `allauth/layouts/manage.html` → `dac/base.html` — email, password, MFA,
  sessions and connected-accounts pages render inside the normal django-mvp
  shell with an "Account Center" sub menu beside the content.
- `allauth/elements/*.html` — every `{% element %}` (button, field, form,
  panel, alert, badge, provider button, table, …) maps to DaisyUI markup.

Because allauth's own stock page templates do the rendering, **every allauth
feature and configuration variation works automatically** — passkeys,
login-by-code, email verification by code, phone numbers, `SOCIALACCOUNT_ONLY`,
MFA (TOTP / WebAuthn / recovery codes / trust), user sessions — now and in
future allauth releases. dac adds on top:

- **Account Center overview page** (`account-center` URL): dashboard cards
  summarising email, password, 2FA, sessions and connected accounts.
- **Sidebar user menu integration**: django-mvp's `<c-user.sidebar-menu>`
  automatically shows an "Account Center" entry and a POST logout form once
  dac's URLs are installed.
- **`AccountCenterMenu`** (django-flex-menus): the internal sub menu, with
  items appearing only for the allauth apps you actually install.
- **`DAC_ICONS`** easy-icons pack and a prebuilt `dac.css` stylesheet.

Integrations are **gated sub-apps**: the core `dac` app ships the Account
Center shell (layout, overview page, menu), and each third-party integration
is opted into individually via `INSTALLED_APPS` — mirroring django-mvp's
guarded-integrations philosophy. Install only what you use:

```python
INSTALLED_APPS = ["dac", "dac.allauth", ...]   # future: "dac.stripe", …
```

Each integration contributes its own labelled menu group, overview cards
(via `dac_overview_template` / `dac_overview_context` hooks on its
`AppConfig`), URLs, and template overrides.

## Installation

```bash
pip install django-accounts-center[allauth]
```

### 1. Settings

```python
INSTALLED_APPS = [
    # ...
    "django.contrib.sites",
    "dac",
    "dac.allauth",              # BEFORE allauth so template overrides win
    "mvp",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",    # optional
    "allauth.mfa",              # optional
    "allauth.usersessions",     # optional
    "easy_icons",
    "flex_menu",
    "django_cotton",
    # ...
]

SITE_ID = 1

MIDDLEWARE = [
    # ...
    "allauth.account.middleware.AccountMiddleware",
]

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]

TEMPLATES = [{
    # ...
    "APP_DIRS": True,
    "OPTIONS": {"context_processors": [
        "django.template.context_processors.request",
        # ...
        "mvp.context_processors.mvp_config",
    ]},
}]

# django-mvp shell: show the user menu at the bottom of the sidebar.
MVP_CONFIG = {
    "layout": {
        "sidebar": {"footer": ["user.sidebar-menu"]},
    },
}

# Icons: mvp's Bootstrap Icons pack + dac's account icons.
EASY_ICONS = {
    "default": {
        "renderer": "easy_icons.renderers.ProviderRenderer",
        "config": {"tag": "i"},
        "packs": ["mvp.utils.BS5_ICONS", "dac.icons.DAC_ICONS"],
    },
}

FLEX_MENUS = {
    "renderers": {
        "sidebar": "mvp.renderers.SidebarRenderer",
        "dock": "mvp.renderers.MobileFooterNavRenderer",
    },
}

LOGIN_URL = "account_login"
LOGIN_REDIRECT_URL = "/accounts/"
```

### 2. URLs

dac's URLconf includes `allauth.urls` for you — mount it once:

```python
urlpatterns = [
    path("accounts/", include("dac.urls")),
    # ...
]
```

This registers the `account-center` overview page at `/accounts/` plus all of
allauth's URLs (`/accounts/login/`, `/accounts/email/`, `/accounts/2fa/`, …).

### 3. Migrate

```bash
python manage.py migrate
```

That's it. Anonymous users get centered entrance pages; authenticated users
reach the Account Center from the user menu at the bottom of the sidebar.

## Customisation

- **Re-skin everything**: override any `allauth/elements/*.html` template in
  your project — it applies across all allauth pages at once.
- **Page-level tweaks**: override individual allauth page templates the normal
  Django way (your project templates win over dac's and allauth's). Prefer
  element overrides — per-page forks are what this package exists to avoid.
- **Sub menu**: append items (or a labelled `mvp.menus.MenuGroup`) to
  `dac.menus.AccountCenterMenu` from your own `menus.py` (e.g. a profile-edit
  page). Items may declare `url_names` prefixes in `extra_context` so
  breadcrumbs resolve their sub-pages.
- **Overview page**: subclass `dac.views.AccountCenterView` and point the
  `account-center` URL at it, or override `dac/account_center.html`.
- **Social login icons**: `dac.allauth` ships brand SVGs for the major
  providers (Google, GitHub, Microsoft, Apple, Facebook, X, LinkedIn, GitLab,
  Discord, ORCID) in its `icons/` template dir; register them under a
  django-easy-icons `"svg"` renderer keyed by allauth provider id (see the
  example `EASY_ICONS` setting). `provider.html` renders them with
  `{% icon provider_id renderer="svg" %}`, so a provider without a registered
  icon raises `IconNotFound` (caught in development, not shipped broken), and
  any icon is overridable via your `EASY_ICONS` config or a template shadow.
- **Styling**: dac ships a prebuilt `dac.css` (Tailwind v4 + DaisyUI 5 over
  both mvp's and dac's templates). If your project runs its own Tailwind
  build, add dac's templates as a source alongside mvp's (see
  `assets/tailwind.css`) and override the `styles` block.

## Development

```bash
git clone https://github.com/SamuelJennings/django-accounts-center.git
cd django-accounts-center
poetry install
npm install

# run the example project
python manage.py runserver

# rebuild the shipped stylesheet after template changes
npm run build:css

# tests
pytest
```

The `example/` project exercises an aggressive allauth configuration
(passkeys, login-by-code, email verification by code, MFA, three social
providers) and `tests/` includes an architecture guard
(`tests/test_architecture.py`) that fails if anyone reintroduces per-page
allauth template forks.

## License

MIT
