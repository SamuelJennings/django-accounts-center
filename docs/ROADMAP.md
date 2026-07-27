# Roadmap — django-accounts-center

**Date:** 2026-07-27

This document was designed against [GOALS.md](../GOALS.md). See also [CONTEXT.md](../CONTEXT.md) for
domain terminology and [memory/constitution.md](../memory/constitution.md) for project standards.

The first five items are already delivered. They are carried so the sequence reads whole and so
later work has something to cite.

## Versioning

Releases are gated on goal importance, not on a count of features.

| Version | Gate |
|---|---|
| `0.7.x` | The current line. Fixes and additive work while the Essential goals are still open. |
| **`0.8.0`** | **All Essential goals delivered.** The framework is usable by an integration that is not allauth. |
| `0.8.x` → `0.9.x` | Advance the Expected goals, at whatever granularity the work takes. Patches are fixes. |
| **`1.0.0`** | **All Expected goals delivered.** The complete, dependable release, and the point the integration contract becomes a public API. |
| `1.x` | Stable line. Non-breaking fixes and additive features only. |
| `2.0` | Next major. Breaking changes. |

Two rules this table does not show. A goal is not one minor release: some take several, and one
minor can move two goals at once. And once `1.0` ships, a breaking change never goes out as `1.x`
— it waits for the next major.

Aspirational goals may be developed against `2.0` or `1.x` as required.

This repo published `0.7.0` before its goals were recorded, so the standard `0.1.0` Essential gate
has been mapped onto the next minor rather than applied literally.

## Essential goals: v0.8.0

Everything needed before an integration that is not allauth can be built against this package.

The package provides exactly three page layouts, and the first three items are those. Everything
an integration renders is one of them.

### R1 — The management page

*Delivered · needs verification · advances G3*

A single page style for any view where a person controls one aspect of their account. It carries
the sub menu, the breadcrumbs, and the content area, so a management view written by one
integration is indistinguishable in shape from one written by another.

Serves G3.

### R2 — The account center dashboard

*Delivered · needs verification · advances G4*

The landing page of the Account Center: a dashboard of cards, each owned and rendered by the
integration that contributed it. The page collects whatever is installed without knowing what any
of it is.

Serves G4.

### R3 — The entrance page

*Delivered · needs verification · advances G2*

A full-screen page holding a single centered card, for anything a signed-out visitor sees. It is
built from django-mvp's entrance component rather than restyled here.

Serves G2. Where it lives and how far it can be configured are open — see R7.

### R4 — Integrations as gated sub-apps

*Delivered · needs verification · advances G1, G8*

Each integration is a separate sub-app with its own optional dependencies, enabled by adding it to
`INSTALLED_APPS`. A project carries only the dependencies of the integrations it turns on, and
contributes its menu group and its cards through documented hooks.

Serves G1 and G8.

### R5 — The allauth integration

*Delivered · needs verification · advances G8, G9*

The first integration built on the three layouts above. It styles allauth by overriding the parts
allauth composes its pages from rather than the pages themselves, so allauth features this package
has never seen arrive already styled.

Serves G8 and G9.

### R6 — Integrations mount their own URLs

*feature · advances G1, G5*

Enabling an integration currently requires an edit to the core app before its pages are reachable,
because the core URL configuration names each integration explicitly. Until that is inverted, G1
is false for any integration that does not already exist, and G5 has no single owner: the path the
Account Center lives under is chosen by each consuming project, and this repo's own README,
example project and test project each pick a different one.

This is first among the open items because R9 cannot be attempted while adding an integration
means patching the core.

**Deliverables:**

- An integration's URLs are reachable purely as a consequence of it being installed.
- One predictable path for account management, owned by this package rather than by the consuming
  project, and consistent across the README, the example project and the tests.
- A stated position on where entrance pages sit relative to that path, given they serve anonymous
  visitors rather than the Account Center.

Serves G1 and G5. Does not cover what an integration must provide to be discovered beyond its
URLs — that is R11.

### R7 — The entrance page belongs to the framework

*feature · advances G2*

The entrance page exists only inside the allauth integration. An integration with its own pages
for signed-out visitors has nothing to inherit, and would have to extend a template named for
another integration to get the same treatment.

It also offers no configuration. The card is one fixed size, and a page whose content does not
suit that size has no recourse.

**Deliverables:**

- The entrance page is owned by the core app and reachable by any integration.
- The card size is configurable, to the extent django-mvp's entrance component supports it. Where
  it does not, the shortfall is raised on django-mvp rather than solved here.
- The allauth integration reaches the shared page rather than defining its own, with no visible
  change to what it already renders.

Serves G2. Does not change how the entrance page looks by default.

### R8 — Per-user visibility

*feature · advances G6*

Menu entries and dashboard cards are decided once, when the process starts, from which apps are
installed. Every signed-in person sees the same Account Center. An integration whose pages only
apply to some users — a billing area for subscribers, a team area for people in a team — has no
way to say so, and the person it does not apply to gets a card or a menu entry that leads
somewhere useless.

**Deliverables:**

- An integration can declare, per request, whether each of its menu entries applies to the current
  visitor.
- The same for dashboard cards, including suppressing a card entirely rather than rendering an
  empty one.
- Installation continues to decide whether a contribution exists. The request decides whether it
  is shown.
- Tests that a contribution visible to one user is absent for another.

Serves G6. Does not cover authorization inside an integration's own views, which remains the
integration's responsibility.

### R9 — A second integration

*multi-feature · advances G1, G4, G8*

Every framework claim in GOALS is currently demonstrated by exactly one integration, which was
also the integration the framework was extracted from. Nothing proves a second one is possible,
and the parts that only one integration exercises are the parts most likely to be wrong. A second
integration built in-tree is the forcing function that turns R6, R7 and R8 from assertions into
facts, and it delivers a capability the projects this package serves actually need.

Which integration comes first is a scoping question for the feature work rather than something to
settle here.

**Deliverables:**

- A second integration shipped in-tree, gated and optional on the same terms as the first.
- Its menu group, its cards and its pages reach the Account Center through the documented
  mechanisms only, with no core changes made on its behalf.
- Any gap it exposes in the framework surfaced as a correction rather than worked around inside
  the integration.

Serves G1, G4 and G8. Does not include the contract documentation, which is R11.

### R10 — Verify the gate holds without allauth

*resolve · advances G1, G8*

The package claims a project carries only the dependencies of the integrations it enables, and by
inspection the claim holds. No test proves it. Every test run installs allauth and every one of its
optional apps, so the core-only configuration — the one an adopter of a future integration would
run — has never executed. The branches that skip an absent app have never been taken.

**Deliverables:**

- The core app is exercised without allauth installed, as part of the normal check on every change.
- The absent-app paths in the shipped integration are covered rather than assumed.

Serves G1 and G8.

### R11 — The integration contract, documented

*feature · advances G7*

An integration author has prose in the README, a glossary entry, and one worked example to read.
The extension points themselves are undocumented outside of that, and the rules that are not
expressed in code — the order an integration must appear in relative to the package it integrates,
what a contributed card may assume about the surrounding page, what happens when two integrations
contribute the same thing — are discoverable only by reading the source or getting it wrong.

This comes after R6 to R9 because documenting the contract before a second integration has
stressed it would document guesses.

**Deliverables:**

- A reference for integration authors covering every extension point, what each receives and what
  it is expected to return.
- The rules that are not enforced by code, stated as rules.
- The shipped integrations readable as worked examples against that reference.

Serves G7. Does not include machine-checkable conformance, which is R15.

## Expected goals: v1.0.0

The capabilities a complete, dependable version is expected to have.

### R12 — A user can export and delete their own data

*multi-feature · advances G10*

A person managing their account can see what the system holds about them, take a copy, and close
the account. This is the first capability in the Account Center that is about the person rather
than about the framework, and the obligations behind it are not optional for a project operating
in Europe.

Whether this arrives as first-party views or as an integration over an existing package is a
scoping question for the feature work.

**Deliverables:**

- A person can request and receive a copy of their own data.
- A person can delete their account, with the consequences stated before they confirm.
- Other integrations can contribute the data they hold to both, rather than each shipping its own
  export.

Serves G10. Does not cover an operator-facing compliance console.

### R13 — Allauth coverage that survives upstream releases

*feature · advances G9*

The allauth integration tracks upstream by styling the parts its pages are composed from, and a
check asserts every one of those parts has an override. The list of parts is written down by hand.
When allauth adds one, the check stays green and the new part renders unstyled, which is precisely
the failure the approach was chosen to avoid.

**Deliverables:**

- The set of parts to override is derived from the installed version of allauth rather than
  restated in this repo.
- A new or renamed part upstream is a failure here before it is a visual defect for an adopter.
- The supported upstream range is recorded and matches what is actually verified.

Serves G9.

### R14 — Profile management

*feature · advances G8*

Editing your own name, and whatever else a project considers part of a person's profile, is the
most common thing an account area does and the one capability every comparable product has. This
package has no answer for it, because the integration it was built around does not cover it and no
other integration exists.

**Deliverables:**

- A person can edit their own profile from the Account Center.
- A project can decide what a profile contains without forking the integration.

Serves G8. Does not cover public-facing profile pages, which are an application concern rather
than an account-management one.

## Aspirational goals: v2.0

Genuine wants whose absence never makes the package incomplete.

### R15 — A conformance kit for integration authors

*feature · advances G11*

Once the contract is a public API and several integrations exist in-tree, an author has no way to
check their integration behaves before shipping it, and the maintainers have no shared check
across the bundled set. Documentation covers this need while the count is small.

Serves G11.
