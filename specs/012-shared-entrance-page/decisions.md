# Decision record — 012 shared entrance page

Ambiguities resolved without escalating, and why each resolution is defensible. Recorded at S1;
appended to as later stages resolve more.

## D1 — The entrance page is a template extension point, not a view

**Ambiguous**: R1 says the page is "owned by the core app and reachable by any integration".
Reachable could mean a core-owned view and URL, or a template an integration extends.

**Chosen**: a template. The core app serves exactly one view today (the Account Center overview),
which is for signed-in people. It has no anonymous pages of its own and no reason to grow one, so
a core-owned entrance *view* would have no content to serve. Integrations keep their own views and
URLs and reach the shared page through their templates, which is how every other override point in
this package already works.

**Defensible because**: Article XV prefers template overrides and documented hooks to requiring a
consumer to subclass Python. Where anonymous pages sit in the URL space is explicitly R4's
question, so fixing a URL here would take a decision that belongs to a later feature.

## D2 — Card width is per page, chosen by the page author

**Ambiguous**: "the card should size itself to what a page needs" does not say who decides, or at
what granularity.

**Chosen**: the page author declares it, per page. Not a project-wide setting, not per request.

**Defensible because**: the driver is content volume — a one-field password reset against a signup
page with a provider list — and content volume is a property of the page, known when the page is
written. A project setting could not distinguish two pages, and a per-request decision would have
nothing to key on. Confirmed with Sam during grilling.

## D3 — The declarable widths are capped at what django-mvp expresses today

**Ambiguous**: R1 asks for a configurable card and says shortfalls in django-mvp's component are
raised there rather than worked around here. It does not say whether this feature waits.

**Chosen**: ship against the interim range, raise the gap upstream, adopt the wider scale later.
Filed as django-mvp/django-mvp#126 (upstream) and #20 (adoption here, deferred, depends on 126).

**Defensible because**: Sam's call during grilling. The value in R1 is the ownership move, and
holding G2 behind a change in another repo would delay the goal for a cosmetic axis. Article XVII
forbids the alternative — reproducing the card here or adding a stylesheet rule — outright.

## D4 — The logo, the stylesheet and the messages region move to the core page

**Ambiguous**: the current allauth entrance layout carries the site logo, the `dac.css` link and
the messages region. The spec has to say whether those belong to the shared page or stay with
each consumer.

**Chosen**: all three belong to the shared page.

**Defensible because**: each is chrome, not content. Leaving any of them to the consumer means
every future integration reproduces it, which is the duplication this feature exists to remove,
and a consumer that forgot the stylesheet would render unstyled. Making the logo configurable is
a separate want and is called out as out of scope.

## D5 — The default width is today's width

**Ambiguous**: whether the shared page's default should be the current fixed width or something
new.

**Chosen**: the current width, so a page that declares nothing renders exactly as it does now.

**Defensible because**: US-2 requires the allauth pages to come through the rewiring with
unchanged output. Any other default makes that story fail by construction, and Article XV asks for
default behaviour to stay stable across minor releases.

## D6 — Tasks get no issues *(correction, 2026-07-31)*

**What happened**: S3 filed one GitHub issue per task, #25 to #39, following
`kit/checklists/issue-contract.md`, which specified a `T###` sub-issue tier. Fifteen issues landed
on a tracker whose entire backlog was seven. Sam rejected it and they were deleted.

**Chosen**: the issue graph is Epic ← Story and stops there. The task list is `tasks.md` on the
branch plus `feature-state.json`. Where a human needs to see it, it goes as a comment on the story
issue or in the draft PR.

**Defensible because**: an issue records intent someone might act on or object to. A task records
how the machine decomposed work already agreed at the Spec gate, and putting it on the tracker
buries the real reports under bookkeeping. Deleted rather than closed — a closed issue still
occupies every search result and milestone view.

**Recorded at source** so it cannot recur: the contract, the issue-graph and pipeline references,
and the ledger schema were all amended the same day.
