# Implementation Plan: Account Center menu entries that appear only for the people they apply to

**Branch**: `013-account-center-menu` | **Date**: 2026-07-31 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/013-account-center-menu/spec.md`

## Summary

Most of this feature already works, in a dependency. django-flex-menus takes a `check` predicate
on every `MenuItem`, evaluates it per request in `MenuItem.process()`, drops failing items from the
processed tree, hides a container left with no visible children, and renders only what survives.
That is FR-001 through FR-005 and FR-007, available today and unused by this package.

So the work is not building a visibility mechanism. It is three things:

1. **Removing the one place the package breaks its own promise.** `get_active_section()` resolves
   the breadcrumb from the *processed* menu, keeping leaves where `visible` is true. Hide someone's
   entry and the section their breadcrumb resolves against disappears with it, so a person reaching
   that page by a direct link gets no section crumb and a generic label on the mobile dropdown.
   Hiding is meant to be presentation-only. This is the feature's only real code change.
2. **Proving the contract, once, at the level this package owns.** A test integration that is not
   `dac.allauth` contributes gated entries and serves a management page through `dac/base.html`.
   This gives the suite a second party — the thing a single-integration suite cannot express — and
   covers FR-008 at the same time.
3. **Making the written record true.** ADR 0002 says "not yet implemented" and cites the wrong
   roadmap item. CONTEXT.md and the integration prose describe visibility as decided but not built.
   FR-009 to FR-011.

**What this plan deliberately does not do:** add a dac-level API over `check`. An integration passes
`check=` to the `MenuItem` it already constructs. A wrapper would be a second name for a working
thing (Articles II and III), and Article XV prefers documented extension points to new Python
surface. The visibility check *is* flex-menus' `check`, documented as this package's contract.

## Technical Context

**Language/Version**: Python ≥ 3.12, Django ≥ 5

**Primary Dependencies**: django-flex-menus (`check` predicate, `process()`), django-mvp
(`MenuGroup`, app shell), allauth (existing integration)

**Storage**: N/A — no models, no migrations

**Testing**: pytest + pytest-django; markup assertions per Article XII

**Target Platform**: reusable Django package

**Project Type**: single package (`dac/`) with integration sub-apps

**Performance Goals**: no regression in Account Center page render. The per-request cost was
accepted in ADR 0002 and this feature does not change its shape.

**Constraints**: no new public Python API; no change to `dac.allauth`'s rendered output; no
migrations

**Scale/Scope**: one core function changed, one test integration added, three documents corrected

## Constitution Check

| Article | Bearing on this feature | Verdict |
|---|---|---|
| I — Test-First | Every task below writes its failing test first. The breadcrumb fix has a test that fails against current `main`. | Pass |
| II — Simplicity | No new abstraction: the contract is the dependency's existing `check` argument. | Pass |
| III — Anti-Abstraction | Explicitly rejected a dac-level wrapper over `check`. | Pass |
| IV — Integration-First | The test integration is the integration-level proof, not a unit mock. | Pass |
| VI — Documentation | ADR 0002, CONTEXT.md and integration prose land in this PR with the behaviour. | Pass |
| VIII — i18n | No new user-facing strings in the package. The test integration's labels use `gettext_lazy` to model correct practice. | Pass |
| XI — Third-party integration strategy | Uses flex-menus' public `check` argument. No monkey-patching, no private API, no fork. | Pass |
| XII — Rendered-markup contracts | Visibility assertions are made against rendered menu markup, not internal state. | Pass |
| XIII — UI verification | Menu and breadcrumb changes confirmed in a browser against US-2 before commit. | Pass |
| XIV — Dual-audience specs | Spec carries `[Developer]` and `[End User]` stories. | Pass |
| XV — Compatibility | An entry with no check keeps today's behaviour. No breaking change. | Pass |
| XVII — Composition | No custom CSS. The menu renders through existing components. | Pass |

**Test-duplication rule (Sam, 2026-07-31):** flex-menus' own behaviour is flex-menus' to test. This
package does not assert that `check` is evaluated, that a failing check hides an item, or that an
empty container hides itself. It asserts what *this package* contributes: that a dac menu entry
carrying a check renders per-person, that the breadcrumb survives a hidden entry, and that a second
integration can serve a page. The line: if the assertion would still hold with `dac` uninstalled,
it belongs upstream.

## Project Structure

### Documentation (this feature)

```
specs/013-account-center-menu/
├── spec.md
├── plan.md
├── research.md
├── tasks.md
├── decisions.md
├── progress.md
├── feature-state.json
└── checklists/requirements.md
```

### Source Code (repository root)

```
dac/
├── menus.py                     # get_active_section() — the breadcrumb fix
└── allauth/menus.py             # unchanged; entries carry no check

docs/
├── adr/0002-account-center-visibility-is-per-request.md   # status, roadmap ref, state
└── index.md                     # integration-facing contract prose

CONTEXT.md                       # "Visibility check" glossary entry

tests/
├── test_menus.py                # per-person rendering + breadcrumb survival
├── test_integration_contract.py # the second integration serving a page
└── testapp/                     # the test integration (menus, view, template, urls)
```

**Structure Decision**: single package, existing layout. The test integration lives under `tests/`
rather than shipping as `dac/<package>/` — it exists to prove the contract, not to be installed by
anyone. Its URLs mount through `tests/urls.py`, because contributing URLs without a core edit is
roadmap R4 and out of scope (spec assumption, D8).

## Complexity Tracking

No constitutional deviations to justify. The one judgement worth recording is the *absence* of
work: this feature ships no visibility API because the dependency already provides one, and the
plan's honest size is small. Inflating it with a wrapper would be the deviation.
