# Progress — 012 shared entrance page

Append-only narrative of the run. The ledger (`feature-state.json`) is the machine truth;
this file is the human one.

## 2026-07-31 — S0 INTAKE

Grilled from issue #19. One question asked: what "configurable card size" means, and whether the
feature blocks on django-mvp growing a wider scale. Sam's ruling: land the shared page now, file
the gap upstream, adopt the wider scale later. Issue labelled `accepted`.

Filed django-mvp/django-mvp#126 (upstream component gap) and #20 (adoption here, deferred,
depends on 126).

## 2026-07-31 — S1 SPECIFY

`specs/012-shared-entrance-page/` created on branch `012-shared-entrance-page`. Three stories
(two developer, one end user — Article XIV satisfied), 14 FRs, 6 SCs, no unresolved markers. Five
ambiguities self-resolved and recorded in `decisions.md`.

## 2026-07-31 — S2 SETUP

Epic #19 promoted in place (retitled `FS-012:`, body grown, intake preserved). Story sub-issues
#21/#22/#23 created and linked. Draft PR #24 opened bot-authored, milestone v0.8.0, `Closes` block
covering all four issues. `check-issue-titles` green.

## 2026-07-31 — Spec gate: APPROVED

Approved by Sam in session. **Plan gate waived** at the same time — Sam's words: "skip the
planning gate. This is a relatively simple feature and I'm happy to review at the merge gate."
So S3 produces its artifacts and the run proceeds straight to S4 with no plan notification. Next
contact with Sam is the merge gate.

## 2026-07-31 — S3 PLAN

Plan authored. The load-bearing design question — how an extending template declares its card
width — was settled by experiment against the real template stack rather than by preference. Two
candidate mechanisms failed: a `{% block %}` inside a cotton attribute is bound without the child's
override applying (silently, which is the dangerous part), and a view-supplied context variable
would require overriding allauth's views. The mechanism that works, verified three levels deep, is
a block override wrapping a small composition component. Recorded as P1–P5 in `plan.md`.

15 tasks across 3 stories, task sub-issues #25–#39 attached. Ledger created and schema-valid.

US-1 and US-2 dispatch as one unit — they are the two halves of one move, and splitting them
across worktrees would only mean the second rebasing onto the first.

## 2026-07-31 — Correction: task issues deleted

S3 filed 15 task issues (#25–#39) per the then-current issue contract. Sam rejected it as tracker
noise and they were deleted (not closed — a closed issue still shows in search and milestone
views). Task issue references stripped from the ledger. The rule was fixed at source the same day
so no future run repeats it. See D6 in `decisions.md`.

The implementation run for US-1 was unaffected: Implementers hold no tokens and never touch the
issue tracker.

## 2026-07-31 — S4 IMPLEMENT

US-1 dispatched, stalled with no output after 33 minutes and was killed. T001's test file was
already on disk and failing for the right reason (`TemplateDoesNotExist: dac/entrance.html`), so
the re-dispatch resumed at T002 with T001 pinned read-only, plus a per-task progress line so a
working run can no longer be mistaken for a dead one. US-2 and US-3 ran clean.

Three verification tasks were answered without leaving a test behind, which is what the plan asked
for in each case. Their findings are recorded here, and the ledger's `evidence` for those tasks
points at this section:

- **T006** — the four anonymous allauth pages rendered through the real stack before and after the
  rewiring. Identical once HTML whitespace is collapsed; the only source differences are
  indentation and blank lines the browser discards.
- **T013** — the stylesheet was rebuilt, and a second build from the pre-change templates produced
  byte-identical output. The move reuses the same classes, so `dac/static/css/dac.css` is untouched.
- **T015** — login, signup and password reset screenshotted at both canonical viewports and read.

## 2026-07-31 — S5 CONVERGE, S6 REVIEW

Both stories' work merged onto the feature branch as one implementation commit plus a
documentation commit. Three reviewers ran against the diff: correctness, recorded standards, and
public prose. Four findings were real and are fixed on the branch:

1. The README described the width override without saying that `{% block content %}` has to move
   inside it. Followed literally it produced a template with the block declared twice, which
   Django rejects. Reworded, and `test_size_full_renders_wider_card` now asserts the content
   survives the override.
2. `test_messages_region_present` only checked that an empty toast container rendered, so it
   would have passed with the messages region broken. A second test queues a real message.
3. `test_core_entrance_templates_reference_no_integration` grepped the templates for integration
   names, which is a guardrail, not the claim. A new test renders the page with `dac.allauth`
   removed from `INSTALLED_APPS` — verified to bite, by confirming dac's own allauth templates
   become unreachable under the same fixture.
4. `CONTEXT.md` read "the core-owned page for pages shown to anonymous users" and drifted from
   "layout", the term its own heading uses. Rewritten, with the two files as a list.

One thing found and deliberately left alone: the committed `dac/static/css/dac.css` is unminified
and stale, while `npm run build:css` minifies. That predates this feature, and correcting it
rewrites a 7,000-line generated artifact inside a feature PR. Filed separately.

## 2026-07-31 — S7 PR_READY, corrections

Two conventions were corrected after the fact, both cases of following a written instruction past
the point where the repository's own history contradicted it:

- The PR carried a `[WIP]` prefix. Every merged feature PR in the family reads `FS-NNN: <title>`
  with no status marker. Retitled to match the epic exactly, and the prefix removed from the
  process docs so it cannot recur.
- The three story completion comments had never been posted, so `check-story-comments` was red.
  Written from the delivered work and posted before the merge gate.

Both machine gates are green. All seven required CI checks pass. The bot is author, committer and
last pusher, so the approval gate will clear.

## 2026-07-31 — Ledger repair

The ledger had been schema-invalid since S4, in two ways, and neither had been caught because
nothing re-validated it after the run wrote to it:

- A top-level `verification` block the schema does not permit. Its content already lived in this
  file, so it was removed rather than widening the schema to accept it. Fitting the rule to the
  mistake would have retired the guardrail.
- Every task was marked `done` with no `evidence`, which the schema requires precisely so that
  evidence rather than assertion advances the ledger. Evidence has been transcribed from what is
  actually on the branch and what was actually run — named tests for the twelve tasks that left a
  test behind, and a command plus a pointer to this file for the three that answered a question
  once.

Both were caught by validating before the merge gate. The checkpoint invariant says to validate
before *every* transition, which would have caught it at S5.
