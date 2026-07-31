# Decision record — 013 Account Center menu entries

Ambiguities resolved without escalating, and the maintainer rulings that shaped the spec. Each
entry states what was unclear, what was chosen, and why the choice is defensible.

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

### D4 — Declaring is optional, not mandatory

**Ambiguous:** whether every contributed entry must answer, or whether silence is allowed.

**Chosen:** optional. An entry that declares nothing stays visible whenever its integration is
installed (FR-005).

**Why:** Article XV puts consumers and upgrades first, and making the answer mandatory would
break every entry `dac.allauth` contributes today for no gain. It also matches the underlying
menu library, whose visibility check defaults to true. Stated to the maintainer at intake exit
as a chosen default and not objected to.

### D5 — A failing answer surfaces rather than hides the entry

**Ambiguous:** what happens when an integration's answer raises.

**Chosen:** the error propagates. It is not caught and turned into "not visible".

**Why:** an entry that silently vanishes gives a developer no signal and no stack trace, and the
same bug would present as a UI mystery rather than an error. Swallowing exceptions to protect a
menu render also hides genuine failures in the integration's own data access. If a project later
wants resilience over visibility, that is a deliberate change with its own decision.

### D6 — The core Overview entry is never hidden

**Ambiguous:** whether the core package's own entry participates in the mechanism.

**Chosen:** it applies to every signed-in person and carries no declaration.

**Why:** it is the Account Center's own landing page. Hiding it would leave a person on a page
with no way back to the top of the section they are in.

### D7 — No anonymous case

**Ambiguous:** what a declaration should answer for a signed-out visitor.

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
