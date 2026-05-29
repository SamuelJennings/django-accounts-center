# Feature Specification: Base Management Page

**Feature Branch**: `005-base-management-page`
**Created**: 2026-05-12
**Status**: Draft

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Developer Extends Base to Build a Sub-Page (Priority: P1) **[Developer]**

A developer on the host project wants to create a new management sub-page (for example, a "Change Phone Number" page). They declare `{% extends "dac/base.html" %}`, override the `title` block with "Change Phone Number", append a breadcrumb item via `page.breadcrumbs`, and render their form inside `page.content`. Without writing any structural HTML they get: a sidebar loaded with the Account Center Menu, a breadcrumb trail rooted at "Account Center", a form-view layout matching the rest of the site, and their content spaced uniformly inside a card stack.

**Why this priority**: This is the primary consumer of the template. Every management sub-page in the package (email, password, phone, sessions) extends this base; it must be correct and complete before any sub-page can be implemented.

**Independent Test**: Can be tested by creating a minimal Django template that extends `dac/base.html` and overriding each block in isolation. The rendered output is fully testable without a database.

**Acceptance Scenarios**:

1. **Given** a template that extends `dac/base.html` and overrides `title` with "My Page", **When** the template is rendered, **Then** "My Page" appears in the toolbar title area.
2. **Given** a template that extends `dac/base.html` and appends a `page.breadcrumbs` item via `{{ block.super }}`, **When** rendered, **Then** the breadcrumb trail shows "Account Center → My Page".
3. **Given** a template that extends `dac/base.html` and places content in `page.content`, **When** rendered, **Then** that content appears inside the card stack layout.
4. **Given** a template that extends `dac/base.html` but overrides no blocks, **When** rendered, **Then** a placeholder "Coming soon…" message is shown in the content area.

---

### User Story 2 — Authenticated User Sees Consistent Management UI (Priority: P2) **[End User]**

A logged-in user navigates between different management pages (email management, password change, etc.). On every page they see the same Account Center sidebar menu, the same breadcrumb trail rooted at "Account Center", and the same visual layout with consistent spacing between page elements.

**Why this priority**: Visual consistency across management pages is the primary value proposition of a shared base template. A broken sidebar or missing breadcrumb degrades the user experience on every sub-page simultaneously.

**Independent Test**: Can be tested by rendering two different sub-pages that extend `dac/base.html` and asserting that both contain the Account Center Menu in the sidebar and the "Account Center" root breadcrumb.

**Acceptance Scenarios**:

1. **Given** any page extending `dac/base.html`, **When** rendered, **Then** the sidebar contains the Account Center Menu navigation.
2. **Given** any page extending `dac/base.html`, **When** rendered, **Then** a breadcrumb component is present and its first item links to the Account Center home page.
3. **Given** two different pages that each extend `dac/base.html`, **When** both are rendered, **Then** both share identical structural layout (sidebar, breadcrumbs, form-view container, card stack).

---

### User Story 3 — Developer Inspects Template Structure (Priority: P3) **[Developer]**

A developer new to the project opens `dac/base.html` and immediately understands which blocks are available for sub-pages to override, what each block's default content is, and how the template composes with the parent `base.html`.

**Why this priority**: Developer legibility and discoverability reduce integration errors and lower onboarding time. It is less critical than functional correctness but important for long-term maintainability.

**Independent Test**: Can be tested by reading the template source and verifying all required blocks are present, named consistently, and carry sensible defaults.

**Acceptance Scenarios**:

1. **Given** the template source, **When** a developer lists all `{% block %}` tags, **Then** the following blocks are present: `app.sidebar`, `content`, `breadcrumbs`, `page.breadcrumbs`, `page.content-wrapper`, `title`, `page.content`.
2. **Given** the template source, **When** a developer reads the `page.breadcrumbs` block default, **Then** it contains exactly one breadcrumb item pointing to the Account Center home URL.
3. **Given** the template source, **When** a developer reads the `page.content` block default, **Then** it shows a localised placeholder string (not an empty block).

---

### Edge Cases

- What happens when a sub-page does not override the `title` block? The toolbar title area renders empty — this is acceptable as it is the developer's responsibility to provide a title.
- What happens when a sub-page overrides the `page.breadcrumbs` block without calling `{{ block.super }}`? The "Account Center" root item is lost — this is a documented developer responsibility, not a template defect.
- What happens when the `account-center` URL is not registered (e.g. the app is not installed)? The breadcrumb `href` raises a `NoReverseMatch` at render time — the host project must install `dac` to use this template.
- What happens when a sub-page places content outside of `page.content`? They can override `page.content-wrapper` to take full control of the content region, at the cost of losing the `layouts.form-view` and `card.stack` defaults.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The base template MUST reside at `dac/base.html` so it can be referenced by `{% extends "dac/base.html" %}`.
- **FR-002**: The base template MUST extend the host project's `base.html`, inheriting all global layout blocks (head, navbar, footer, etc.).
- **FR-003**: The base template MUST override the `app.sidebar` block to inject the Account Center Menu using the project's sidebar component.
- **FR-004**: The base template MUST override the `content` block to provide the standardised management page structure.
- **FR-005**: Within the overridden `content` block, the template MUST include a `breadcrumbs` block containing a toolbar with a pre-configured breadcrumbs component.
- **FR-006**: Within the `breadcrumbs` breadcrumbs component, the template MUST provide a `page.breadcrumbs` block whose default content is a single breadcrumb item labelled "Account Center" that links to the account-center home URL.
- **FR-007**: The main content area MUST be wrapped in a `layouts.form-view` component to constrain its width and maintain visual consistency with standard django-mvp form pages.
- **FR-008**: Within the `layouts.form-view` component, the template MUST render a toolbar containing a `title` block, allowing sub-pages to declare their page title.
- **FR-009**: Below the title toolbar, all page content MUST be wrapped in a `card.stack` component to provide consistent vertical spacing between UI elements.
- **FR-010**: Within the `card.stack`, the template MUST expose a `page.content` block whose default content is a localised "Coming soon…" placeholder.
- **FR-011**: Sub-pages MUST NOT need to include any structural layout markup; all structural elements (sidebar injection, breadcrumbs, form-view container, card stack) are provided by the base template.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Every existing management sub-page (`account/email.html`, `account/password_change.html`, etc.) that extends this base renders with an identical top-level structure, verified by automated Cotton rendering tests.
- **SC-002**: A new management sub-page can be created by a developer using only `{% extends "dac/base.html" %}` and the minimum required block overrides (`title`, `page.breadcrumbs`, `page.content`), with zero additional structural markup.
- **SC-003**: The Account Center Menu appears in the sidebar on 100% of pages that extend `dac/base.html`, verified by automated tests that assert the menu component is present in rendered output.
- **SC-004**: The "Account Center" root breadcrumb linking to the account-center home is present on 100% of pages that extend `dac/base.html` without overriding `page.breadcrumbs`.

## Assumptions

- The host project's `base.html` exposes an `app.sidebar` block and a `content` block; both are required for `dac/base.html` to function correctly.
- The `account-center` URL name is registered by the host project; the root breadcrumb item's `href` depends on this.
- The `layouts.form-view`, `card.stack`, `breadcrumbs`, `breadcrumbs.item`, and `mvp.toolbar` Cotton components are all provided by `django-mvp` and are available in the host project's template environment.
- The Account Center Menu (`AccountCenterMenu`) is defined in `dac/menus.py` and registered with the menu system before the template is rendered.
- The `app.sidebar` Cotton component accepts a `menu` attribute that accepts a menu name string and renders that menu's items in the sidebar.
- Management pages are only accessed by authenticated users; the base template does not enforce authentication itself — sub-page views are responsible for access control.
- Internationalisation via `{% load i18n %}` and `{% trans %}` is available and required for all user-visible strings in the template.
