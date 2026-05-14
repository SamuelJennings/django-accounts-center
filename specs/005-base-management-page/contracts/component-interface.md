# Component Interface Contract: `dac/base.html`

**Template path**: `dac/templates/dac/base.html`
**Parent**: `base.html` (host project root template)
**Role**: Base template for all authenticated management pages

---

## Block Contract

The following blocks are the public extension surface of `dac/base.html`.
Sub-page templates interact only with these blocks.

### `title`

- **Default**: *(empty)*
- **Type**: Inline text or translation string
- **Usage**: Rendered inside a `<c-mvp-toolbar>` as the page heading. Sub-pages MUST
  override this block to provide a localised page title.
- **Nesting**: Do NOT call `{{ block.super }}`. No parent content to preserve.

```django
{% block title %}{% trans "Change Password" %}{% endblock title %}
```

---

### `page.breadcrumbs`

- **Default**: Single `<c-breadcrumbs.item>` with text "Account Center" linking to
  the `account-center` URL.
- **Type**: One or more `<c-breadcrumbs.item>` components
- **Usage**: Sub-pages MUST call `{{ block.super }}` to preserve the root item, then
  append their own breadcrumb items.

```django
{% block page.breadcrumbs %}
  {{ block.super }}
  <c-breadcrumbs.item text="{% trans "Change Password" %}" />
{% endblock page.breadcrumbs %}
```

---

### `page.content`

- **Default**: `{% trans "Coming soon..." %}` placeholder string
- **Type**: Any Django template markup; typically Cotton form/card components
- **Usage**: Primary content area. All markup placed here is automatically wrapped in
  a `<c-card.stack>` for consistent vertical spacing.

```django
{% block page.content %}
  <c-form method="post">
    {% csrf_token %}
    {{ form|crispy }}
    <c-button type="submit" text="{% trans "Save" %}" />
  </c-form>
{% endblock page.content %}
```

---

### `page.header` *(advanced)*

- **Default**: `<c-mvp-toolbar fluid>` wrapping a `<c-breadcrumbs>` that contains
  the `page.breadcrumbs` block.
- **Usage**: Override only when the header structure itself must change (e.g., adding
  a search bar or action buttons to the toolbar). Most sub-pages should NOT override
  this block; use `page.breadcrumbs` instead.

---

### `page.content-wrapper` *(advanced)*

- **Default**: `<c-page.content class="container">` wrapping `<c-layouts.form-view>`
  which wraps the title toolbar and `<c-card.stack>` content area.
- **Usage**: Override only for non-form pages that need a full-width or custom layout.
  Overriding this block bypasses the `layouts.form-view` width constraint and the
  `card.stack` wrapper.

---

### `app.sidebar` *(reserved)*

- **Default**: `<c-app.sidebar menu="Account Center Menu" />`
- **Usage**: Do not override unless the sub-page requires a completely different
  sidebar menu. Overriding removes the Account Center Menu.

---

### `content` *(reserved)*

- **Default**: Full management page structure (page header + content wrapper)
- **Usage**: Do NOT override. Use `page.content` for content, `page.header` for header
  changes. Overriding `content` bypasses all management page structure.

---

## Component Composition

```
base.html
└── app.sidebar                   → <c-app.sidebar menu="Account Center Menu" />
└── content
    └── <c-page>
        └── page.header
            └── <c-mvp-toolbar fluid>
                └── <c-breadcrumbs>
                    └── page.breadcrumbs
                        └── <c-breadcrumbs.item text="Account Center" href="..." />
        └── page.content-wrapper
            └── <c-page.content class="container">
                └── <c-layouts.form-view>
                    └── <c-mvp-toolbar relaxed gap="3">
                        └── title  (sub-page title text)
                    └── <c-card.stack>
                        └── page.content  (sub-page content)
```
