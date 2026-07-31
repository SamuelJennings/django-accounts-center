# Decision record — 013 Account Center menu entries

Ambiguities resolved without escalating, and the maintainer rulings that shaped the spec. Each
entry states what was unclear, what was chosen, and why the choice is defensible.

**Where a decision lives.** The question and its answer belong in `spec.md`, under
`## Clarifications`, and the answer is integrated into the requirement, scenario or edge case it
affects — a specification has to be readable on its own. This file carries only the longer
reasoning that would bloat the spec if inlined. It is a companion to the Clarifications section,
never a substitute for it.

## Settled at intake with the maintainer

### D1 — Hiding is presentation only

**Ambiguous:** whether "this entry does not apply to you" also means the page behind it must
refuse you.

**Chosen:** presentation only. The entry disappears, the URL still resolves, and the view decides
who may open it.

**Why:** the maintainer's ruling — the package is UI presentation, and what a downstream view
does is the downstream author's responsibility. It also keeps a display hook from being mistaken
for access control by integration authors, which would be security by appearance.

### D2 — A section with no visible entries is the menu library's job

**Ambiguous:** whether this package must hide a section heading whose entries are all hidden, and
whether it should test that.

**Chosen:** django-flex-menus already does it (`flex_menu/menu.py:422` — a container with no URL
and no visible children sets `visible = False`). This package relies on it and does not test it.

**Why:** the maintainer's standing rule against duplicating tests across packages. FR-004 states
the behaviour the feature requires, and the tests this feature adds assert what this package
contributes rather than re-proving a dependency.

### D3 — Cards are out of scope

**Ambiguous:** ADR 0002 covers menu entries and overview cards together, so the feature could be
read as covering both.

**Chosen:** menu entries only. Cards are roadmap item R3 with their own feature.

**Why:** the maintainer's ruling at decomposition — R2 and R3 share a mechanism but were kept as
separate runs, and R2's design does not pre-plan for R3.

## Resolved without escalating

### D4 — The visibility check is optional, not mandatory

**Ambiguous:** whether every contributed entry must carry a visibility check, or whether silence is allowed.

**Chosen:** optional. An entry with no visibility check stays visible whenever its integration is
installed (FR-005).

**Why:** Article XV puts consumers and upgrades first, and making the answer mandatory would
break every entry `dac.allauth` contributes today for no gain. It also matches the underlying
menu library, whose visibility check defaults to true. Stated to the maintainer at intake exit
as a chosen default and not objected to.

### D5 — A failing visibility check surfaces rather than hides the entry

**Ambiguous:** what happens when an integration's visibility check raises.

**Chosen:** the error propagates. It is not caught and turned into "not visible".

**Why:** an entry that silently vanishes gives a developer no signal and no stack trace, and the
same bug would present as a UI mystery rather than an error. Swallowing exceptions to protect a
menu render also hides genuine failures in the integration's own data access. If a project later
wants resilience over visibility, that is a deliberate change with its own decision.

### D6 — The core Overview entry is never hidden

**Ambiguous:** whether the core package's own entry participates in the mechanism.

**Chosen:** it applies to every signed-in person and carries no visibility check.

**Why:** it is the Account Center's own landing page. Hiding it would leave a person on a page
with no way back to the top of the section they are in.

### D7 — No anonymous case

**Ambiguous:** what a visibility check should answer for a signed-out visitor.

**Chosen:** there is no such case to answer. The Account Center requires sign-in
(`AccountCenterView` uses `LoginRequiredMixin`), so entries are only ever resolved for a
signed-in person.

**Why:** specifying behaviour for a state the pages cannot be in would add a rule no test could
reach honestly.

### D8 — Proving the second integration does not wait on URL contribution

**Ambiguous:** US-3 asks that any integration can serve a management view through the shared
page, which could be read as also requiring the integration to be reachable without a core edit.

**Chosen:** US-3 covers the page and menu contract. Reachability without a core edit is roadmap
item R4 and stays out of scope.

**Why:** `dac/urls.py` still names each integration explicitly, and changing that is a separate
roadmap item with its own feature. Widening US-3 to cover it would take work R4 owns.

## Raised by the clarify coverage scan (2026-07-31)

Both were found by the taxonomy scan rather than while drafting, which is the argument for running
the scan at all — drafting only surfaces what the author already thought to question.

### D9 — A hidden entry must not degrade the page frame

**Ambiguous:** the spec said a page whose entry is hidden "behaves exactly as it did before", which
covered the view but said nothing about the page furniture around it.

**Chosen:** the page renders the same frame for everyone who reaches it, breadcrumbs included
(FR-006a, US-2 scenario 5).

**Why:** `get_active_section()` resolves the breadcrumb by walking the *processed* menu and keeping
leaves where `item.visible` is true. A check returning false removes the entry from that tree
entirely, so no section matches, the section crumb disappears and the mobile dropdown falls back to
its generic label. That is presentation leaking out of a feature whose whole premise is that hiding
is presentation-only and the page still works. Someone arriving from a deep link would get a
visibly degraded page for no stated reason.

This is a behaviour requirement, not a design: how breadcrumb resolution stops depending on
per-person visibility is planning work.

### D10 — "Visibility check" is the canonical term

**Ambiguous:** the draft called the same concept a per-request answer, a declaration, and something
an integration declares, across one document.

**Chosen:** **visibility check**, used everywhere, and added to CONTEXT.md (FR-011).

**Why:** CONTEXT.md exists to stop exactly this, and the word is already in the vocabulary — the
Integration entry frames installation against "whether it is shown", and ADR 0002 is titled
"Account Center visibility is resolved per request". The underlying menu library also calls the
predicate a check, so one term now spans docs, spec and code without translation.

## US0 — Foundational (Implementer, 2026-07-31)

### D11 — `gated` and `ungated` carry no `view_name`

**Ambiguous:** T002 asks for three entries (`gated`, `ungated`, `sectioned`); T003 asks for exactly
one management view. Whether the first two also needed their own page was not stated.

**Chosen:** `gated` and `ungated` are non-link leaf items — a label and, for `gated`, a check, and
nothing else. Only `sectioned` carries `view_name` and a real page. `MenuItem` explicitly supports
a leaf with neither URL nor children (flex_menu/menu.py's own docstring: "Non-clickable items
(headers, dividers)"), and mvp's sidebar item component already renders that case as a `<button>`
rather than an `<a>` (`href|yesno:"a,button"` in `cotton/menu/item.html`) — `MobileFooterMenu`'s
`sidebar_toggle` entry uses the same shape today.

**Why:** T003's brief is singular — "one management view" — and inventing a second and third page
to give `gated`/`ungated` a destination would be scope beyond what this task asked for, for a
question (does a gated entry need its own page?) that belongs to whichever later story needs it.
If US-2 (breadcrumb-survives-a-hidden-entry, T007) turns out to need `gated` to resolve to its own
page, that is that story's task to add — this entry is deliberately minimal.

**Revisit if:** a later story's test needs the `gated` entry to be a real destination rather than a
menu-presence demonstration.

**Superseded 2026-07-31 (US-2):** that revisit condition was met before US-2 was dispatched — T007
needs a page to open as the person the entry is hidden from. The orchestrator gave `gated` a
`view_name` (`testapp_gated`) and a sub-page at commit `6df57ac`. `ungated` still carries none.

### D12 — The visibility check reads group membership

**Ambiguous:** T002 leaves the check's mechanism to the implementer ("a callable reading an
attribute or group membership... keep it obvious").

**Chosen:** `request.user.groups.filter(name="testapp-gated").exists()`, with the group name as a
module-level constant (`GATED_GROUP_NAME`) that `tests/conftest.py`'s fixtures import rather than
duplicating the literal string.

**Why:** `django.contrib.auth`'s `Group` model is already installed and needs no new field on the
user model or a bespoke attribute, and "which group a person is in" is a realistic stand-in for the
billing/team-membership examples the spec itself uses.

**Revisit if:** a later story needs the check to depend on something other than group membership.

### D13 — `sectioned`'s `url_names` prefix is its own view name

**Ambiguous:** whether the declared prefix should include the sub-page URL name pattern only, or
also match the section's own page.

**Chosen:** `url_names=("testapp_settings",)`, matching `dac.allauth`'s existing convention (e.g.
`mfa_index` / `url_names=("mfa_",)`) — the prefix also matches the section's own page, which is
harmless because `get_active_section()` checks `item.selected` in an exact-match pass before it
ever consults `url_names`.

**Why:** consistency with the one existing integration's pattern, and it needed no third URL name
just to exclude the redundant self-match.

### D14 — The gated check tolerates a request with no `user` attribute

**Ambiguous:** none at design time — found by running the full suite after wiring the app in
(T004). `tests/test_components/test_dac_base.py`'s `cotton_render_string_soup` fixture renders
`dac/base.html` through a bare `RequestFactory` request with no `AuthenticationMiddleware` in the
chain, so `request` carries no `user` attribute at all — not even `AnonymousUser`. The
straightforward `request.user.groups...` raised `AttributeError` on every one of those tests, none
of which this story is allowed to touch.

**Chosen:** `_visible_to_gated_group` reads `getattr(request, "user", None)` and treats a missing
user as "does not apply" (`False`), before falling through to the real group-membership check.

**Why:** this is a rendering-harness artifact — the fixture is deliberately unauthenticated
(there is a sibling `cotton_render_string_soup_authenticated` fixture for tests that need
`request.user`) — not a case the Account Center's own requests can be in (D7: it is behind
`LoginRequiredMixin`, so `request.user` is always at least populated by
`AuthenticationMiddleware`). Handling a request with no `user` attribute at all is not the same as
swallowing a broken check (D5 still holds: a check that raises for a signed-in person's request
still propagates the error).

### D15 — `gated_client`/`ungated_client` use a fresh `Client()`, not the shared `client` fixture

**Ambiguous:** none at design time — found by smoke-testing the fixtures end-to-end before
committing T005 (not part of the story's own suite; this story writes no assertions). T005's brief
says to follow the existing `authenticated_client` style, which builds on pytest-django's `client`
fixture.

**Chosen:** both fixtures construct their own `django.test.Client()` instead of depending on the
shared `client` fixture.

**Why:** pytest caches a fixture's value per fixture *name* for the life of a test. `client` is
itself function-scoped, so a test requesting both `gated_client(client, ...)` and
`ungated_client(client, ...)` would receive the *same* `client` object from both — the second
`force_login()` call silently signs out the first person, and both "different" clients render the
menu for whichever person was logged in last. `authenticated_client` never hits this because no
test needs a second, independently-signed-in client alongside it; this story's whole point is a
test needing exactly that (US1's independent test: two people, one page, compared side by side).
Confirmed by a throwaway smoke test exercising both fixtures together against the real
`AccountCenterMenu` and `/account-center/` — not committed, since this story adds no assertions.

**Revisit if:** a later story's fixtures need cookie/session isolation beyond what a fresh
`Client()` gives for free.

### D16 — `tests/urls_minimal.py` mounts the test integration's own URLs

**Ambiguous:** T017's brief says to use "the existing minimal-URLconf pattern... exactly as
`tests/test_components/test_dac_base.py:180` does," but that file's `tests/urls_minimal.py` only
ever mounted `admin/` — no route the test integration's view could be reached through. Reusing the
file unmodified would 404 before the test could assert anything about the response.

**Chosen:** added one `path("test/testapp/", include("tests.testapp.urls"))` line to
`tests/urls_minimal.py` — the same mount `tests/urls.py` already uses — and nothing else. No
`dac.urls` route, so the file still carries no dac-owned URL at all, which is what the six
pre-existing `TestUserSidebarMenuIntegration` tests in `test_dac_base.py` depend on.

**Why:** the brief's instruction is "follow that file's *approach* … rather than inventing a new
isolation mechanism" — the approach is overriding `settings.ROOT_URLCONF` to a URLconf carrying no
dac route, not "never add a line to that file." Extending it purely additively keeps the one
isolation mechanism the suite already has, rather than adding a second, parallel "minimal-2"
module. Verified the pre-existing tests that use this file are unaffected: full suite green at 259
(D17 below covers the other surprise this uncovered).

**Revisit if:** a future story needs a URLconf with dac's own core route (`account-center`) but
not `dac.allauth`'s — `tests/urls_minimal.py` currently mounts neither.

### D17 — the breadcrumb root link renders a duplicated `href`

**Corrected after the story landed.** The original entry (kept below, struck through) concluded the
root crumb's `href` is never evaluated and "has never pointed anywhere". That is wrong, and the
correction matters because a future story would otherwise start from a false premise.

**What actually happens**, confirmed by rendering the test integration's page under both URLconfs:

- Under the normal URLconf the tag *is* evaluated. The markup is
  `<a href="/account-center/" href="/account-center/">Account Center</a>` — resolved correctly, but
  the attribute is emitted twice. Browsers honour the first, so the link works and the defect is
  invalid markup rather than a dead link.
- Under `tests/urls_minimal.py`, where the name cannot be reversed, the unresolved tag text leaks
  into the page as the attribute value instead of raising. That is the only condition under which
  the literal appears, and it is why the page did not 500.

**Cause**, and it is not in this package: `mvp/templates/cotton/breadcrumbs/item.html` renders
`<a href="{{ href }}" {{ attrs }}>` while its `<c-vars text class />` does not declare `href`, so
the attribute stays in the `attrs` passthrough and is written a second time verbatim. Every
breadcrumb link in every app using the component carries it. Filed upstream against `django-mvp`;
no change here, and nothing in this feature depends on it.

<del>

#### Original entry — `dac/base.html`'s breadcrumb root link never actually evaluates its `href`

**Found by:** designing T017. The concern going in was that opening the test integration's page
under a URLconf with no `account-center` route registered would 500 — `dac/base.html`'s breadcrumb
block unconditionally renders `<c-breadcrumbs.item … href="{% url 'account-center' %}" />`
whenever a section is active, and `{% url %}` normally raises `NoReverseMatch` when the name isn't
registered.

**What actually happens:** it doesn't raise. The rendered markup shows the literal string
`{% url 'account-center' %}` (once HTML-escaped, once not — two `href` attributes on the same
`<a>`) instead of a resolved path, on every page this template renders, `dac.allauth` installed or
not. django-cotton is not evaluating that `{% url %}` tag as a Django template tag inside the
component's attribute value. The root breadcrumb link has never pointed anywhere; this predates
this story.

**Not fixed here:** `dac/base.html` is off-limits for this story (the forbidden list), and this is
unrelated to FR-008. Reported as a concern in the completion report instead. Recorded here because
it's why T017's tests don't assert on the breadcrumb root crumb's `href` (D16's URLconf choice
turned out not to need working around it, but a test asserting the href resolved would have failed
for a reason this story has no mandate to fix).

**Revisit if:** a story touching `dac/base.html`'s breadcrumbs fixes the root crumb — worth adding
a regression test for the fix at that point.

</del>

## US-2 — The menu lists only what applies to me (Implementer, 2026-07-31)

### D18 — `_iter_leaves()` drops its `_processed_children` fallback entirely

**Ambiguous:** none at design time, but research.md R2 states "`_iter_leaves()` already falls back
to `node.children` when `_processed_children` is absent, so it works unchanged" when walking the
*declared* (unprocessed) `AccountCenterMenu` tree.

**Found:** that fallback never actually triggers on a raw node. `MenuItem.__init__`
(django-flex-menus, `flex_menu/menu.py:143`) sets `_processed_children = []` unconditionally, on
every instance, whether or not it has ever been processed — the attribute is never *absent*
(`getattr(..., None)` returns `[]`, not `None`), it is merely empty until `process()` populates it.
Checked directly against the raw tree (`poetry run python -c "..."`, not committed): every node's
`_processed_children` reads `[]`. The old `_iter_leaves()`'s `if children is None:` guard therefore
never falls through to `node.children` for a raw node — it would treat every group as a childless
leaf and yield the group itself, never descending to its actual entries.

**Chosen:** rewrote `_iter_leaves()` to walk `node.children` unconditionally, dropping the
`_processed_children` special case altogether. It is private, used nowhere but
`get_active_section()` (confirmed by `grep -rn "_iter_leaves"`), and `get_active_section()` no
longer processes the menu at all, so nothing needs the processed-tree branch any more.

**Why:** the function's one caller changed shape entirely (declared tree, not processed copy), and
carrying dead logic that silently mismatches its own docstring's claim is a worse hazard than
deleting it. Verified against both the raw tree (this function's new input) and by the full suite
staying green, including `tests/test_components/test_breadcrumbs.py` unmodified (T009).

**Revisit if:** a future caller needs to walk a *processed* tree's leaves again — that would need
the `_processed_children` branch back, written against the processed copy's actual behaviour
(populated only for nodes that had children, `[]` for processed leaves) rather than the mixed
raw/processed assumption this entry replaces.

### D19 — Menu-label extraction in tests excludes the mobile dropdown's toggle button

**Ambiguous:** none at design time — found while writing T011's page-comparison test.
`tests/test_menus.py`'s `_menu_labels()` helper (T010) collected every `<span>` inside
`<aside aria-label="Account navigation">`. On `testapp_gated`'s own page, that made the gated
entry look present for `ungated_client` too: the mobile dropdown's toggle button
(`dac/base.html`, `{% if section %}{{ section.label }}{% else %}...`) renders the *active
section's* label in its own `<span>`, and that button lives in the same `aside` as the actual menu
— this is T008's own fix working correctly (FR-006a: the button still names the section for the
person the entry is hidden from), not a menu-entry leak.

**Chosen:** `_menu_labels()` only counts `<span>` elements nested inside an `<li>` — every real
menu item and group heading renders inside one (`cotton/menu/item.html`, `cotton/menu/group.html`);
the dropdown's toggle button does not.

**Why:** confirmed by inspecting the parent chain of the false positive (`span.find_parent("li")`
was `None`; its ancestors were `button > div > aside`) before changing the helper, rather than
guessing at a fix. The `<li>` filter is exact rather than heuristic (e.g. excluding by class name),
so it does not need updating if the dropdown button's markup changes shape later.

**Revisit if:** mvp changes the menu item/group templates to render outside an `<li>`.

## US-1 — An integration says who each menu entry is for (Implementer, 2026-07-31)

### D20 — T013 overlaps T010's assertion, deliberately

> **Superseded at review (Forge, 2026-07-31) — see D21.** The reasoning below defends writing
> assertions that already exist elsewhere. Independent demonstrability is a property of the story,
> not a licence for a test that cannot fail alone.

~~**Ambiguous:** none at design time — noticed while writing T013.~~
~~`TestMenuDiffersByPerson` (T010, US-2) already asserts `"Gated" in gated_labels` and `"Gated" not~~
~~in ungated_labels` on the way to its own conclusion (the menus differ in exactly that one entry).~~
~~T013's brief (US-1) asks for exactly the same two facts, on their own.~~

~~**Chosen:** wrote `TestGatedEntryVisibilityCheck` as two focused tests — presence for the person~~
~~the entry applies to, absence for the person it does not — rather than treating T010 as already~~
~~satisfying T013 and skipping it.~~

~~**Why:** spec.md gives US-1 and US-2 separate Independent Tests on purpose — a developer's "I can~~
~~declare a check and it's asked per request" (FR-001, FR-002, FR-003) and an end user's "my menu~~
~~only lists what applies to me" are two different scenarios that happen to share a fixture and a~~
~~first assertion, not one test wearing two names. Each user story is independently testable and~~
~~independently demoable per spec-kit's own methodology; collapsing them into one test would make~~
~~US-1 undemonstrable on its own once US-2's assertion changed shape. This is not the cross-package~~
~~duplication the forbidden list rules out (D2, and tasks.md's "Not tested here") — both tests assert~~
~~this package's own contract, not flex-menus' internals, and neither re-derives the other's~~
~~conclusion (T010 additionally proves the set-difference is exactly `{"Gated"}`, which T013 does not~~
~~assert).~~

~~**Revisit if:** a future refactor of either story's tests wants to fold the shared premise into one~~
~~parametrized case — worth doing then, not speculatively now.~~

### D21 — T013 tests FR-002 directly instead of restating T010

**Ambiguous:** what T013 should assert, given T010 already covers presence-for-one-and-absence-for-
the-other. D20 answered "both, separately". That answer was wrong.

**Chosen:** `TestGatedEntryVisibilityCheck` holds one test — the same signed-in person, the same
session, reads a different menu once the fact their entry's check consults changes. The two
presence/absence assertions D20 added are gone; `TestMenuDiffersByPerson` (T010) keeps them.

**Why:** the two tests D20 defended were strict subsets of T010's assertions on the same fixtures,
so no bug could fail them without failing T010 first. A test with no independent failure it can
detect is maintenance cost with nothing bought. Story independence is satisfied by US-1 owning a
requirement of its own, not by re-asserting a neighbour's lines. FR-002 is that requirement — the
check is evaluated *per request* rather than once when the menu is built — and it was the one FR in
US-1's brief nothing asserted directly. `AccountCenterMenu` is assembled at import, so an answer
captured at import, at sign-in, or in any cache in between is a live failure mode this package owns;
T010's two-people comparison is only a proxy for it and passes against a per-user cache. Mutation-
checked: with the membership change removed, the test fails on the second assertion.

FR-001 and FR-005 remain covered by T014 (an entry declaring nothing stays visible for everyone) and
by the test integration itself, which cannot be constructed at all if an integration cannot attach a
check.

**Revisit if:** flex-menus grows a documented per-request caching layer — the test then needs to say
which cache boundary it is asserting across.
