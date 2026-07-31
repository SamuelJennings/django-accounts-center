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
