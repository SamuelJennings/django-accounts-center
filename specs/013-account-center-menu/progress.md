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
