# ADR 0002 — Account Center visibility is resolved per request

**Status:** accepted, implemented for menu entries

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

Implemented for menu entries. An integration passes django-flex-menus' own `check` argument to a
`MenuItem` it contributes from its `menus.py` — a callable that takes the request and returns
whether that entry applies to the person making it. django-flex-menus evaluates `check` while
building the menu for each request, so two people loading the same page are answered separately,
and an entry whose check returns false is absent from the rendered tree. django-flex-menus already
hides a group left with no visible children, so a section with nothing left in it loses its
heading along with its entries — this package relies on that rather than reimplementing it. An
entry that declares no check stays visible whenever its integration is installed, exactly as
before this decision existed, so an existing integration needs no change to keep working.

A check that raises is not caught. The error surfaces as an error rather than being read as "does
not apply", because an entry that silently disappears leaves a developer with a missing menu item
and no stack trace, and swallowing the exception would also hide genuine failures in the
integration's own data access.

Breadcrumb resolution (`get_active_section()`) reads the menu's declared entries rather than the
per-request tree django-flex-menus builds from them, so which section a URL belongs to does not
depend on whether the current person can see that section's entry — the breadcrumb and the mobile
menu's button label name the section for everyone who reaches one of its pages, whether or not
their menu shows the entry that leads there.

Cards are unchanged. The overview page still decides which cards to render from
`app_is_installed()` alone, with no per-request check, so that half of this decision stays decided,
not built. It is roadmap item R3's own feature.

The goal is G6. The work is R2 in the roadmap, in the Essential phase.

## Revisit if

Per-request evaluation shows up as a measurable cost on Account Center page loads that caching
cannot absorb, or a pattern emerges where integrations consistently want the same visibility rule
and would be better served by declaring it once than by answering per request.
