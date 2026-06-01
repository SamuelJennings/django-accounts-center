# Implementation Plan: Allauth Password Reset Flow

**Branch**: `003-allauth-password-reset` | **Date**: 2026-05-11 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `specs/003-allauth-password-reset/spec.md`
**Propagated**: 2026-05-11 — Updated from spec.md refinement (FR-001, FR-002, FR-003, FR-005, FR-006, FR-010)

## Summary

Rewrite five existing `{% element %}`-based DAC template overrides to use Cotton components, matching the allauth-fidelity principle established in specs 001 and 002. The four standard templates (`password_reset.html`, `password_reset_done.html`, `password_reset_from_key.html`, `password_reset_from_key_done.html`) are full page-level rewrites extending `account/base_entrance.html`. The shared base template `account/base_confirm_code.html` is also fully rewritten to Cotton (replacing `{% element %}` throughout), benefiting all code-confirmation child templates. The child template `confirm_password_reset_code.html` requires only block-value updates, not structural changes.

No new Python views, models, forms, or migrations are introduced. No new Cotton components are created. All UI changes are via template overrides within `dac/addons/allauth/templates/account/`.

## Technical Context

**Language/Version**: Python 3.12+
**Primary Dependencies**: Django 5.2+, django-allauth v65+, django-mvp ≥0.1.1, django-cotton, django-cotton-bs5, crispy-bootstrap5
**Storage**: N/A — no database changes
**Testing**: pytest, pytest-django, pytest-playwright
**Target Platform**: Django web application (server-rendered HTML)
**Project Type**: Reusable Django extension library
**Performance Goals**: No additional database queries vs. allauth baseline
**Constraints**: Must not monkey-patch allauth. All UI changes via template overrides only. Zero `{% element %}` tags in any modified file after implementation.
**Scale/Scope**: 5 template files rewritten + 1 shared base rewritten = 6 files touched; 15 screenshots (5 states × 3 viewports)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Pre-design check** (before Phase 0):

| Principle | Status | Notes |
|---|---|---|
| I. Design-First, Verify Implementation | ✅ PASS | Pure template rewrites. Design-first via Playwright MCP verification; tests written after verification. |
| II. Documentation-First | ✅ PASS | `quickstart.md` documents all pages, optional code-based flow, and customisation. |
| III. Component Quality & Accessibility | ✅ PASS | All UI via Cotton components which produce valid, semantic HTML. |
| IV. Compatibility & Config-Driven Design | ✅ PASS | Template overrides only. No Python-level config changes. |
| V. Tooling & Consistency | ✅ PASS | All commands via Poetry. Ruff + djlint enforced. |
| VI. UI Verification (playwright-mcp) | ✅ PASS | Each UI-modifying task includes a Playwright MCP verification step. |
| VII. Documentation Retrieval (context7) | ✅ PASS | allauth context variable contracts validated against allauth source before design. |
| VIII. End-to-End Testing (pytest-playwright) | ✅ PASS | Screenshot tests for 5 page states × 3 viewports. Integration tests cover all branches. |
| IX. Template Component Reuse Discipline | ✅ PASS | django-mvp components first (`<c-form>`, `<c-group>`), cotton-bs5 second (`<c-button>`). No new DAC-owned components. |
| X. Third-Party Integration Strategy | ✅ PASS | Template overrides primary. No view overrides. All overrides within `dac/addons/allauth/`. |
| XI. Dual-Audience User Stories | ✅ PASS | Spec contains developer story (US5) and multiple end-user stories (US1–US4). |
| XII. View Class Docstring Completeness | ✅ PASS | No new view classes introduced. |
| XIII. Multi-Viewport Screenshot Coverage | ✅ PASS | 15 screenshots: 5 states × 3 viewports (desktop 1440×900, tablet 768×1024, mobile 390×844). |

**Post-design re-check** (after Phase 1 artifacts):

| Check | Status | Notes |
|---|---|---|
| No new DAC-owned Cotton components | ✅ PASS | All UI from spec 001's entrance family + django-mvp + cotton-bs5. |
| Template overrides isolated inside addon | ✅ PASS | All files under `dac/addons/allauth/templates/account/`. |
| `{% load socialaccount %}` absent | ✅ PASS | No social provider integration in password-reset flow. |
| `redirect_field` preserved in all forms | ✅ PASS | Contracts explicitly document `{{ redirect_field }}` placement. |
| Hidden forms (#resend, #logout-from-stage) preserved | ✅ PASS | Component interface contract documents exact HTML. |
| `base_confirm_code.html` rewritten (not just validated) | ✅ PASS | Research decision 3 confirms full rewrite in scope. |

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
dac/
└── addons/
    └── allauth/
        └── templates/
            └── account/
                ├── password_reset.html                  # FULL REWRITE
                ├── password_reset_done.html             # FULL REWRITE
                ├── password_reset_from_key.html         # FULL REWRITE
                ├── password_reset_from_key_done.html    # FULL REWRITE
                ├── base_confirm_code.html               # FULL REWRITE
                └── confirm_password_reset_code.html     # BLOCK VALUES ONLY

tests/
└── test_addons/
    └── test_allauth/
        └── test_password_reset_view.py   # integration tests (all branches)

screenshots/
└── test_password_reset_screenshots.py   # 15 screenshot tests (5 states × 3 viewports)

docs/_static/
├── desktop/    # 1440×900 — password-reset, password-reset-done, etc.
├── tablet/     # 768×1024
└── mobile/     # 390×844
```

**Structure Decision**: Pure template-override approach. All files under existing `dac/addons/allauth/templates/account/` — no new directories required. Screenshot tests isolated in `screenshots/` (excluded from default testpaths). Tablet viewport added (three-viewport coverage required by Principle XIII).

## Phase 0: Research

*See [research.md](research.md) for all 8 decisions.*

All NEEDS CLARIFICATION items resolved. Key outcomes:

1. Template chain identical to specs 001/002: `base_entrance.html → entrance.html → base.html → mvp/base.html`.
2. Six templates exist as DAC overrides but all use `{% element %}` syntax — all require rewriting.
3. `base_confirm_code.html` is in scope for a full rewrite (not just validation).
4. Context variables validated against allauth v65+ source — documented in `contracts/template-context.md`.
5. Cotton component mapping confirmed — documented in `contracts/component-interface.md`.
6. Cancel mechanism: hidden `<form id="logout-from-stage">` POSTing to `account_logout`, replicated exactly.
7. Contact-us paragraph included in `password_reset.html` (allauth-fidelity principle).
8. 15 screenshots (5 states × 3 viewports); naming convention and storage paths defined.

## Phase 1: Design Artifacts

| Artifact | Path | Status |
|---|---|---|
| Data model | [data-model.md](data-model.md) | ✅ Complete |
| Template context contracts | [contracts/template-context.md](contracts/template-context.md) | ✅ Complete |
| Component interface contracts | [contracts/component-interface.md](contracts/component-interface.md) | ✅ Complete |
| Developer quickstart | [quickstart.md](quickstart.md) | ✅ Complete |

## Complexity Tracking

No constitution violations. This section is intentionally blank.
