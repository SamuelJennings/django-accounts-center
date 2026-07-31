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
