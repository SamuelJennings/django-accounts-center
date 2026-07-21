# Implementation Plan: MFA Management Templates

**Branch**: `011-mfa-management-templates` | **Date**: 2026-05-22 | **Spec**: [spec.md](spec.md)
**Propagated**: 2026-05-25 — Updated from spec.md refinement
**Input**: Feature specification from `specs/011-mfa-management-templates/spec.md`

## Summary

Rewrite nine MFA management template overrides in `dac/addons/allauth/templates/mfa/`
so they render inside the full DAC Account Center layout (sidebar, breadcrumbs, card-stack).
The root cause is identical to specs 006/007/009/010: `mfa/base_manage.html` extends
`allauth/layouts/manage.html` instead of `dac/base.html`. The single-line base fix
propagates the layout to all nine templates. The nine content templates then receive a full
Cotton rewrite, replacing all allauth `{% element %}` / `{% slot %}` / `{% endelement %}`
tags with `<c-card>`, `<c-form>`, `<c-button>`, `<c-badge>`, `<c-form.field>`,
and raw Bootstrap HTML where no component applies. WebAuthn JavaScript is preserved intact.

Integration tests and Playwright screenshot tests are written as part of this feature in
`tests/test_addons/test_allauth/test_mfa_management_view.py` and
`screenshots/test_mfa_management_screenshots.py`.

## Technical Context

<!--
  ACTION REQUIRED: Replace the content in this section with the technical details
  for the project. The structure here is presented in advisory capacity to guide
  the iteration process.
-->

**Language/Version**: Python ≥3.12, Django ≥5.0, <6.0
**Primary Dependencies**: django-allauth ≥64.0, django-cotton, django-mvp, django-cotton-bs5
**Storage**: N/A (template-only changes; no models, migrations, or settings changes)
**Testing**: pytest, pytest-django, pytest-playwright
**Target Platform**: Django web application (server-rendered templates)
**Project Type**: Reusable Django extension library
**Performance Goals**: Same as existing management-page templates
**Constraints**: Zero `{% element %}` / `{% endelement %}` / allauth-`{% slot %}` tags in modified files; `id="recovery_codes"` must be preserved (JS dependency); `id="mfa_webauthn_add"` must be preserved (JS dependency); WebAuthn JS blocks (`allauth.webauthn.forms.addForm`) preserved intact; Bootstrap `<table class="table mb-3">` inside `<c-card>` (no `<c-table>` component); `<c-form.field>` cannot render textarea with content (self-closing render — use raw HTML wrapper for recovery codes textarea); CSRF token explicit (`{% csrf_token %}`) in templates not using `:form-obj="form"`
**Scale/Scope**: 10 template files edited (1 base + 9 content); 1 new integration test file; 1 new screenshot test file; 22 PNGs (11 states × 2 viewports)

## Constitution Check

*Pre-design gate — all items PASS.*

| Principle | Gate | Status |
|---|---|---|
| I. Design-First | Template inheritance graph and component structure in `contracts/component-interface.md`; integration tests define acceptance criteria | ✅ PASS |
| II. Documentation-First | `quickstart.md` documents all ten files, block contracts, and test commands | ✅ PASS |
| III. Component Quality & Accessibility | No new components introduced; all components are validated existing ones | ✅ PASS |
| IV. Compatibility | Template overrides only; no view or settings changes | ✅ PASS |
| V. Tooling | `poetry run pytest`; djlint for templates | ✅ PASS |
| VI. UI Verification | playwright-cli skill is the first choice for all UI verification; screenshot file analysis is a token-expensive fallback only when interactive verification is insufficient; `.github/skills/playwright-cli/SKILL.md` MUST be consulted before any browser step (v1.1.5) | ✅ PASS |
| VII. Documentation Retrieval | No new external APIs — reusing established patterns from Specs 001–010 | ✅ PASS (N/A) |
| VIII. E2E Testing | Screenshot tests: 11 states × 2 viewports = 22 PNGs | ✅ PASS |
| IX. Component Reuse | No new components; `<c-badge>`, `<c-button>`, `<c-card>`, `<c-form>`, `<c-form.field>`, `<c-dropdown>`, `<c-dropdown.item>`, `<c-navigation.breadcrumbs.item>` are all existing; raw Bootstrap table used for WebAuthn list (Principle IX one-off exemption); raw HTML textarea used for recovery codes (self-closing limitation of `<c-form.field>`, one-off exemption) | ✅ PASS |
| X. Third-Party Integration | Template overrides primary; no view overrides introduced | ✅ PASS |
| XI. Dual-Audience Stories | US1, US4 [Developer] + US2, US3 [End User] | ✅ PASS |
| XII. View Docstrings | No view classes introduced or modified | ✅ PASS (N/A) |
| XIII. Screenshot Coverage | 11 page states × 2 viewports = 22 PNGs (desktop + mobile); `screenshots/` dir; `pytest screenshots/` | ✅ PASS |

**No violations. No complexity justification required.**

*Post-design re-check: same result — no new Python, no new components, no new views.*

## Project Structure

### Documentation (this feature)

```text
specs/011-mfa-management-templates/
├── plan.md              ← this file
├── research.md          ← Phase 0 output
├── data-model.md        ← Phase 1 output
├── quickstart.md        ← Phase 1 output
├── contracts/
│   └── component-interface.md   ← Phase 1 output
├── checklists/
│   └── requirements.md
└── tasks.md             ← generated by /speckit.tasks (NOT by /speckit.plan)
```

### Source Code (affected files)

```text
dac/addons/allauth/templates/mfa/
├── base_manage.html                    ← EDIT: extends line only (allauth/layouts/manage.html → dac/base.html)
├── index.html                          ← FULL REWRITE (block page.content; 3 × <c-card> panels)
├── totp/
│   ├── activate_form.html              ← FULL REWRITE (<c-form>; QR code + secret + form fields)
│   └── deactivate_form.html            ← FULL REWRITE (<c-form>; danger submit)
├── recovery_codes/
│   ├── index.html                      ← FULL REWRITE (raw textarea; Download/Generate buttons below)
│   └── generate.html                   ← FULL REWRITE (<c-form>; conditional danger submit)
└── webauthn/
    ├── authenticator_list.html         ← FULL REWRITE (<c-card> + Bootstrap table; <c-badge> types; <c-dropdown> for edit/remove actions)
    ├── add_form.html                   ← REWRITE (preserve JS block exactly; id="mfa_webauthn_add")
    ├── edit_form.html                  ← REWRITE (<c-form> or block page.content)
    └── authenticator_confirm_delete.html  ← REWRITE (<c-form> or block page.content; danger submit)

tests/test_addons/test_allauth/
└── test_mfa_management_view.py         ← NEW: integration tests (all US1–US4 acceptance scenarios)

screenshots/
└── test_mfa_management_screenshots.py  ← NEW: screenshot tests (11 states × 2 viewports = 22 PNGs)

docs/_static/
├── desktop/                            (11 new PNGs)
└── mobile/                             (11 new PNGs)
```

**Structure Decision**: Changes are primarily confined to the existing `dac/addons/allauth/`
addon. No new Python files required. Tests and screenshot files follow the established
pattern from Specs 006–010.
