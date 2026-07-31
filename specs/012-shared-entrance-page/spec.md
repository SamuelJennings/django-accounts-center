# Feature Specification: A shared entrance page owned by the core package

**Feature Branch**: `012-shared-entrance-page`

**Created**: 2026-07-31

**Status**: Draft

**Serves**: G2 (a shared entrance layout) · **Roadmap**: R1 · **Issue**: #19

**Input**: User description: "A shared entrance page owned by the core package: move the full-screen centered-card entrance page out of the allauth integration into the core dac app so any integration with anonymous-facing pages can render through it, let a page choose its card width through a supported attribute rather than one fixed size, and make the allauth integration the first consumer of the shared page with no visible change to its output."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - [Developer] An entrance page the core package owns (Priority: P1)

A developer is building an integration that has pages for signed-out visitors — an invitation
acceptance page, say, or a magic-link landing page. They want it to look like every other
signed-out page in the Account Center. Today the only entrance layout in the package belongs to
`dac.allauth`, so their choice is to extend a template belonging to a package their integration
has nothing to do with, or to write the card themselves and drift. After this feature the
entrance page belongs to the core app, and their integration reaches it directly.

**Why this priority**: This is the whole point of the feature and the goal it serves. Without it
G2 is unmet: there is no shared entrance layout, only one integration's private one.

**Independent Test**: Render a page from an app that does not depend on `dac.allauth` through the
shared entrance page and assert it produces the full-screen background, the centered card, and
the site logo, with the app's own content inside the card.

**Acceptance Scenarios**:

1. **Given** an installed app with an anonymous-facing view, **When** its template extends the
   core entrance page and fills the content region, **Then** the page renders the background,
   card and logo without the app supplying any of that markup.
2. **Given** a project with `dac.allauth` absent from `INSTALLED_APPS`, **When** an anonymous page
   renders through the core entrance page, **Then** it renders correctly and references no
   template belonging to an integration.
3. **Given** a page rendered through the core entrance page, **When** a message is queued for the
   visitor, **Then** the message displays as it does on entrance pages today.

---

### User Story 2 - [End User] Signed-out pages are unchanged (Priority: P1)

Someone signing in, signing up, resetting a password or entering a sign-in code sees exactly the
page they saw before. The entrance page changing owner is invisible to them, which is the point:
this is a structural move, and a visitor should never be able to tell it happened.

**Why this priority**: The move only counts as done if it costs nothing. A regression in the
signed-out pages is the most visible failure this package can ship, because those pages are the
first thing every visitor sees. Implemented alongside US-1 — they are two sides of one change.

**Independent Test**: Render every anonymous allauth page before and after the rewiring and
compare the rendered markup.

**Acceptance Scenarios**:

1. **Given** the login, signup, password-reset and sign-in-code pages, **When** each renders after
   the allauth entrance layout is rewired to the shared page, **Then** its visible output is the
   same as before the change.
2. **Given** any anonymous allauth page, **When** it renders, **Then** the site logo, card width
   and page background are the ones it had before.
3. **Given** the allauth integration, **When** its entrance layout is inspected, **Then** it
   contains no card, background or logo markup of its own.

---

### User Story 3 - [Developer] A page asks for the card width it needs (Priority: P2)

A password-reset form is one field and a button. A signup page with a provider list is several
times that, and both currently render in a card of one fixed width. A developer writing an
entrance page states the width that page wants, and a page that states nothing keeps the width it
has today.

**Why this priority**: Additive, and the range it can offer is capped by what django-mvp's
entrance component expresses. The ownership move in US-1 and US-2 delivers the goal on its own,
so this rides along rather than gating it.

**Independent Test**: Render two pages declaring different widths, assert each renders at the
width it declared, then render a third declaring none and assert it matches the current default.

**Acceptance Scenarios**:

1. **Given** two entrance pages declaring different card widths, **When** each renders, **Then**
   each card carries the width it declared.
2. **Given** an entrance page declaring no width, **When** it renders, **Then** the card is the
   width entrance pages have today.
3. **Given** a width the underlying component cannot express, **When** a developer looks for it,
   **Then** the documented choices name only widths that actually work.

---

### Edge Cases

- A page declares a width outside the range the underlying component offers. The documented
  choices are limited to what works, so this is a developer error rather than a runtime state.
  The page renders at the default rather than producing broken markup.
- Two installed apps each serve anonymous pages through the shared entrance page. Neither owns the
  page, so there is nothing to conflict over, and each page's content region is its own.
- The shared entrance page renders with no content in it. It produces an empty card rather than
  raising.
- A project overrides the entrance page itself. The override wins, as template overrides always
  do, and nothing in this package assumes otherwise.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The core package MUST provide an entrance page rendering a full-screen background,
  a single centered card, and the site logo above the page's own content.
- **FR-002**: Any installed app MUST be able to render an anonymous-facing page through the
  entrance page without depending on, or referencing a template belonging to, any integration.
- **FR-003**: The entrance page MUST expose a content region the extending page fills, and MUST
  NOT require that page to reproduce the background, card or logo.
- **FR-004**: An extending page MUST be able to declare the card width it wants.
- **FR-005**: An extending page declaring no width MUST render at the width entrance pages render
  at today, so no existing page changes by omission.
- **FR-006**: The declarable widths MUST be limited to what django-mvp's entrance component
  expresses. Where a wanted width is not expressible, the shortfall is raised upstream and left
  there — this package MUST NOT reproduce the card in its own markup or add a stylesheet rule to
  work around it (Article XVII).
- **FR-007**: The allauth integration's entrance layout MUST render through the shared entrance
  page and MUST NOT contain background, card or logo markup of its own.
- **FR-008**: Every anonymous allauth page MUST render with the same visible output after the
  rewiring as before it.
- **FR-009**: The entrance page MUST carry the package stylesheet, so an extending page does not
  have to know about it.
- **FR-010**: The entrance page MUST render correctly when no integration is installed.
- **FR-011**: Queued messages MUST continue to display on pages rendered through the entrance
  page.
- **FR-012**: The architecture guardrails MUST still pass: no new allauth page-template fork, and
  the `base`, `entrance` and `manage` layout overrides still resolve.
- **FR-013**: The domain glossary MUST be reconciled so the entrance layout is described as a
  core-owned page rather than as something that exists only inside one integration.
- **FR-014**: The package documentation MUST describe the entrance page as an extension point:
  how a page reaches it, what it fills in, and how it declares a card width.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: An app that does not depend on the allauth integration serves an anonymous-facing
  page through the shared entrance page, demonstrated by a test in the suite.
- **SC-002**: Every anonymous allauth page — login, signup, password reset, sign-in codes and any
  other the installed allauth version serves — renders with unchanged visible output.
- **SC-003**: Two entrance pages declaring different widths each render at the width they
  declared, and a page declaring none renders at the current default.
- **SC-004**: The shared entrance page renders with `dac.allauth` absent from `INSTALLED_APPS`.
- **SC-005**: No entrance page in the package writes its own card, background or logo markup:
  every one reaches the shared page.
- **SC-006**: A developer can build an entrance page for their own app from the documentation
  alone, without reading this package's templates.

## Assumptions

- **The entrance page is a template extension point, not a view.** The core app serves no
  anonymous pages of its own, so an integration keeps its own views and URLs and reaches the
  shared page through its templates.
- **Card width is chosen by the page author.** Not by a project setting and not per request. The
  issue asks for a card that sizes itself to what a page needs, and what a page needs is a
  property of the page.
- **The default width is today's width.** Existing pages are rewired without declaring anything
  and come out identical, which is what makes US-2 achievable.
- **Where entrance pages sit in the URL space is out of scope.** That question belongs to R4,
  which owns the single account-management path and the position of anonymous pages relative to
  it. Nothing here fixes a URL.
- **django-mvp keeps owning the card and background markup.** This package composes its entrance
  component (Article XVII); it does not reimplement one.
- **The width range available at merge is the interim one.** django-mvp's component offers one
  boolean today. The wider scale is requested at django-mvp/django-mvp#126, and adopting it here
  is tracked separately at #20 rather than blocking this feature.
- **The site logo is django-mvp's, at the size entrance pages use today.** Making the logo
  configurable is not part of this.
