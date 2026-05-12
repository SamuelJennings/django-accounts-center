# Data Model: Base Management Page

No new models, fields, migrations, or database entities are introduced by this feature.

`dac/base.html` is a pure template artifact. All data it accesses comes from:

- The `AccountCenterMenu` object registered in `dac/menus.py` (read-only, no DB writes)
- The `account-center` URL reverse lookup (URL registry, no DB access)
- Child template context variables (provided by the sub-page's view)

**Entities referenced (read-only)**:

| Name | Source | Usage in template |
|---|---|---|
| `AccountCenterMenu` | `dac/menus.py` / `flex_menu` | Menu name string passed to `<c-app.sidebar menu="Account Center Menu" />` |
| `account-center` URL | `dac/urls.py` | Root breadcrumb href via `{% url "account-center" %}` |
