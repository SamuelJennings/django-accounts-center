# Progress — 013 Account Center menu entries

## Spec gate — approved 2026-07-31

Sam approved the specification in session and waived the plan gate ("Approved, continue. Skip the
planning gate. Work through until you hit the PR merge gate."). The run is autonomous from here to
the merge gate: decisions inside the approved scope are self-resolved and recorded, not asked.

Approved artefacts: `spec.md` at 4fa40f5 (12 FRs, 4 stories, 2 clarifications integrated), epic #42,
stories #43–#46, draft PR #47.

## US0 — Foundational (Implementer)

### 2026-07-31 · Implementer US0 · T001

**Did:** Scaffolded `tests/testapp/` — `__init__.py`, `apps.py` (`TestappConfig`, app name
`tests.testapp`, label `testapp`), and an empty `templates/testapp/` directory (tracked with
`.gitkeep`). Not installed yet, so it has no effect on the suite.

**Verified:** `poetry run ruff check tests/testapp/` — all checks passed. `poetry run pytest -q` —
252 passed (baseline unchanged, app not yet in `INSTALLED_APPS`).

**Next:** T002 — contribute a gated `MenuGroup` from `tests/testapp/menus.py`.

**Watch:** nothing yet.

### 2026-07-31 · Implementer US0 · T002

**Did:** Added `tests/testapp/menus.py`, appending a `MenuGroup` ("Test App") to
`AccountCenterMenu` with three entries — `gated` (check reads membership in the
`testapp-gated` group), `ungated` (no `check` argument), `sectioned` (`view_name` +
`url_names=("testapp_settings",)`). All labels use `gettext_lazy`. See decisions.md D11–D13.

**Verified:** `poetry run ruff check tests/testapp/` and `poetry run mypy tests/testapp/` — both
clean. `poetry run pytest -q` — 252 passed (app still not in `INSTALLED_APPS`, so this module is
not yet imported).

**Next:** T003 — the test integration's management view and template.

**Watch:** `sectioned`'s `view_name="testapp_settings"` doesn't resolve to a real URL yet — that
lands in T003/T004. Harmless until the app is installed and the menu is actually rendered.

### 2026-07-31 · Implementer US0 · T003

**Did:** Added `tests/testapp/views.py` (`SettingsView`, a bare `LoginRequiredMixin` +
`TemplateView`) and `templates/testapp/settings.html`, which extends `dac/base.html` and fills
only `{% block content %}`. References no template belonging to any integration.

**Verified:** `poetry run ruff check tests/testapp/`, `poetry run djlint
tests/testapp/templates/testapp/settings.html`, `poetry run mypy tests/testapp/` — all clean.
`poetry run pytest -q` — 252 passed (still not installed).

**Next:** T004 — register the app and mount its URLs.

**Watch:** nothing new.

### 2026-07-31 · Implementer US0 · T004

**Did:** Added `tests/testapp/urls.py` (`testapp_settings`, `testapp_settings_sub` — the sub-page
matching `sectioned`'s `url_names` prefix). Added `"tests.testapp"` to `INSTALLED_APPS` in
`tests/settings.py` and mounted its URLs at `test/testapp/` in `tests/urls.py`'s test-only
section.

Wiring the app in surfaced a real bug in T002's check: `tests/test_components/test_dac_base.py`
renders `dac/base.html` through a bare `RequestFactory` request with no `user` attribute at all
(no `AuthenticationMiddleware`), and `_visible_to_gated_group` raised `AttributeError` on ten
pre-existing, off-limits tests. Fixed by reading `request.user` through `getattr(..., None)` — see
decisions.md D14.

**Verified:** `poetry run ruff check tests/`, `poetry run djlint tests/testapp/`, `poetry run mypy
tests/testapp/` — all clean. `poetry run pytest -q` — 252 passed, all pre-existing tests
(including `test_dac_base.py` and `test_breadcrumbs.py`) unmodified and green.

**Next:** T005 — fixtures for two signed-in people, gated and ungated.

**Watch:** any future check added to this test app should account for the same
no-`AuthenticationMiddleware` rendering path until dac/base.html tests move to
`cotton_render_string_soup_authenticated` or an equivalent.

### 2026-07-31 · Implementer US0 · T005

**Did:** Added `gated_person`/`gated_client` and `ungated_person`/`ungated_client` fixtures to
`tests/conftest.py` — the gated person is a member of `GATED_GROUP_NAME` (imported from
`tests.testapp.menus`), the ungated person is not.

Smoke-tested the fixtures end-to-end before committing (throwaway, not part of the suite — this
story writes no assertions): rendering `/account-center/` as `gated_client` showed "Gated" and
"Ungated"; as `ungated_client` showed only "Ungated"; `gated_client` at
`/test/testapp/settings/` rendered "Test App Settings". That surfaced a real bug — see decisions.md
D15 — `gated_client` and `ungated_client` initially shared pytest-django's `client` fixture, so
requesting both in one test silently collapsed them into the same signed-in person. Fixed with an
independent `Client()` per fixture, deviating from the brief's "reuse the `authenticated_client`
style" suggestion for a stated reason.

**Verified:** `poetry run ruff check tests/conftest.py`, `poetry run mypy tests/conftest.py` —
clean. `poetry run pytest -q` — 252 passed. Smoke test (not committed) confirmed both fixtures
work correctly together.

**Next:** T006 — confirm the full suite is green as the story's final checkpoint.

**Watch:** nothing new.

### 2026-07-31 · Implementer US0 · T006

**Did:** Final checkpoint for the story — confirmed the scaffold leaves the suite exactly where it
started.

**Verified:** `poetry run ruff check .` — all checks passed. `poetry run djlint .` — 36 files, 0
errors. `poetry run mypy .` — 2 pre-existing errors, both in files this story never touched
(`example/settings.py:97`, `tests/test_components/conftest.py:17`; confirmed via `git diff a38cbf3
--stat` against both showing no changes). `poetry run pytest -q` — **252 passed**, matching the
baseline in progress.md's spec-gate entry exactly. No new failures, no skips, no xfails.

**US0 done.** `tests/testapp/` exists as a plain installed app (not `dac.*`), contributing a
`MenuGroup` with a `check`-gated entry, a check-free entry, and a URL-backed sectioned entry with
`url_names`; a management view rendering through `dac/base.html`; and fixtures for two people the
gated entry does and does not apply to. No file under `dac/` was touched. No assertions about the
feature were written — that is later stories' job.

**Next:** US-2 (Phase 2, T007–T012) — the breadcrumb fix in `dac/menus.py` and its tests.

**Watch:** decisions.md D14/D15 are two real, non-obvious footguns for whoever writes US-1/US-2's
assertions: (1) any check added to this test app must tolerate a request with no `user` attribute
at all (dac/base.html's own structural tests render that way), and (2) `gated_client` and
`ungated_client` are independent `Client()` instances specifically so both can be signed in within
one test — don't "simplify" them back onto the shared `client` fixture.

### 2026-07-31 · Implementer US3 · T016

**Did:** Added `tests/test_integration_contract.py` with
`TestSecondIntegrationServesManagementPage`, asserting `authenticated_client.get(reverse
("testapp_settings"))` returns 200 and the response carries the Account Center sub menu (`aside`
with `aria-label="Account navigation"`, the "Test App" group, a link back to `account-center`),
the breadcrumbs region (`aria-label="Breadcrumbs"` with the current-page "Settings" crumb), and the
view's own content ("Test App Settings").

Confirmed each assertion fails for the right reason before it passed: mutated each expected string
in turn (e.g. `"Test App Settings"` → `"Test App Settings NOPE"`), watched the test fail on that
exact line, then reverted. All four assertions passed immediately once written — the scaffold from
US0 (T001–T006) already satisfies FR-008's first scenario, since nothing about serving this page
depends on the sub menu, breadcrumbs or content block knowing the requesting app is or isn't
`dac.allauth`. That is what this establishes: the existing shared-page contract already holds for
a second integration. It does not establish anything about `dac.allauth`'s *absence* — that's T017.

**Verified:** `poetry run ruff check .`, `poetry run djlint .`, `poetry run mypy .` — clean (2
pre-existing mypy errors, unrelated files, unchanged). `poetry run pytest -q` — 256 passed (252 +
4).

**Next:** T017 — the same page with `dac.allauth` absent.

**Watch:** nothing new.

### 2026-07-31 · Implementer US3 · T017

**Did:** Added `TestSecondIntegrationServesManagementPageWithoutAllauth` to
`tests/test_integration_contract.py`: with `settings.ROOT_URLCONF = "tests.urls_minimal"`, the same
page still returns 200, still shows "Test App Settings", and `response.templates` contains no
template name starting with `account/`, `allauth/` or `dac/allauth/`.

Extended `tests/urls_minimal.py` to mount `tests.testapp.urls` (decisions.md D16) — without it the
request 404s before the test can assert anything, since the file previously carried only `admin/`.
No `dac.urls` route was added, so the six pre-existing `TestUserSidebarMenuIntegration` tests in
`test_dac_base.py`, which depend on this file carrying no dac-owned URL name, are unaffected.

Ran the new tests against the *unmodified* `urls_minimal.py` first and watched all three fail with
`NoReverseMatch: Reverse for 'testapp_settings' not found` — confirming the failure was "route not
mounted," the thing the fix addresses, not something else. Added the mount, reran, all three
passed. Also mutation-tested `test_references_no_integration_template` by narrowing
`integration_prefixes` to a tuple that couldn't match anything real (`("dac/base.html",)` — a
template that legitimately is used) and confirmed it failed as expected, then reverted.

Going in, expected the page might 500 under a URLconf with no `account-center` route, since
`dac/base.html`'s breadcrumb block unconditionally builds `{% url 'account-center' %}`. It doesn't
— see decisions.md D17. (That entry's original conclusion was wrong and was corrected after this
story landed: the tag *is* evaluated under a normal URLconf, and the real defect is a duplicated
`href` attribute emitted by mvp's breadcrumbs component. Filed upstream as django-mvp/django-mvp#127.
Pre-existing, out of scope.)

Also tightened T016's `test_sub_menu_present`/`test_breadcrumbs_present`: the `href` assertion for
`account-center` moved out of the breadcrumbs test and into the sub-menu test, since D17 showed the
breadcrumb root crumb's own `href` never renders — the assertion was passing only because the sub
menu's overview link carries the same href elsewhere on the page. Keeping it under
`test_breadcrumbs_present` would have implied the breadcrumb link itself resolves, which it doesn't.

**Verified:** `poetry run ruff check .`, `poetry run djlint .`, `poetry run mypy .` — clean (same 2
pre-existing errors, unchanged). `poetry run pytest -q` — 259 passed (252 + 7).

**Next:** T018 — the module comment stating what these tests do and don't establish.

**Watch:** decisions.md D17 (the breadcrumb `href` bug) is worth a maintainer's attention outside
this story — it means the "Account Center" root crumb has never linked anywhere, on any page.

### 2026-07-31 · Implementer US3 · T018

**Did:** Added a module-level docstring paragraph to `tests/test_integration_contract.py` stating
what T016/T017 establish (the test integration reaches `dac/base.html` purely by being installed
and mounting its own URLs, no core-package edit) and what they don't (that URL contribution without
a core edit is possible — that's roadmap R4, out of scope here). No test code changed; this is
documentation only, verified by rerunning the full suite unchanged.

**Verified:** `poetry run ruff check .`, `poetry run djlint .`, `poetry run mypy .` — clean.
`poetry run pytest -q` — 259 passed, same as T017 (no assertions added).

**US-3 done.** FR-008 is proven end to end: a second integration (`tests/testapp`, not `dac.*`)
serves a management view through the shared `dac/base.html`, carrying the sub menu, the
breadcrumbs and its own content, both with `dac.allauth` present and with no dac-owned URL
registered at all. No file under `dac/` was touched.

**Next:** none — this story's tasks (T016–T018) are complete. US-4 (T019–T021, the ADR update) is
a separate story.

**Watch:** decisions.md D17 — the breadcrumb root crumb's dead `href` — is a real bug independent
of this story and worth a follow-up issue.

## US-2 — The menu lists only what applies to me (Implementer)

### 2026-07-31 · Implementer US-2 · T007

**Did:** Added `tests/test_menus.py` — `TestBreadcrumbSurvivesHiddenEntry`, two cases: the person
the `gated` entry does not apply to (`ungated_client`) requests the entry's own page
(`testapp_gated`) and its sub-page (`testapp_gated_sub`), asserting the response still carries the
section breadcrumb (`aria-label="Breadcrumbs"` and the section's label, "Gated"; the sub-page case
also asserts the crumb links back to `testapp_gated`).

**Confirmed failing against current `dac/menus.py`** (Article I red step) — both cases fail because
`get_active_section()` resolves the breadcrumb from the *processed* menu tree, which drops the
`gated` leaf entirely once its check returns `False`, so no section matches and no breadcrumb
renders at all:

```
tests/test_menus.py::TestBreadcrumbSurvivesHiddenEntry::test_section_page_breadcrumb_survives_hidden_entry FAILED
tests/test_menus.py::TestBreadcrumbSurvivesHiddenEntry::test_subpage_breadcrumb_survives_hidden_entry FAILED

    def test_section_page_breadcrumb_survives_hidden_entry(self, ungated_client):
        """The gated entry's own page still carries its section breadcrumb
        for the person the entry is hidden from."""
        response = ungated_client.get(reverse("testapp_gated"))
        content = response.content.decode()
>       assert 'aria-label="Breadcrumbs"' in content
E       assert 'aria-label="Breadcrumbs"' in '...<h1>Test App Settings</h1>...'
tests/test_menus.py:21: AssertionError

    def test_subpage_breadcrumb_survives_hidden_entry(self, ungated_client):
        response = ungated_client.get(reverse("testapp_gated_sub"))
        content = response.content.decode()
>       assert 'aria-label="Breadcrumbs"' in content
E       assert 'aria-label="Breadcrumbs"' in '...<h1>Test App Settings</h1>...'
tests/test_menus.py:29: AssertionError

2 failed, 252 passed in 37.65s
```

The page frame still renders (content, sidebar menu, messages region) — only the breadcrumb block
is silently empty, exactly the defect research.md R2 and decisions.md D9 describe.

**Verified:** `poetry run ruff check tests/test_menus.py` — clean. `poetry run djlint .` — 36
files, 0 errors. `poetry run mypy tests/test_menus.py` — no issues. `poetry run pytest -q` — **252
passed, 2 failed** (the two new tests above; baseline unchanged).

**Next:** T008 — rewrite `get_active_section()` per research.md R2 so these pass.

**Watch:** nothing new.

### 2026-07-31 · Implementer US-2 · T008

**Did:** Rewrote `get_active_section()` in `dac/menus.py` per research.md R2 (option C). It now
resolves the section from `AccountCenterMenu`'s *declared* children — walked with a simplified
`_iter_leaves()` that recurses on `node.children` unconditionally — instead of a processed copy,
matching the current page on URL name taken from `request.resolver_match`:

- **Exact match first, across every leaf**, before any prefix match is considered:
  `resolver_match.view_name` when the item's `view_name` contains a namespace colon, otherwise
  `resolver_match.url_name`. Kept as one complete pass over all leaves before the second pass
  starts — the ordering research.md flags as load-bearing (a section root's own name must never
  lose to another entry's `url_names` prefix).
- **Prefix match second**: `resolver_match.url_name` against each leaf's declared `url_names`.
  The crumb's link is resolved with `reverse(item.view_name)`, guarded against `NoReverseMatch` —
  an unreachable entry degrades the whole call to `None` (no breadcrumb) rather than a 500.
- The `overview` entry and any leaf with no `view_name` (the `ungated` entry, a non-link item) are
  excluded from the candidate list up front.

`_iter_leaves()` no longer special-cases `_processed_children`: that branch existed only to walk a
*processed* copy, which this function no longer touches, and `_processed_children` is never
actually absent on a raw node (`MenuItem.__init__` sets it to `[]`, not `None`) — checked against
the raw tree directly (`poetry run python` one-off, not committed) before relying on it, since
research.md's claim that the existing fallback "works unchanged" does not hold for the *unprocessed*
tree the rewrite needs to walk. See decisions.md D18.

**Verified:** `poetry run ruff check .` — all checks passed. `poetry run djlint .` — 36 files, 0
errors. `poetry run mypy .` — 2 pre-existing errors only (`example/settings.py:97`,
`tests/test_components/conftest.py:17`), unchanged from the US0 baseline; `dac/menus.py` itself
clean. `poetry run pytest -q` — **254 passed** (252 baseline + T007's two tests, both now green).

**Next:** T009 — confirm `tests/test_components/test_breadcrumbs.py` is unmodified and still green.

**Watch:** nothing new.

### 2026-07-31 · Implementer US-2 · T009

**Did:** Confirmed `tests/test_components/test_breadcrumbs.py` — the pre-existing suite covering
today's breadcrumb behaviour (section-page trail, sub-page link, overview has none) — passes
unmodified against the T008 rewrite. No edit made to the file (`git diff --stat` on it is empty).

**Verified:** `poetry run pytest tests/test_components/test_breadcrumbs.py -v` — 3 passed. Full
`poetry run pytest -q` — 254 passed, confirming the rewrite is not a checkpoint-local pass.

**Next:** T010 — the per-person menu-markup comparison test.

**Watch:** nothing new.

### 2026-07-31 · Implementer US-2 · T010

**Did:** Added `TestMenuDiffersByPerson` to `tests/test_menus.py`: `gated_client` and
`ungated_client` each request `/account-center/`, and a shared `_menu_labels()` helper parses each
response with `BeautifulSoup`, collecting the set of `<span>` texts inside
`<aside aria-label="Account navigation">` (both the mobile dropdown and the desktop card render
the same menu inside that one `aside`, per `dac/base.html`, so this counts each label once
regardless of which render site shows it — Article XII: asserted on rendered markup, not
`get_active_section()`'s return value). Asserts `"Gated"` is present for `gated_client`, absent for
`ungated_client`, and the set difference between the two menus is exactly `{"Gated"}` in both
directions — i.e. the menus differ in that one entry and nothing else.

**Verified:** `poetry run ruff check .` — all checks passed. `poetry run djlint .` — 36 files, 0
errors. `poetry run mypy tests/test_menus.py` — no issues. `poetry run pytest -q` — **255 passed**
(254 baseline + this test).

**Next:** T011 — confirm the rest of the page (other entries, content, messages) is unaffected for
the person the gated entry is hidden from.

**Watch:** nothing new.

### 2026-07-31 · Implementer US-2 · T011

**Did:** Added `TestPageUnaffectedByHiddenEntry` to `tests/test_menus.py`: `gated_client` and
`ungated_client` both request `testapp_gated` (the hidden entry's own page — FR-006), asserting the
menu entries other than `"Gated"` are identical between the two, the content region (`<h1>Test App
Settings</h1>`) is identical, and the messages region (the `<div class="toast …">` from
`dac/base.html`'s `<c-messages>`) is byte-identical between the two renders.

Writing this surfaced a real gap in T010's `_menu_labels()` helper: on this specific page, it
counted `ungated_client`'s response as showing `"Gated"`, which would have made this test wrongly
assert the menus are equal. The cause was the mobile dropdown's *toggle button* — which carries the
active section's label in its own `<span>` (`dac/base.html`'s `account_section` button, T008's own
fix, FR-006a) — living inside the same `<aside>` as the actual menu items. Confirmed by inspecting
the false positive's parent chain (`span.find_parent("li")` was `None`) rather than guessing.
Fixed `_menu_labels()` to only count `<span>`s nested in an `<li>`, which every real menu entry and
group heading is and the dropdown button is not. See decisions.md D19. Re-ran T010's test after the
fix — still green, confirming the helper's stricter filter doesn't change that test's outcome.

**Verified:** `poetry run ruff check .` — all checks passed. `poetry run djlint .` — 36 files, 0
errors. `poetry run mypy tests/test_menus.py` — no issues. `poetry run pytest tests/test_menus.py
-v` — 4 passed. Full `poetry run pytest -q` — **256 passed** (255 baseline + this test).

**US-2 done (T007–T011; T012's browser confirmation is the orchestrator's).** `get_active_section()`
now resolves the breadcrumb from `AccountCenterMenu`'s declared entries independent of any entry's
visibility, the pre-existing breadcrumb suite is untouched and green, and the per-person menu
rendering, page content and messages region are all covered by markup-level tests without
duplicating flex-menus' own test surface.

**Next:** T012 (orchestrator) — browser confirmation at desktop and mobile widths, including the
mobile dropdown button label on `testapp_gated`'s page for `ungated_client` (the exact case D17
surfaced) — that button should read "Gated", not fall back to "Account Center", which is the
visible proof that FR-006a holds.

**Watch:** the mobile dropdown toggle button and the real menu items share one `<aside>` — any
future test parsing that markup needs the same `<li>` filter D17 uses, not a blanket span scan.

## US-1 — An integration says who each menu entry is for (Implementer, 2026-07-31)

### 2026-07-31 · Implementer US-1 · T013

**Did:** Added `TestGatedEntryVisibilityCheck` to `tests/test_menus.py` — two cases, both against
`/account-center/`: `gated_client` sees `"Gated"` in the rendered menu, `ungated_client` does not.
Reused `_menu_labels()` (T010) rather than writing a second extractor, per the brief's scaffold
note. Left it in place in `tests/test_menus.py` rather than moving it — every task in this story
needed it, and no consumer outside this file exists yet.

Confirmed each assertion fails for the right reason before it passed: mutated the expected label
in each test in turn (`"Gated"` → `"Gated-NOPE"`, and inverted the negative assertion), watched
each fail on its own line, then reverted. Both passed immediately once written — the mechanism
(flex-menus' `check` argument, wired up in US0's `tests/testapp/menus.py`) already does this; this
story adds no code under `dac/` or `tests/testapp/`.

This overlaps `TestMenuDiffersByPerson` (T010, US-2), which already asserts the same two facts on
its way to a different conclusion. Recorded as a deliberate choice, not an oversight — see
decisions.md D20.

**Verified:** `poetry run ruff check .` — all checks passed. `poetry run djlint .` — 36 files, 0
errors. `poetry run mypy .` — 2 pre-existing errors only (`example/settings.py:97`,
`tests/test_components/conftest.py:17`), unchanged. `poetry run pytest -q` — **265 passed** (263
baseline + 2).

**Next:** T014 — the ungated entry stays visible for both people.

**Watch:** nothing new.

### 2026-07-31 · Implementer US-1 · T014

**Did:** Added `TestUngatedEntryStaysVisible` to `tests/test_menus.py`: both `gated_client` and
`ungated_client` see `"Ungated"` in the rendered menu at `/account-center/` (FR-005 — an entry
contributed with no visibility check stays visible regardless of who is looking). Reused
`_menu_labels()` again.

Confirmed failing for the right reason before passing: mutated the first assertion
(`"Ungated"` → `"Ungated-NOPE"`), watched it fail on that line, reverted. Passed immediately once
written, for the same reason as T013 — the `ungated` entry (no `check` argument) has worked this
way since US0.

**Verified:** `poetry run ruff check .` — all checks passed. `poetry run djlint .` — 36 files, 0
errors. `poetry run mypy .` — 2 pre-existing errors only, unchanged. `poetry run pytest -q` —
**266 passed** (265 + 1).

**Next:** T015 — `dac.allauth`'s own entries are unchanged.

**Watch:** nothing new.

### 2026-07-31 · Implementer US-1 · T015

**Did:** Added `TestAllauthEntriesUnchanged` to `tests/test_menus.py`: `authenticated_client` (a
plain signed-in person, not a member of the test app's gated group) requests `/account-center/`
and the rendered menu carries all five of `dac.allauth`'s labels — `"Email"`, `"Password"`,
`"Connected accounts"`, `"Two-factor authentication"`, `"Sessions"` — asserted individually
(`<=` on a set of literals) rather than as a substring check, so the test fails if the feature
changed any one of them (FR-007). All five appear because `tests/settings.py` installs
`allauth.socialaccount`, `allauth.mfa` and `allauth.usersessions`.

Confirmed failing for the right reason before passing: mutated one expected label
(`"Two-factor authentication"` → `"Two-factor authentication-NOPE"`), watched the assertion fail
listing that exact extra item, reverted. Passed immediately once written — `dac/allauth/menus.py`
contributes none of its entries with a `check`, so US-1's mechanism has nothing to act on here;
this test is a regression guard for FR-007, not a proof of new behaviour.

**Verified:** `poetry run ruff check .` — all checks passed. `poetry run djlint .` — 36 files, 0
errors. `poetry run mypy .` — 2 pre-existing errors only, unchanged. `poetry run pytest -q` —
**267 passed** (266 + 1).

**US-1 done (T013–T015).** No file under `dac/` or `tests/testapp/` was touched — every assertion
runs against the mechanism US0 already wired up. `tests/test_menus.py` now covers the full US-1
acceptance surface: a declared check is asked per person (T013), an absent check keeps an entry
visible (T014), and the one real integration in this repo is unaffected (T015).

**Next:** none — this story's tasks are complete. Convergence (Phase 6) is the orchestrator's.

**Watch:** nothing new.

### 2026-07-31 · Forge review of US-1

**Did:** Replaced T013's two tests with one that asserts FR-002 directly — the same signed-in
person, the same session, reads a different menu once the group membership their entry's check
consults changes. The pair it replaces (`"Gated"` present for `gated_client`, absent for
`ungated_client`) were strict subsets of `TestMenuDiffersByPerson`'s assertions on the same
fixtures, so nothing could fail them without failing T010 first. D20 defended that overlap on
story-independence grounds; D21 supersedes it and records why independence is owned by the
requirement, not by the assertion. T014 and T015 accepted unchanged.

**Verified:** mutation-checked the replacement — with the membership change removed, it fails on the
second assertion, which is the per-request evaluation the test exists to prove. `poetry run ruff
check .` clean, `poetry run djlint .` 36 files 0 errors, `poetry run mypy .` 2 pre-existing errors
only, `poetry run pytest -q` — **266 passed** (263 baseline + 3).

**Next:** merge US-1 onto the feature branch; US-4 outstanding.

**Watch:** T010 is now the sole holder of the presence/absence assertions. If US-2's test is ever
narrowed, US-1 loses that coverage silently.




