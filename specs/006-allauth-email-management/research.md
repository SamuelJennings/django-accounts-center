# Research: Allauth Email Management Templates

**Feature**: 006-allauth-email-management
**Status**: N/A — no unknowns requiring research

## Summary

All implementation patterns required for this feature are established in prior specs
(001–005). No new external APIs, libraries, or component patterns are introduced.

## Decisions

### Decision 1: Template inheritance fix strategy

**Decision**: Change only `base_manage.html` extends line; leave `base_manage_email.html` untouched.
**Rationale**: The single-point fix propagates the DAC layout to all descendants without requiring changes to intermediate base files. Minimises diff surface area per Principle V (keep changes minimal and focused).
**Alternatives considered**: Flatten all descendants to extend `dac/base.html` directly — rejected because it removes the useful email-specific base abstraction and creates unnecessary divergence from allauth's own template hierarchy.

### Decision 2: `email_change.html` form wrapper component

**Decision**: Use `<c-form.card>` (not nested `<c-form>` + `<c-card>`).
**Rationale**: `<c-form.card>` is the established management-page form wrapper (used in `password_change.html`, established in Spec 003). Consistency across management pages. Nested alternative is only acceptable when `<c-form.card>` lacks required functionality.
**Alternatives considered**: `<c-form>` + `<c-card>` — rejected per spec clarification (Q4).

### Decision 3: `verified_email_required.html` content wrapper

**Decision**: Wrap explanatory paragraphs in an explicit `<c-card>` inside `{% block page.content %}`.
**Rationale**: Consistent with all other DAC management pages that place content inside a card surface. The `card.stack` from `dac/base.html` provides vertical spacing; the `<c-card>` provides the visual surface (background, border, padding).
**Alternatives considered**: Bare paragraphs directly in `page.content` — rejected per spec clarification (Q2).

### Decision 4: `email.html` correction scope

**Decision**: Corrections-only. Fix only functional errors in the management flow (broken form `action` URLs, incorrect button `name` attributes, content outside `{% block page.content %}`).
**Rationale**: The template is already substantially Cotton. Cosmetic or structural refactoring would violate Principle V (keep changes minimal) without delivering user value.
**Alternatives considered**: Full rewrite — rejected per spec clarification (Q3).

## Prior Art (Established Patterns)

| Pattern | Established in |
|---|---|
| `{% extends "dac/base.html" %}` chain fix | Spec 004 (`account_inactive.html`) |
| `<c-form.card>` as management-page form wrapper | Spec 003 (`password_change.html`) |
| `{% block page.content %}` override | Spec 005 (`dac/base.html` contract) |
| `<c-card>` wrapper for informational content | Spec 004 (`email_confirm.html` invalid branch) |
| Pre-written integration test + screenshot test pattern | Spec 005 |
| `account_email_change_test` test URL | `tests/urls.py` (pre-existing) |
| `account_verified_email_required` test URL | `tests/urls.py` (pre-existing) |
