<!--
Sync Impact Report
- Version change: 1.1.4 → 1.1.5
- Change type: PATCH — Removed the tablet (768×1024) viewport from the required
  screenshot tiers. Desktop (1440×900) and mobile (390×844) are now the two
  canonical tiers. Tablet screenshots are available as an optional explicit capture
  when a component has a meaningful md-breakpoint layout that differs visually from
  both desktop and mobile. Updated Principle XIII heading, viewport table,
  settings-permutation wording, implementation rules, agent decision rule, rationale,
  and Quality Gates accordingly. No structural principle changes.
- Modified principles:
  - Principle XIII: viewport tiers reduced from three (desktop/tablet/mobile) to
    two (desktop/mobile); tablet noted as optional for md-breakpoint components
- Added sections: none
- Removed sections: none
- Templates requiring updates:
  - .specify/templates/tasks-template.md — ✅ updated screenshot task pattern to
    remove tablet tier; now references desktop + mobile only
  - .specify/templates/plan-template.md — ✅ no hardcoded three-tier wording found;
    no update required
  - .specify/templates/spec-template.md — no update required
- Deferred items: none

--- Previous Report (v1.1.4, 2026-05-22) ---
- Version change: 1.1.3 → 1.1.4
- Change type: PATCH — Clarified the boundary between playwright-cli interactive
  verification (Principle VI) and screenshot file analysis (Principle XIII). Added
  an explicit token-efficiency priority rule to Principle VI stating that playwright-cli
  MUST be the first choice for all UI verification and that screenshot file analysis
  is a token-expensive fallback. Replaced the blanket NON-NEGOTIABLE screenshot
  inspection mandate in Principle XIII with a decision rule that limits screenshot
  analysis to cases where interactive verification is insufficient (multi-viewport
  layout differences, settings-permutation visual diffs, subtle CSS regressions, or
  explicit human review requests). No structural principle changes.
- Modified principles:
  - Principle VI: added token-efficiency priority and screenshot-fallback boundary rule
  - Principle XIII: replaced blanket screenshot inspection mandate with conditional
    decision rule; removed NON-NEGOTIABLE label from agent visual verification bullet
- Added sections: none
- Removed sections: none
- Templates requiring updates:
  - .specify/templates/plan-template.md — no update required
  - .specify/templates/tasks-template.md — no update required
  - .specify/templates/spec-template.md — no update required
- Deferred items: none

--- Previous Report (v1.1.3, 2026-05-22) ---
- Version change: 1.1.2 → 1.1.3
- Change type: PATCH — Updated Principle VI to mandate the `playwright-cli` skill
  (`.github/skills/playwright-cli/SKILL.md`) as the required tool for all UI
  verification tasks. Replaced all references to "Playwright MCP server" with
  "playwright-cli skill". Added an explicit bullet requiring that the skill file is
  read before any browser-based verification step. Updated the Development Workflow
  section to reference playwright-cli instead of playwright-mcp. No structural
  principle changes; intent of Principle VI (verify UI changes in a real browser)
  is unchanged.
- Modified principles:
  - Principle VI: renamed "(playwright-mcp)" → "(playwright-cli)"; replaced all
    "Playwright MCP server" references with "playwright-cli skill"; added mandatory
    skill-consultation bullet
- Added sections: none
- Removed sections: none
- Templates requiring updates:
  - .specify/templates/plan-template.md — ✅ no "Playwright MCP" wording found;
    no update required
  - .specify/templates/tasks-template.md — ✅ no "Playwright MCP" wording found;
    no update required
  - .specify/templates/spec-template.md — no update required
- Deferred items: none

--- Previous Report (v1.1.2, 2026-05-08) ---
- Version change: 1.1.1 → 1.1.2
- Change type: PATCH — Clarified Principle XIII to document that screenshot tests
  MUST live in the root `screenshots/` directory (not inside `tests/`), are excluded
  from normal pytest runs via `testpaths = ["tests"]`, and are regenerated explicitly
  with `pytest screenshots/`. No structural principle changes; this formalises the
  existing project layout convention.
- Modified principles:
  - Principle XIII: added "Screenshot test location & invocation" bullet to
    Implementation Rules
- Added sections: none
- Removed sections: none
- Templates requiring updates:
  - .specify/templates/tasks-template.md ✅ Updated Path Conventions and screenshot
    task pattern to reference `screenshots/` directory and `pytest screenshots/`
  - .specify/templates/plan-template.md ✅ Added `screenshots/` to project structure
  - .specify/templates/spec-template.md — no update required
- Deferred items: none

--- Previous Report (v1.1.1, 2026-05-07) ---
- Version change: 1.1.0 → 1.1.1
- Change type: PATCH — Clarified Principle XIII to add mandatory agent visual
  verification step. Implementing agents MUST inspect generated screenshot files
  (not merely run the tests) before closing any UI task. No structural changes;
  intent of the principle is unchanged.
- Modified principles:
  - Principle XIII: added "Agent visual verification" bullet to Implementation Rules
- Added sections: none
- Removed sections: none
- Templates requiring updates:
  - .specify/templates/plan-template.md — no update required
  - .specify/templates/tasks-template.md — no update required
  - .specify/templates/spec-template.md — no update required
- Deferred items: none

--- Previous Report (v1.1.0, 2026-05-07) ---
- Version change: 1.0.0 → 1.1.0
- Change type: MINOR — Added Principle XIII (Multi-Viewport Screenshot Coverage).
  This principle mandates that all UI-modifying tasks must be accompanied by
  pytest-playwright screenshot tests capturing two canonical viewport sizes
  (desktop 1440×900, tablet 768×1024, mobile 390×844) and persisting them under
  docs/_static/{desktop,tablet,mobile}/. Settings-permutation screenshots are
  required for any page whose visual output varies by configuration.
- Modified principles: none
- Added sections:
  - Principle XIII: Multi-Viewport Screenshot Coverage (NON-NEGOTIABLE)
- Removed sections: none
- Templates requiring updates:
  - .specify/templates/plan-template.md ✅ Updated project structure to include
    docs/_static/ screenshot directories
  - .specify/templates/tasks-template.md ✅ Added screenshot capture task note
    for UI-modifying phases
  - .specify/templates/spec-template.md — no update required (screenshot
    requirements are implementation-phase concerns, not spec-level)
- Deferred items: none

--- Previous Report (v1.0.0, 2026-05-07) ---
- Version change: (blank template) → 1.0.0
- Change type: MAJOR — Initial ratification of the Django Accounts Center constitution
  from blank speckit template. All twelve principles authored from scratch,
  mirroring django-mvp v3.6.0 with DAC-specific adaptations:
    - Source tree references use dac/ rather than mvp/
    - Principle IX: django-mvp components take highest priority before django-cotton-bs5
    - Principle X: Third-Party Integration Strategy (replaces django-mvp Skill Currency)
    - Principle XII: View Class Docstring Completeness scoped to dac/views/
- Modified principles: none (first issue)
- Added sections: ALL (initial ratification)
- Removed sections: none
- Templates requiring updates:
  - .specify/templates/plan-template.md ✅ Updated path conventions to reflect
    dac/ source tree; Constitution Check section is dynamic (no hardcoded gates)
  - .specify/templates/spec-template.md ✅ Updated user story format to include
    [Developer] / [End User] audience labels per Principle XI
  - .specify/templates/tasks-template.md ✅ Updated path conventions (dac/ instead
    of src/) and added per-phase validation checkpoint tasks per Principle I
- Deferred items: none
-->

# Django Accounts Center Constitution

## Core Principles

### I. Design-First, Verify Implementation (NON-NEGOTIABLE)

All behavior changes MUST follow a design-verify-test workflow to ensure alignment
between expectations and implementation.

**Rationale**: Account management flows are security-sensitive and user-visible. Implementing design first allows for visual verification and user feedback before investing time in test design. This reduces wasted effort on tests for flows that do not match user expectations or third-party package constraints.

**Workflow**:

1. **Design Phase**: Create the design (mockups, wireframes, or initial implementation) based on specifications
2. **Verification Phase**: Verify the design meets expectations using visual inspection
   (`playwright-cli` skill for UI), user feedback, and manual testing
3. **Implementation Phase**: Refine implementation based on verification feedback
4. **Testing Phase**: Write comprehensive tests for the verified, approved implementation

**Testing Requirements** (after design verification):

- All new or changed Python behavior MUST have pytest coverage.
- Django integration behavior MUST have pytest-django coverage.
- Cotton component tests MUST use the fixtures and patterns defined in the
  `cotton-test-components` skill (`.github/skills/cotton-test-components/SKILL.md`).
  The skill MUST be consulted before writing any Cotton component test. Use
  `cotton_render` / `cotton_render_soup` / `cotton_render_string` / `cotton_render_string_soup`
  from `django-cotton-bs5` as appropriate (NOT `Template()` or `render_to_string`).
- Cotton component tests MUST live under `tests/test_components/` and MUST be grouped
  by top-level Cotton directory to keep discovery predictable: all
  `templates/cotton/dac/**` components in one shared module, and the same pattern
  for every additional top-level directory under `templates/cotton/`.
- Single-file top-level Cotton components MUST be grouped into one shared top-level
  module rather than split into one file per tiny component.
- One-test-module-per-tiny-component sprawl is prohibited unless a strong, explicit
  exception is documented in the related spec/plan/tasks artifact.
- Test structure MUST mirror the `dac/` source tree
  (e.g., `dac/views.py` → `tests/test_views.py`;
  `dac/menus.py` → `tests/test_menus.py`).
- Fixture factories MUST use factory-boy (`DjangoModelFactory`) for reusable test
  data; ad-hoc inline model creation is only acceptable for truly one-off fixtures
  with no reuse potential.
- Performance tests MUST NOT use wall-clock timing assertions; use deterministic
  guards (e.g., `django_assert_num_queries`) instead.
- User-visible/UI behavior MUST have pytest-playwright coverage when the change
  affects rendered output, interactions, or accessibility.
- Pull requests MUST NOT be merged with failing tests, or without new/updated tests
  for behavior changes.
- The only acceptable exception is a docs-only change (no runtime behavior impact).

**Story-Level Validation (NON-NEGOTIABLE)**:

- **Task Breakdown**: Tasks (`tasks.md`) MUST be grouped by user story so that each
  story can be implemented and tested independently where feasible. Shared foundational
  work MUST be captured as explicit blocking tasks. Every phase in `tasks.md` that
  modifies any Django code (models, views, forms, URLs, settings, migrations,
  templates) MUST include an explicit validation task running
  `python manage.py check` AND the pytest suite for the touched area
  (e.g., `pytest tests/test_views/` after a view phase). These validation tasks are
  REQUIRED regardless of which tool or agent generates `tasks.md`; they MUST NOT be
  omitted when regenerating, updating, or re-ordering task files.
- **Test-First Discipline**: Tests MUST be written and observed failing before
  implementation begins. No change MAY be merged that causes the agreed test suite
  for the touched area to fail.
- **System Checks**: `python manage.py check` MUST pass after completing each user
  story or major phase; model errors, admin field references, and misconfiguration
  MUST be caught before they reach staging.
- **Validation Frequency**: For multi-phase implementations, run system checks after
  each phase and update documentation incrementally.

### II. Documentation-First

Documentation is part of the product surface area.

- Every public setting, template block, and component MUST be documented with at
  least one minimal usage example.
- Any change to public behavior MUST include a docs update in the same pull request.
- Examples MUST be kept working and reflect the current recommended usage.
- Docs MUST describe expected behavior in testable terms (inputs, outputs, and
  constraints).

### III. Component Quality & Accessibility

Components MUST be usable, accessible, and predictable.

- Components MUST render valid, semantic HTML.
- Components MUST be accessible by default (keyboard navigable where relevant, with
  appropriate ARIA when necessary).
- If a change affects markup structure, add/update tests that assert the rendered
  HTML contract.
- UI behavior changes SHOULD be covered by browser tests when feasible.

### IV. Compatibility & Config-Driven Design

This is a reusable Django extension; upgrades and consumers matter.

- Prefer template overrides and extension points over Python-level customisation.
- View overrides are permitted only on a case-by-case basis with documented
  justification; they MUST NOT be the first reach for third-party package integration.
- Breaking changes MUST be avoided; if unavoidable, they MUST be explicit, documented,
  and versioned.
- Default behavior MUST remain stable across minor releases.
- **Cotton-Only UI Configuration**: UI configuration and customization MUST be achieved
  exclusively through Django Cotton components and template-level overrides.
  Python-level configuration is reserved for structural settings (e.g., installed
  apps, database, middleware). No CSS/JS wiring, layout selection, or component
  behavior MAY be configured through Python code when a Cotton component attribute
  or slot override is sufficient.

### V. Tooling & Consistency

The project uses consistent tooling to keep quality high and contributions smooth.

- Project commands MUST run through Poetry (e.g., `poetry run pytest`).
- Code MUST satisfy linting/formatting and any configured static checks before merge.
- Static analysis: Ruff (lint + format) for Python; djlint for templates. Both MUST
  be configured in `pyproject.toml` and MUST pass in CI. Template files MUST NOT be
  committed with djlint violations.
- Keep changes minimal and focused; avoid incidental refactors.

### VI. UI Verification (playwright-cli)

Agents MUST verify UI changes using the `playwright-cli` skill during implementation.

- When building or modifying UI elements, agents MUST use the `playwright-cli` skill
  (`.github/skills/playwright-cli/SKILL.md`) to open a real browser, interact with
  the rendered output, and confirm that implementation changes are visually and
  interactively represented as expected.
- The `playwright-cli` skill MUST be read and followed before performing any
  browser-based verification step. Agents MUST NOT attempt ad-hoc browser automation
  without consulting the skill.
- **Token-efficiency priority**: `playwright-cli` interactive verification is the
  most token-efficient confirmation method and MUST be the first and default choice
  for all UI verification tasks. Opening and examining generated screenshot files is
  a token-expensive secondary step; agents MUST NOT read screenshot files unless the
  conditions in Principle XIII's agent visual verification decision rule are met.
- Any phase in `tasks.md` that modifies the user experience — including HTML
  templates, Cotton components, form rendering, CSS, HTMX interactions, or any
  visible UI element — MUST include at least one `playwright-cli` verification task
  that confirms the expected interactive or visual outcome in a real browser.
- Verification tasks MUST assert the specific UX behaviour described in the
  corresponding user story acceptance criteria and MUST NOT merely assert that the
  page loads without error.
- Visual verification MUST occur after each significant UI modification to catch
  rendering issues before they are committed.
- This requirement applies to all `tasks.md` files regardless of which agent or tool
  generates them.

### VII. Documentation Retrieval (context7)

Agents MUST use current documentation when working with dependencies.

- Agents MUST use context7 to retrieve up-to-date documentation for all packages and
  libraries they are working with.
- This ensures that code follows current API patterns and best practices rather than
  outdated examples.
- Context7 MUST be consulted before implementing features that rely on external
  libraries (Django, django-mvp, Cotton, Bootstrap, django-allauth, etc.).

### VIII. End-to-End Testing (pytest-playwright)

Features MUST include comprehensive end-to-end test coverage using pytest-playwright.

- All new features MUST include end-to-end tests using pytest-playwright to verify
  complete user workflows.
- E2E tests MUST cover the entire user journey from initial page load through final
  action completion.
- UI interactions, form submissions, navigation flows, and visual elements MUST be
  tested at the browser level.
- E2E tests serve as acceptance tests that validate feature requirements are fully met.
- **Distinction from Principle VI**: `playwright-cli` skill tasks (Principle VI) are
  the inline interactive verification step performed by agents during implementation;
  pytest-playwright tests (this principle) are the formal regression suite that
  persists in the repository and runs in CI.

### IX. Template Component Reuse Discipline (NON-NEGOTIABLE)

Template markup is a first-class authoring surface. `django-accounts-center` renders
account management UIs using the django-mvp component system; consistency with the
host application's look and feel depends on delegating all presentational decisions
to django-mvp components wherever possible.

**Component priority order (MUST be followed)**:

1. **django-mvp components first**: Before authoring any template markup, agents MUST
   check whether a django-mvp component (`<c-mvp-*>` or equivalent) already covers
   the need. Using django-mvp components ensures that a consumer's site-wide style
   overrides propagate automatically into account management pages.
2. **django-cotton-bs5 prebuilt second**: If no django-mvp component satisfies the
   need, check whether a prebuilt `django-cotton-bs5` component applies. The
   `django-cotton-bs5` skill (`.github/skills/django-cotton-bs5/SKILL.md`) MUST be
   consulted before authoring raw HTML that could be served by an existing component.
3. **Custom Cotton component last resort**: If no prebuilt component from either
   library satisfies the need AND the template segment appears in more than one
   location or is conceptually reusable, a custom Cotton component MUST be created
   (following the `django-cotton` skill at `.github/skills/django-cotton/SKILL.md`)
   rather than an `{% include %}`-based partial. Custom components in this package
   are strongly discouraged and MUST be justified in the PR description.

**Additional rules**:

- Django template partials used solely via `{% include %}` MUST NOT be introduced for
  reusable content.
- **Exemption**: Genuinely one-off, non-reusable markup unique to a single view with
  no reasonable extraction path is exempt from the custom-component mandate. Even
  within exempt fragments, django-mvp and django-cotton-bs5 components MUST still be
  used wherever they apply.
- **Component placement**: Custom Cotton component files MUST be placed under
  `templates/cotton/` (or an appropriate app-scoped subdirectory) and named using
  lowercase-kebab convention (e.g., `my-widget.html`). Files MUST NOT be placed
  alongside view templates or nested arbitrarily.
- **Testing mandate**: Every custom Cotton component MUST be covered by tests that
  exercise rendering, attributes, slots, and edge-case behaviour. Tests MUST follow
  the `cotton-test-components` skill
  (`.github/skills/cotton-test-components/SKILL.md`).
- **Test module topology mandate**: Cotton component tests MUST be organized under
  `tests/test_components/` by top-level Cotton directory, with one module per
  top-level directory. Single-file top-level components MUST be grouped in one shared
  top-level module. One test module per tiny component is prohibited unless the
  exception is documented and justified.
- **Rationale**: Keeping django-mvp as the primary component surface ensures that a
  consumer's site-wide overrides propagate automatically. Minimising custom components
  reduces surface area and maintenance burden for this extension package.

### X. Third-Party Integration Strategy (NON-NEGOTIABLE)

`django-accounts-center` integrates with third-party Django packages
(e.g., django-allauth, django-activity-stream, Stripe) to provide a unified account
management interface without requiring changes to those packages.

- **Template overrides primary**: Integration with third-party packages MUST be
  achieved through template overrides wherever the target package supports it.
  Template overrides are additive, upgrade-safe, and do not require forking or
  patching the upstream package.
- **View overrides case-by-case**: Custom view classes that override third-party
  package views are permitted only when template overrides are insufficient. Every
  such override MUST be documented with:
  - The upstream view being overridden and the upstream package version it was
    verified against.
  - The specific reason a template override is insufficient.
  - An upgrade note describing how to verify the override on dependency updates.
- **No source patches**: The package MUST NOT rely on monkey-patching, private APIs,
  or internal details of third-party packages. Integrations MUST degrade gracefully
  if the optional third-party package is not installed.
- **Addon isolation**: Each third-party integration MUST be isolated under
  `dac/addons/<package_name>/` so that consumers only incur the dependency cost of
  integrations they actually install. An addon MUST NOT import or reference another
  addon at module level.
- **Version pinning**: Verified compatibility ranges for third-party packages MUST be
  recorded in `pyproject.toml` and updated whenever an integration is modified.
- **Graceful degradation**: Features that depend on optional third-party packages MUST
  fail silently (suppress UI elements) rather than raising errors when the optional
  package is not installed.

### XI. Dual-Audience User Stories (NON-NEGOTIABLE)

`django-accounts-center` is a reusable Django extension consumed by two distinct
audiences: **developers** who integrate and configure it, and **end users** who
interact with the resulting account management UI at runtime. Both audiences MUST be
represented in every feature specification.

- **Developer stories** describe the integrator experience: installing and wiring the
  package, configuring templates and URLs, enabling optional addons, and understanding
  the public API. Example: *"As a developer, I want to include the account center in
  my project by adding a single URL include, so I can get account management without
  writing custom views."*
- **End-user stories** describe the runtime experience of a logged-in user managing
  their account. Example: *"As a user, I want to view and update all my account
  details from a single page, so I do not have to navigate to multiple separate
  sections."*
- Every feature specification (`spec.md`) MUST include at least one developer story
  AND at least one end-user story before the spec is considered complete. A spec with
  only one audience represented MUST be treated as a failing acceptance criterion.
- Developer stories and end-user stories MUST be clearly labelled using
  `[Developer]` / `[End User]` tags on the story heading or as an **Audience** field.
- Prioritisation (P1, P2 …) applies independently within each audience group; a P1
  developer story and a P1 end-user story may coexist and SHOULD be implemented
  together where they describe two sides of the same feature.

### XII. View Class Docstring Completeness (NON-NEGOTIABLE)

Every public view mixin and concrete base view class in `dac/views/` (and within
addon view modules) MUST carry a comprehensive class-level docstring that serves as
the authoritative reference for human contributors and AI agents.

**Rationale**: Account management flows involve security-sensitive behaviour and
complex third-party integration. Without complete, structured docstrings, integration
attributes inherited from mixins become invisible, override hooks go undiscovered, and
contributors risk introducing regressions. A well-structured docstring is both a
quality gate and a knowledge-transfer artifact.

**Requirements**:

- **Scope**: Every public mixin and concrete base class in `dac/views/` and in
  `dac/addons/*/` view modules MUST have a class-level docstring. Private helpers
  (`_*` prefix) and internal detail classes are exempt.
- **Intended-use summary**: The docstring MUST open with one or two sentences
  describing what the class does and when a developer should reach for it.
- **Config section**: The docstring MUST include a `Config:` block listing every
  configuration attribute a downstream developer may set, using the format:

  ```
  Config:
      - ``attr_name`` (type, default): One-line description plus any special
        behaviour. Attributes inherited from mixins that are routinely overridden
        MUST also appear here; their provenance may be noted parenthetically.
  ```

- **Override hooks**: Any method that downstream classes are expected to override MUST
  be listed under an `Override hooks:` subsection with a one-line summary of the
  expected return type and intended customisation point.
- **Minimal example**: Where the class is the primary entry point for a new
  developer, the docstring SHOULD include at minimum a short usage example showing
  the class wired to a URL.
- **Completeness gate**: A pull request that introduces a new view mixin or base class
  without a conforming docstring MUST NOT be merged. A PR that modifies the public
  interface of an existing class MUST update its docstring in the same PR.
- **AI-agent discoverability**: Docstrings are the canonical surface area description
  consumed by AI agents performing code lookups. They MUST be complete enough that
  an agent can determine all available knobs and extension points without reading
  every parent class.

### XIII. Multi-Viewport Screenshot Coverage (NON-NEGOTIABLE)

All tasks that modify UI MUST be accompanied by automated Playwright tests that
capture screenshots at two canonical viewport sizes and persist them as visual
documentation artifacts under `docs/_static/`.

**Viewport Sizes** (MUST be used consistently across all screenshot tests):

| Tier    | Width | Height | Representative device    |
|---------|-------|--------|--------------------------|
| Desktop | 1440  | 900    | 13″ laptop / wide monitor |
| Mobile  | 390   | 844    | iPhone 12 / 13 portrait  |

**Tablet (optional)**: A 768×1024 tablet capture MAY be added when a component has
a meaningful `md`-breakpoint layout that is visually distinct from both desktop and
mobile. Tablet is not a default requirement.

**Storage Convention**:

Screenshots MUST be saved under `docs/_static/` partitioned by viewport tier:

```
docs/_static/
├── desktop/<page-name>.png
└── mobile/<page-name>.png
```

Where `<page-name>` is the lowercase-kebab slug of the page being captured
(e.g., `signup-page`, `account-settings`, `login-page`).

**Settings-Permutation Requirement** (NON-NEGOTIABLE):

For any page whose visual output varies based on Django or package settings (e.g.,
whether social accounts are enabled, MFA is active, or a specific addon is installed),
a desktop and mobile screenshot MUST be captured for **each distinct visible
configuration**. Permutation screenshots MUST follow the naming pattern
`<page-name>-<config-slug>.png`. Examples:

```
docs/_static/desktop/signup-page-social-enabled.png
docs/_static/desktop/signup-page-social-disabled.png
docs/_static/desktop/signup-page-social-only.png
...
```

All reachable settings permutations that produce a visually distinct page state MUST
be documented with screenshots. A permutation is "visually distinct" if it adds,
removes, or materially rearranges any visible UI element.

**Implementation Rules**:

- Screenshot capture MUST be implemented as pytest-playwright tests (see Principle
  VIII), NOT as one-off scripts or manual captures.
- Screenshot tests MUST live under the root `screenshots/` directory (e.g.,
  `screenshots/test_signup_screenshots.py`), NOT inside the `tests/` tree. Because
  `pyproject.toml` sets `testpaths = ["tests"]`, a plain `pytest` invocation never
  discovers the `screenshots/` directory, keeping normal test runs fast. To
  regenerate screenshots explicitly, run `pytest screenshots/`.
- Tests MUST use `@pytest.mark.parametrize` or a viewport fixture to switch across
  both sizes (desktop and mobile) without duplicating assertion logic.
- Screenshots MUST be committed to the repository alongside the code change that
  introduces the UI modification; a PR that changes UI without updated screenshots
  MUST NOT be merged.
- CI MUST execute the screenshot tests so screenshots are regenerated on each run and
  any visual regression that produces a diff causes a deliberate review step.
- Screenshots are **living documentation**; stale screenshots (not updated when the
  UI changes) constitute a quality failure equivalent to a failing test.
- The `docs/_static/desktop/` and `docs/_static/mobile/`
  directories MUST be created before the first screenshot test runs; if they do not
  exist, the test setup MUST create them.
- **Agent visual verification — decision rule**: `playwright-cli` interactive
  verification (Principle VI) is the default confirmation method and is sufficient
  for most UI tasks. Agents MUST NOT open or analyse screenshot files as a routine
  step when `playwright-cli` has already confirmed the expected interactive state;
  doing so wastes token budget unnecessarily.
  Screenshot file analysis is warranted **only** in the following cases:
  - **Multi-viewport layout differences**: the change may render differently at
    mobile (390 px) width and the difference cannot be confirmed interactively
    with `playwright-cli` alone.
  - **Settings-permutation diffs**: the task generates permutation screenshots and
    the agent must confirm that two or more config states produce visually distinct
    output.
  - **Subtle CSS/layout regression**: the change involves precise spacing, overflow,
    or z-index behaviour that the `playwright-cli` snapshot cannot reliably surface.
  - **Explicit human request**: the user or reviewer has specifically asked the agent
    to open and describe a screenshot.
  Outside these four cases, agents MUST rely solely on `playwright-cli` verification
  and MUST NOT open screenshot files. Any discrepancy found during warranted
  screenshot analysis MUST be resolved before the task is closed.

**Rationale**: Account management UIs must remain coherent across device categories.
Visual regressions on mobile viewports are routinely invisible to developers working
only on desktop. Persisted screenshots provide reviewers, project maintainers,
and future agents with an authoritative visual reference for every page state and
settings permutation, reducing the risk of silent regressions and misaligned
integrations.

## Quality Gates

The following gates MUST pass for every pull request that changes runtime behavior:

- Unit/integration tests pass (`pytest` via Poetry).
- Linting passes (Ruff).
- Formatting is applied (Ruff formatter).
- Documentation is updated when public behavior changes.
- `python manage.py check` passes with no errors.

If a change affects UI output or interaction:

- Add or update pytest-playwright coverage (Principle VIII).
- Capture and commit viewport screenshots for both tiers (desktop and mobile)
  and all distinct settings permutations (Principle XIII).

## Development Workflow

- Start with the design that expresses the desired behavior and visual appearance
- Verify the design meets expectations through visual inspection and user feedback
  (use the `playwright-cli` skill for UI verification)
- Refine the implementation based on verification feedback
- Write comprehensive tests for the verified implementation (unit, integration,
  and end-to-end)
- After each user story phase, run `python manage.py check` and the relevant pytest
  suite
- Update documentation alongside the change, not after
- Keep PRs small and reviewable; split unrelated changes
- Prefer template overrides over view overrides when integrating third-party packages

## Governance

This constitution defines non-negotiable project rules and supersedes local
conventions.

- Amendments MUST be proposed via pull request and include a brief rationale.
- Amendments MUST state whether they are MAJOR/MINOR/PATCH changes to this
  constitution.
- Any PR that materially changes development norms MUST update this constitution and
  any dependent templates.
- Reviews MUST explicitly check compliance with the Core Principles.

### Versioning Policy (Constitution)

- MAJOR: Removes or redefines a principle in a backward-incompatible way.
- MINOR: Adds a principle/section or materially expands guidance.
- PATCH: Clarifies wording or fixes typos without changing intent.

**Version**: 1.1.5 | **Ratified**: 2026-05-07 | **Last Amended**: 2026-05-22
