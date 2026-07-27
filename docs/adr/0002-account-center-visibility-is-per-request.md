# ADR 0002 — Account Center visibility is resolved per request

**Status:** accepted, not yet implemented

## Decision

Menu entries and overview cards answer one question per request: *should this appear for the
person looking at it, right now?*

Installation decides whether a contribution **exists**. The request decides whether it is
**shown**. Both halves are required — an integration that is installed is not thereby visible to
everyone.

The obligation sits on the integration. Each one declares, per request, whether each of its menu
entries and each of its cards applies to the current visitor, and a card that does not apply is
suppressed rather than rendered empty.

## Why

Most integrations worth bundling carry per-user state. A billing area means nothing to someone on
no plan. A team area means nothing to someone in no team. An integration whose pages apply to some
users has no way to say so if visibility is decided once at startup, and the person it does not
apply to gets a card or a menu entry leading somewhere useless.

That failure undermines the thing the framework promises. If adding an app to `INSTALLED_APPS` is
the whole wiring step, then the framework has to be the one that knows who a contribution is for.
Pushing the decision into each integration's views means every integration reimplements it and the
menu still lies.

The cost is accepted: every integration author implements one more hook, and the Account Center
pays a per-request cost it would not pay for a static menu. Visibility was considered as an
install-time-only concern and rejected. It is cheaper and it is wrong — a menu that lists things
you cannot use is worse than a shorter menu.

## State

Decided, not built. The code decides visibility once, at import, from `app_is_installed()`; no
menu item carries a check predicate and the overview page has no visibility predicate at all.

The goal is G6. The work is R6 in the roadmap, in the Essential phase. The mechanism is open —
django-flex-menus already evaluates a `check` predicate per request, and cards may turn out to be
better expressed as menu nodes than as the current `AppConfig` attributes. That is a question for
the feature's own design work, not for this decision.

## Revisit if

Per-request evaluation shows up as a measurable cost on Account Center page loads that caching
cannot absorb, or a pattern emerges where integrations consistently want the same visibility rule
and would be better served by declaring it once than by answering per request.
