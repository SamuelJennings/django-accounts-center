# Tasks — 013 Account Center menu entries

**Branch**: `013-account-center-menu` · **Spec**: [spec.md](spec.md) · **Plan**: [plan.md](plan.md)

Test-first throughout (Article I): each task's test is written and seen to fail before the change
that makes it pass. `[P]` marks tasks that may run in parallel with their siblings.

Stories, in dependency order: **Foundational → US-2 → US-1 → US-3 → US-4**. US-2 comes first among
the stories because it carries the only production code change, and US-1's assertions read more
honestly once the breadcrumb no longer depends on visibility.

---

## Phase 1 — Foundational (sequential, blocks every story)

The suite has one integration, so it cannot express "visible to one person, not another" without
inventing a second party. This phase builds that party.

- **T001** — Create the test integration app at `tests/testapp/`: `__init__.py`, `apps.py`
  (an `AppConfig` named `testapp`), and an empty `templates/testapp/` directory. It is a plain
  installed app, not a `dac.*` package, because the claim under test is that an app the core
  package knows nothing about can participate.
- **T002** — Add `tests/testapp/menus.py` contributing a `MenuGroup` to `AccountCenterMenu` with
  three entries:
  - `gated` — carries a visibility check that consults the requesting person (a callable reading
    an attribute or group membership, chosen by the implementer; keep it obvious).
  - `ungated` — carries no check at all, to hold FR-005 honest.
  - `sectioned` — declares `url_names` so breadcrumb resolution has a sub-page prefix to match.

  Labels use `gettext_lazy` (Article VIII). flex-menus autodiscovers `menus` modules from installed
  apps (`flex_menu/apps.py:9`), so no explicit import is needed.
- **T003** — Add `tests/testapp/views.py` and `templates/testapp/settings.html`: one management
  view whose template does nothing but `{% extends "dac/base.html" %}` and fill `{% block content %}`.
  It must reference no template belonging to any integration.
- **T004** — Register the app: add `"tests.testapp"` to `INSTALLED_APPS` in `tests/settings.py`,
  and mount its URLs in `tests/urls.py` under the test-only section, with a sub-page URL whose name
  matches the `sectioned` entry's declared prefix.
- **T005** — Add fixtures to `tests/conftest.py` for two signed-in people, one the gated entry
  applies to and one it does not. Reuse the existing `user` / `authenticated_client` style.
- **T006** — Confirm the existing suite is still green before any behaviour change
  (`kit/forge verify`). This is the baseline the rest of the work is measured against.

---

## Phase 2 — US-2 (P1): the menu lists only what applies to me · issue #44

> **T007 to T009 were reverted before merge.** FR-006a was withdrawn (decisions.md D9), so the
> breadcrumb tests are removed and `dac/menus.py` is restored to `main`. T010 to T012 stand.

**Independent test:** sign in as each of the two people and compare rendered menus and page frames.

- **T007** — Write the failing breadcrumb test in `tests/test_menus.py`: the person the gated entry
  does *not* apply to opens the gated entry's page directly, and the page must still render its
  section breadcrumb. **This must fail against the current implementation** — if it passes, the
  test is not reaching the defect and the task is not done. Assert on rendered markup (Article XII),
  not on `get_active_section()`'s return value alone.
- **T008** — Rewrite `get_active_section()` in `dac/menus.py` per research R2: resolve the section
  from `AccountCenterMenu`'s declared children rather than a processed copy, matching the current
  page on URL name.
  - Exact match first (`resolver_match.view_name` when the item's `view_name` is namespaced,
    otherwise `resolver_match.url_name`), then `url_names` prefix match. **The two passes must stay
    in that order** — `mfa_index` is a section root while `mfa_` is a prefix, so a prefix match
    winning over an exact match would misname the section.
  - Link the crumb with `reverse()`, guarded against `NoReverseMatch`, only where the crumb is a
    link.
  - Keep excluding the `overview` entry.
- **T009** — Confirm `tests/test_components/test_breadcrumbs.py` still passes unchanged. It covers
  the existing behaviour and must not be edited to accommodate the rewrite — if it fails, the
  rewrite is wrong. (Tamper guardrail: pre-existing tests are not modified.)
- **T010** [P] — Test that two people with the same installed apps get menus differing in exactly
  the gated entry, asserted on rendered markup.
- **T011** [P] — Test that the rest of the page is unaffected for the person the entry is hidden
  from: the other entries, the content region, and the messages region all render as before.
- **T012** — Confirm in a browser (Article XIII) that both people's Account Center renders
  correctly at desktop and mobile widths, including the mobile dropdown's button label on a page
  whose entry is hidden. Record what was checked in `progress.md`.

---

## Phase 3 — US-1 (P1): an integration says who each menu entry is for · issue #43

**Independent test:** render the Account Center as each person and assert which of the test
integration's entries are present.

- **T013** — Test that the gated entry is present for the person it applies to and absent for the
  person it does not, asserted on the rendered menu markup.
- **T014** [P] — Test that the ungated entry is present for both people (FR-005), so the optional
  half of the contract is held by a test rather than by intent.
- **T015** [P] — Test that `dac.allauth`'s own entries are unchanged for a signed-in person
  (FR-007). Assert the same entries render as before the feature.

**Not tested here** (Sam's cross-package rule, restated in plan.md): that `check` is called, that a
false result hides an item, that an empty group hides its heading. All of it is flex-menus'
behaviour, covered by flex-menus.

---

## Phase 4 — US-3 (P2): a second integration serves a page through the shared page · issue #45

- **T016** — Test in `tests/test_integration_contract.py` that the test integration's management
  view renders through `dac/base.html` carrying the sub menu, the breadcrumbs and its own content.
- **T017** [P] — Test the same page with `dac.allauth` absent, using the existing
  `tests/urls_minimal.py` pattern (`settings.ROOT_URLCONF` override, as
  `tests/test_components/test_dac_base.py:180` does), asserting it renders and references no
  template belonging to an integration.
- **T018** — Assert the core package was not edited to make this work: the test states in a comment
  that the app reaches the shared page purely by being installed and mounting its own URLs, and
  that URL contribution without a core edit is roadmap R4, out of scope here.

---

## Phase 5 — US-4 (P3): the recorded decision matches the built behaviour · issue #46

- **T019** — Update `docs/adr/0002-account-center-visibility-is-per-request.md`: status becomes
  implemented for menu entries, the roadmap reference changes from R6 to R2, and the **State**
  section is rewritten to describe what the code now does. Cards remain decided-and-not-built —
  say so explicitly rather than letting the ADR read as fully delivered.
- **T020** [P] — Add the **Visibility check** entry to `CONTEXT.md` (FR-011), defining it as an
  integration's per-request answer for one menu entry, and pointing at flex-menus' `check`. Update
  the existing **Integration** entry, which currently says the second half is "decided but not
  built".
- **T021** [P] — Update `docs/index.md`'s Integrations section with the contract an integration
  author needs: contribute entries from your own `menus.py`, pass `check=` for entries that apply
  to only some people, and understand that hiding is presentation only — your view still owns
  access.
- **T022** — Humanize every public markdown this feature touched (`kit/checklists/public-md.md`):
  the ADR, CONTEXT.md, docs/index.md, and the PR body. No internal handles.

---

## Phase 6 — Convergence

- **T023** — Full `kit/forge verify` plus `kit/forge tamper-check` across the whole feature diff.
- **T024** — Confirm no migrations were produced (`makemigrations --check`); this feature adds no
  models.
- **T025** — ADR graduation scan over `decisions.md`: D5 (a failing visibility check raises rather
  than hiding the entry) is the candidate — durable, cross-cutting, and non-obvious. Decide and
  record either way.

---

## Dependencies

- Phase 1 blocks everything.
- T008 depends on T007 existing and failing.
- T009 gates T008 — a green rewrite that breaks the existing breadcrumb tests is not done.
- Phases 3 and 4 depend on Phase 1 only, and may run alongside Phase 2 once T008 lands.
- Phase 5 depends on the behaviour being final.
- Phase 6 is last.

## Task-to-requirement map

| Requirement | Tasks |
|---|---|
| FR-001 | T002, T014 |
| FR-002 | T002, T013 |
| FR-003 | T010 |
| FR-004 | covered by the dependency; asserted incidentally by T010 |
| FR-005 | T002, T014 |
| FR-006 | T011 |
| ~~FR-006a~~ | withdrawn — T007 to T009 reverted |
| FR-007 | T015 |
| FR-008 | T003, T016, T017, T018 |
| FR-009 | T019 |
| FR-010 | T020, T021 |
| FR-011 | T020 |
