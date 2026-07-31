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
