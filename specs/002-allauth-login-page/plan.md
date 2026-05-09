# Implementation Plan: Allauth Login Page

**Branch**: `002-allauth-login-page` | **Date**: 2026-05-08 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `specs/002-allauth-login-page/spec.md`

## Summary

Build a styled, modern allauth login page for django-accounts-center by rewriting three existing placeholder template overrides (`account/login.html`, `account/request_login_code.html`, `account/confirm_login_code.html`) to use Cotton components instead of allauth's `{% element %}` syntax. `confirm_login_code.html` extends `account/base_entrance.html` directly, bypassing `account/base_confirm_code.html` (which is shared with other confirmation flows and remains out of scope).

The `<c-entrance>` shell — centred card, logo, background, and visual framework — is **already implemented** from spec 001 and requires no changes. All entrance-page templates inherit it automatically via the existing template chain. This spec's work is entirely at the page-content level: replacing `{% element %}` calls inside `{% block content %}` with the appropriate Cotton components (`<c-form>`, `<c-form.crispy>`, `<c-button.stack>`, `<c-button>`, `<c-card.divider>`, `<c-entrance.text>`).

Social provider rendering is also already Cotton-based (spec 001) via `socialaccount/snippets/provider_list.html`. The login page reuses it with `process="login"`.

No new Python views, models, forms, or migrations are introduced. No new Cotton components are created.

## Technical Context

**Language/Version**: Python 3.12+
**Primary Dependencies**: Django 5.2+, django-allauth v65+, django-mvp ≥0.1.1, django-cotton, django-cotton-bs5, crispy-bootstrap5
**Storage**: N/A — no database changes
**Testing**: pytest, pytest-django, pytest-playwright
**Target Platform**: Django web application (server-rendered HTML)
**Project Type**: Reusable Django extension library
**Performance Goals**: No additional database queries vs. allauth baseline
**Constraints**: Must not monkey-patch allauth. Must degrade gracefully without `allauth.socialaccount`. All UI changes via template overrides only.
**Scale/Scope**: 3 template files fully rewritten + 1 template restructured to bypass `base_confirm_code.html`

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Pre-design check** (before Phase 0):

| Principle | Status | Notes |
|---|---|---|
| I. Simplicity First | ✅ PASS | Pure template overrides. No new Python code, models, or views. |
| II. django-mvp First | ✅ PASS | Primary shell uses `mvp/base.html` via the existing `allauth/layouts/base.html` override. |
| III. Cotton Component Composition | ✅ PASS | All UI composed from Cotton components. No raw Bootstrap classes in page templates (dividers, forms, buttons all go through Cotton). |
| IV. No Duplication | ✅ PASS | `<c-entrance>` reused unchanged. `provider_list.html` snippet reused with `process="login"`. |
| V. Addon Isolation | ✅ PASS | All template overrides remain within `dac/addons/allauth/templates/`. |
| VI. No Monkey-Patching | ✅ PASS | No Python view or adapter overrides. Template-only. |
| VII. Graceful Degradation | ✅ PASS | `{% if SOCIALACCOUNT_ENABLED %}`, `{% if PASSKEY_LOGIN_ENABLED %}`, `{% if LOGIN_BY_CODE_ENABLED %}` guards throughout. |
| VIII. i18n Throughout | ✅ PASS | All user-visible strings wrapped in `{% trans %}` or `{% blocktrans %}`. |
| IX. Component Priority | ✅ PASS | django-mvp components first (`<c-form>`, `<c-card.divider>`, `<c-button.stack>`), cotton-bs5 second (`<c-button>`). No new DAC-owned components needed. |
| X. Template Overrides Primary | ✅ PASS | Entire feature is template overrides. |
| XI. Test Coverage | ✅ PASS | Integration tests cover all rendering paths; screenshot tests cover all permutations × 3 viewports. |
| XII. Documentation | ✅ PASS | `quickstart.md` covers setup, configuration, and customisation. |
| XIII. Multi-Viewport Screenshot Coverage | ✅ PASS | FR-012 mandates 7 permutations × 3 viewports = 21 files. Screenshot tests in `screenshots/test_login_screenshots.py`, written to `docs/_static/{desktop,tablet,mobile}/`. |

**Post-design re-check** (after Phase 1 artifacts):

| Check | Status | Notes |
|---|---|---|
| No new DAC-owned Cotton components | ✅ PASS | All UI from spec 001's entrance family + django-mvp + cotton-bs5. |
| Template overrides isolated inside addon | ✅ PASS | All files under `dac/addons/allauth/templates/`. |
| Social provider loading guarded | ✅ PASS | `{% load socialaccount %}` only inside `provider_list.html` (unchanged from spec 001). |
| `<c-form.crispy form=verify_form />` used on confirm page | ✅ PASS | Contracts document the `verify_form` binding explicitly. |
| `base_confirm_code.html` not modified | ✅ PASS | `confirm_login_code.html` bypasses it by extending `base_entrance.html` directly. |

## Project Structure

### Documentation (this feature)

```text
specs/002-allauth-login-page/
├── plan.md              # This file
├── research.md          # Phase 0 output — unknowns resolved
├── data-model.md        # Phase 1 output — runtime entities
├── quickstart.md        # Phase 1 output — developer guide
├── contracts/
│   ├── template-context.md     # Phase 1 — context variable contracts (3 templates)
│   └── component-interface.md  # Phase 1 — Cotton component usage and dependency graph
└── tasks.md             # Phase 2 output (/speckit.tasks — NOT created here)
```

### Source Code (repository root)

```text
dac/
└── addons/
    └── allauth/
        └── templates/
            ├── account/
            │   ├── login.html                   # REWRITE: Cotton (social top, form below, passkey/code, signup link)
            │   ├── request_login_code.html       # REWRITE: Cotton (description, form, back-to-login link)
            │   └── confirm_login_code.html       # RESTRUCTURE: extend base_entrance.html directly (bypass base_confirm_code.html)
            └── (all other templates unchanged — already Cotton or out of scope)

screenshots/
└── test_login_screenshots.py                    # 7 permutations × 3 viewports = 21 files

docs/_static/
├── desktop/                                     # 1440×900 screenshots (auto-generated)
├── tablet/                                      # 768×1024 screenshots (auto-generated)
└── mobile/                                      # 390×844 screenshots (auto-generated)

tests/
└── test_addons/
    └── test_allauth/
        └── test_login_view.py                   # Integration tests for all login-flow templates
```

**Structure Decision**: All source changes are restricted to `dac/addons/allauth/templates/account/`. Three template files are touched; no Python, no new Cotton components, no new CSS. Screenshot tests go in `screenshots/` (per Principle XIII) and integration tests mirror the source tree under `tests/test_addons/test_allauth/`.

## Complexity Tracking

No constitution violations. No complexity justification required.
