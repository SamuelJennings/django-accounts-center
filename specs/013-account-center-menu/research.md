# Research — 013 Account Center menu entries

One open technical question, plus confirmation of what the dependency already provides.

## R1 — What django-flex-menus already does

**Question:** how much of FR-001 to FR-005 needs building?

**Finding: none of it.** Verified against the pinned source at
`/home/sam/projects/django-mvp/django-flex-menus`:

- `MenuItem.__init__` takes `check: Callable | bool = True` (`flex_menu/menu.py:92`), stored as
  `self._check`.
- `MenuItem.check(request, **kwargs)` calls it when callable and coerces the result to bool
  (`menu.py:351`).
- `MenuItem.process(request, **kwargs)` sets `processed.visible` from that check and returns early
  when false, so a failing item never reaches its children (`menu.py:384`).
- A parent keeps only children whose processed copy is visible (`menu.py:405`).
- A container with no URL and no visible children hides itself (`menu.py:422`) — the section-header
  behaviour, already provided.
- The renderer skips invisible items and walks `visible_children` (`flex_menu/renderers.py:149`,
  `:172`).
- `process_menu` caches one processed tree per menu per request, so a check runs once per request
  regardless of how many times the menu is rendered — and `dac/base.html` renders it twice, mobile
  and desktop.

**Consequence:** the visibility check is flex-menus' `check` argument. This package documents it as
the contract and adds no wrapper. An integration writes:

```python
MenuItem(name="billing", view_name="billing_overview", check=viewer_has_a_plan, ...)
```

**Not tested here.** Every bullet above is the dependency's own behaviour and is covered by the
dependency's suite (Sam's rule against cross-package test duplication).

## R2 — Making breadcrumb resolution independent of visibility — **SUPERSEDED 2026-07-31**

> The requirement this research served (FR-006a) was withdrawn by the maintainer before merge, and
> `get_active_section()` was restored to the implementation on `main`. Option C below was built and
> then reverted. The reasoning is kept because it is what surfaced the two upstream gaps now filed as
> django-flex-menus #34 and #35. See decisions.md D9.

**Question:** `get_active_section()` must name the current page's section even when the entry for
that section is hidden from the person viewing it (FR-006a). How?

**Why today's implementation cannot.** It calls `AccountCenterMenu.process(request)` and filters
leaves on `item.visible`. A hidden entry is not merely invisible in that tree — `process()` drops it
from its parent's children entirely, so there is nothing left to match against. Both resolution
paths then fail and the function returns `None`, which `dac/base.html` renders as no breadcrumb and
a dropdown button reading "Account Center".

**Options considered.**

| Option | Approach | Verdict |
|---|---|---|
| A | Process the menu with checks suppressed, for section resolution only | Rejected — flex-menus has no such flag, and adding one is an upstream change for a problem this package can solve locally |
| B | Walk the processed tree, then fall back to the raw tree when nothing matches | Rejected — two code paths that must agree, and the fallback is the *only* path exercised by the case that matters |
| C | Resolve the section from the raw menu tree, matching on URL name | **Chosen** |

**Chosen approach (C).** Section resolution answers "which section does the current URL belong
to?", which has nothing to do with who is looking. Resolve it from the declared menu, not the
rendered one:

- Walk `AccountCenterMenu`'s own children rather than a processed copy. `_iter_leaves()` already
  falls back to `node.children` when `_processed_children` is absent, so it works unchanged.
- Match the current page against each leaf on URL name, taken from `request.resolver_match`:
  - **The section page itself** — the item's `view_name` equals the current URL name. Use
    `resolver_match.view_name` when the item's `view_name` contains a namespace colon, otherwise
    `resolver_match.url_name`. This replaces today's path-comparison (`match_url()`), which needs a
    processed item and a resolved URL.
  - **A sub-page of the section** — the current URL name starts with one of the item's declared
    `url_names` prefixes. This path is unchanged in substance.
- Resolve the crumb's link with `reverse(item.view_name)` only when the crumb is a link (the
  sub-page case), guarded against `NoReverseMatch` so an unreachable entry degrades to no
  breadcrumb rather than a 500.

**Why this is better than a fix that preserves the current structure.** Matching on URL name is
what the sub-page path already does, so the two branches become one idea instead of two. It also
removes the function's dependence on processing the menu at all, which is the coupling that caused
the defect.

**Ordering caution for the implementer.** Today's code checks `selected` across all leaves before
checking any prefix. That ordering is load-bearing: `mfa_index` is a section root while `mfa_` is
another entry's prefix, so a prefix match must never win over an exact match. Keep the two passes
in that order.

**Overview entry.** Still excluded from section resolution by name, as today — it is the
breadcrumb's root, not a section.

## R3 — Where the test integration lives

**Question:** the spec needs a second integration (FR-008, and a second party for the per-person
tests). Ship it, or keep it in the suite?

**Finding: keep it in `tests/`.** Shipping a second integration inside `dac/` would mean choosing a
third-party package to integrate with, which is a product decision this feature has no mandate for
and which would carry a real dependency. A test-only app proves exactly the claim the spec makes:
that an app which is not `dac.allauth`, and which the core package knows nothing about, can
contribute gated entries and serve a page through `dac/base.html`.

Its URLs mount through `tests/urls.py`. Contributing URLs without a core edit is roadmap R4 (spec
assumption D8), so this proves the page and menu contract only, and the tests say so.

**Existing suite layout** puts app-scoped tests in `tests/test_allauth/`; the new app follows with
`tests/testapp/` for the app itself and top-level test modules for the assertions, matching Article
X's mirror-the-source-tree rule.
