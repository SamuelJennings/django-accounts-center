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
— see decisions.md D17: that `href` is never actually evaluated by django-cotton, on every page
this template renders, not just this one. Pre-existing, out of scope, reported as a concern.

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
