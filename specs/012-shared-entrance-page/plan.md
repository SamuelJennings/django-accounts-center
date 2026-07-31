# Implementation Plan: A shared entrance page owned by the core package

**Branch**: `012-shared-entrance-page` | **Date**: 2026-07-31 | **Spec**: [spec.md](spec.md)

## Summary

The entrance page moves from `dac/allauth/templates/allauth/layouts/entrance.html` into the core
app as two files: a composition component that holds the card and the logo, and an extendable page
template that any app reaches with `{% extends %}`. The allauth layout keeps only its own block
mapping and delegates the rest. A layout declares a card width by overriding one block, which is
what stops a width choice from duplicating the chrome around it.

## Technical Context

**Language/Version**: Python ≥ 3.12, Django ≥ 5

**Primary Dependencies**: django-cotton (component layer), django-mvp (`c-entrance`, `mvp/base.html`),
django-allauth (the first consumer). No new dependency.

**Storage**: N/A — templates only, no models and no migrations.

**Testing**: pytest with the existing `cotton_render_string_soup` fixture in
`tests/test_components/conftest.py`, which renders a template string to BeautifulSoup with a
request that carries `request.site`. That fixture is the whole harness this feature needs.

**Target Platform**: any Django project installing this package.

**Project Type**: reusable Django app (single package).

**Scale/Scope**: four template files, one glossary entry, one documentation section, one
stylesheet rebuild. No Python module gains a line.

## Design decisions taken at plan time

Each was tested against the real template stack before being written down. The probes are recorded
here rather than kept as code.

### P1 — The extension point is a template, reached by `{% extends %}`

allauth's stock entrance pages extend `allauth/layouts/entrance.html` and fill `{% block content %}`.
Under the elements-first rule (ADR 0001) those pages are never forked, so whatever the shared page
is, it has to be reachable through an unbroken `{% extends %}` chain that ends in a `content` block.
That rules out an include-based or purely component-based contract for the page itself.

### P2 — Width is declared by overriding a block, not by a variable

Four mechanisms were considered. Two were eliminated by experiment:

| Mechanism | Result |
|---|---|
| `{% block %}` inside a cotton attribute (`small="{% block w %}{% endblock %}"`) | **Fails silently.** Cotton binds the attribute without applying the child's block override, so every page renders at the default and nothing reports an error. |
| Context variable set by the view | **Fails for allauth.** allauth owns those views, so setting context would require a view override — Article XI permits that only where a template override cannot reach, and one can. |
| Custom tag writing to `render_context` from a block | Works, but adds machinery to do what a block override already does. Rejected on Articles II and III. |
| **Block override around the component** | **Works, verified three levels deep.** |

The verified chain: `dac/entrance.html` holds `{% block entrance %}` containing
`<c-dac.entrance>` wrapping `{% block content %}`. A layout that wants a different width overrides
`{% block entrance %}` and passes a different `size`. A stock page three levels down still fills
`{% block content %}`, and the width the layout chose still applies. Probed with a stand-in
component and both branches rendered the expected card class.

### P3 — The wrapper component is what makes P2 legitimate under Article XVII

Article XVII forbids authoring components here. `c-dac.entrance` is admissible because it is the
mechanism that prevents duplication rather than a piece of design: it introduces no class name of
its own, ships no stylesheet rule, and delegates every visual decision to mvp's `c-entrance`. Without
it, a layout overriding `{% block entrance %}` to change the width would have to restate the card
and the logo, which is exactly what FR-003 and SC-005 forbid. Reviewers applying the article's own
test — where did this class come from — will find only mvp's.

### P4 — `size`, not `small`

The component exposes `size`, defaulting to the current width. Today it accepts two values because
mvp's `c-entrance` expresses two: `sm` maps to mvp's `small`, and `full` leaves it unset. Mirroring
mvp's boolean directly would mean every consumer that wanted a width had to change its call when the
wider scale lands (#20). A named attribute absorbs that change inside the component instead.

### P5 — What lives where

| File | Holds |
|---|---|
| `dac/templates/cotton/dac/entrance.html` | `<c-entrance>` with the `size` mapping, the site logo, the slot |
| `dac/templates/dac/entrance.html` | extends `mvp/base.html`, the stylesheet link, the messages region, `{% block entrance %}` → `{% block content %}` |
| `dac/allauth/templates/allauth/layouts/entrance.html` | `{% extends "dac/entrance.html" %}` and the allauth block mapping (`head_title`, `extra_head`, `extra_body`) only |

The messages region sits in the page template outside `{% block entrance %}`, so a layout that
overrides the block to change its width does not silently lose messages.

The allauth block names stay in the allauth layout. `dac/base.html` currently carries those same
names in the core app, which is pre-existing drift; the management layout is out of scope for this
feature, so it is left alone and noted.

## Constitution Check

| Article | Bearing | Status |
|---|---|---|
| I Test-First | every task pairs a failing test before its template | planned |
| II Simplicity / III Anti-Abstraction | the rejected `render_context` tag was the abstraction to avoid | pass |
| XI Integration strategy | no view override, no allauth page fork, template override only | pass |
| XII Rendered-markup contracts | the new templates get markup-contract tests, not status-code tests | planned |
| XIII UI verification | browser check of the four anonymous pages before commit, no pixel baselines | planned |
| XIV Dual-audience | spec carries US-1/US-3 developer and US-2 end user | pass |
| XV Compatibility | default width unchanged, no consumer edit required, stylesheet rebuilt | planned |
| XVII Composition | see P3; no class authored, no stylesheet rule added | pass |

No violation to record.

## Verification approach

- **US-1** renders a bare `{% extends "dac/entrance.html" %}` string through the component fixture.
  A template string belongs to no app, which is precisely the "does not depend on `dac.allauth`"
  condition SC-001 asks for.
- **US-2** captures the rendered markup of every anonymous allauth page before the rewiring and
  asserts byte-identical output after it. The capture is a test fixture generated during the task,
  not a committed baseline — Article XIII declines standing baselines, and this comparison is
  answering one question once.
- **SC-004** ("renders with the integration uninstalled") is asserted structurally rather than by
  reconfiguring `INSTALLED_APPS` mid-suite: a guardrail test asserts the core entrance templates
  reference no path under an integration directory. That is the property that makes the claim true,
  and it fails loudly if a future edit reaches sideways.
- Full `forge verify` plus a browser pass on login, signup, password reset and sign-in code.

## Out of scope

Where entrance pages sit in the URL space (R4), widening mvp's component (django-mvp#126), adopting
the wider scale here (#20), and the management layout.
