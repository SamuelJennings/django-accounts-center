# ADR 0001 — Style allauth through elements and layouts, never page forks

**Status:** accepted

## Decision

The allauth integration restyles django-allauth by overriding its three **layouts**
(`allauth/layouts/base.html`, `entrance.html`, `manage.html`) and its 22
**element** templates (`allauth/elements/*.html`) only. Allauth's own page
templates do the rendering, and this package never ships a copy of one.

A per-page override is permitted only as a named exception: add it to
`PAGE_OVERRIDE_ALLOWLIST` in `tests/test_architecture.py` with a comment saying
why the element system could not express the result.
`account/snippets/warn_no_email.html` is the only entry today.

`tests/test_architecture.py` enforces this. It fails if an allauth page template
is forked without being allowlisted, if any of the 22 element overrides goes
missing, or if the allauth templates move out of the gated `dac.allauth` sub-app
into the core `dac` app.

## Why

The obvious way to restyle allauth is to copy its page templates and edit the
markup. That approach is what this package existed to escape.

Forking pages couples the package to allauth's page inventory. Every allauth
feature is a set of pages, and the feature set is large and still growing —
passkeys, login by code, email verification by code, phone numbers,
`SOCIALACCOUNT_ONLY`, MFA across TOTP, WebAuthn, recovery codes and trust, user
sessions. Each fork is a page frozen at the allauth version it was copied from,
and each allauth release risks leaving a fork silently stale: the upstream page
gains a field, a security notice or a config branch that the fork never renders.
The maintenance cost scales with allauth's feature set, which this project does
not control.

Elements invert that. Allauth composes its pages from a small, stable vocabulary
of parts, so overriding the parts styles every page built from them — including
pages that did not exist when the override was written. A new allauth feature
assembled from existing elements arrives styled. The maintenance surface becomes
22 small templates instead of an open-ended page count, and it tracks allauth's
*composition* vocabulary, which changes far more slowly than its feature set.

The cost is real and accepted: element overrides give less control than page
forks, so some layouts have to be expressed within what the element boundaries
allow rather than exactly as designed. The allowlist is the pressure valve, and
keeping it near-empty is the point.

This became the architecture in 0.7, replacing an earlier design that did fork
pages and shipped its own standalone shell.

## Revisit if

Allauth stops composing pages from elements, or begins shipping pages whose
structure the element vocabulary genuinely cannot express — at which point the
allowlist would start growing rather than holding at one or two entries. A
steadily growing allowlist is the signal that this decision has stopped paying
for itself.
