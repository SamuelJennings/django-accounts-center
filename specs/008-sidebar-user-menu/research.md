# Phase 0 Research: Sidebar User Menu Component

**Feature**: `008-sidebar-user-menu`
**Date**: 2026-05-18
**Status**: Complete — all unknowns resolved
**Refined**: 2026-05-18 — Research Task 3 (Avatar Rendering) updated to reflect zero-config implementation.

---

## Research Task 1: Bootstrap 5 Dropup via `<c-dropdown direction="up">`

**Unknown**: How does the `<c-dropdown>` component from django-cotton-bs5 produce a
dropup, and what does the trigger element require?

**Finding**:
The `cotton_bs5/templates/cotton/dropdown/index.html` template renders:

```html
<div class="{{ "drop"|add:direction }} {{ dropdown_class }}">
  {% if button %}{{ button }}{% else %}...{% endif %}
  <ul class="dropdown-menu" style="--bs-dropdown-min-width: {{ min_width }}">
    {{ slot }}
  </ul>
</div>
```

Passing `direction="up"` produces `<div class="dropup">`. Bootstrap 5 detects the
`dropup` class and opens the `.dropdown-menu` upward automatically. No additional CSS
or JS is required. The component also accepts:

- `min_width` — controls `--bs-dropdown-min-width` CSS variable (default `10rem`)
- `:ul="True"` / `:ul="False"` — renders `<ul>` or `<div>` for the menu container
- `dropdown_class` — extra classes on the outer wrapper div

**Decision**: Use `<c-dropdown direction="up">` to produce the dropup container.
Set `min_width` to `100%` to match the full width of the sidebar trigger.

**Custom trigger button**: The `<c-dropdown>` component supports a `button` named
slot. When content is passed via `<c-slot name="button">...</c-slot>`, the default
`<c-button>` trigger is replaced entirely. The custom button element MUST carry
`data-bs-toggle="dropdown"` and `aria-expanded="false"` for Bootstrap's dropdown JS
to activate.

---

## Research Task 2: Allauth Logout — POST Requirement and URL Name

**Unknown**: What is the allauth logout URL name, and does it require a POST?

**Finding**: Verified via `django.urls.reverse('account_logout')` in the example app:
the URL resolves to `/account-center/logout/` (confirming the URL name is
`account_logout`). Since allauth 0.56+, logout requires a POST request (CSRF-safe)
rather than a GET. A plain `<a>` tag cannot be used.

**Decision**: The logout menu item MUST be rendered as an HTML `<form method="post">`
with a CSRF token and a `<button type="submit">` inside a `<li>` element. The
`<c-dropdown.item>` component cannot wrap a form, so the logout item uses raw `<li>`
markup rather than the Cotton component:

```html
<li>
  {% url 'account_logout' as logout_url %}
  {% if logout_url %}
    <form method="post" action="{{ logout_url }}" class="d-block m-0">
      {% csrf_token %}
      <button type="submit"
              class="dropdown-item text-start w-100">Log out</button>
    </form>
  {% endif %}
</li>
```

---

## Research Task 3: Avatar Rendering

**Unknown**: Should the component generate a custom user avatar or delegate entirely
to the `<c-avatar>` component?

**Alternatives considered**:

| Approach | Assessment |
|---|---|
| Generate initials via template tag + conditional render | Adds a Python tag, a conditional branch, and fragile logic; inconsistent with component-reuse principle |
| Accept `initials` prop and render conditionally | Shifts implementation burden to every developer; still requires custom HTML |
| Accept `avatar_url` prop, pass to `<c-avatar src="...">` | Requires caller to supply URL; couples component to caller's user model structure |
| `<c-avatar size="sm" />` with no src, full delegation | Single render path; `<c-avatar>` uses its own `avatar_url` template tag to resolve the current user's photo; fallback SVG icon when no URL found; no avatar-related logic in `<c-dac.user-menu>` |

**Decision**: Use `<c-avatar size="sm" />` with **no `src` attribute**. The `<c-avatar>`
component uses its own `avatar_url` template tag to resolve the logged-in user's
photo URL from the request context. When no URL is found (user has no profile photo),
`<c-avatar>` renders its built-in SVG person icon. This approach:

1. Keeps `<c-dac.user-menu>` completely free of avatar-related configuration
2. Means the component passes no props related to avatars — all avatar behaviour is
   encapsulated in `<c-avatar>`
3. Developers who want to customise avatar rendering should override the `<c-avatar>`
   component template in their project (the correct Cotton/django-mvp extension point)

**Consequence**: The component template contains a single `<c-avatar size="sm" />` call
with no `src`. The component accepts no `avatar_url` or `avatar_size` props.

---

## Research Task 4: `<c-sidebar.footer>` Integration

**Unknown**: How is the sidebar footer structured in django-mvp? Where should the
`<c-dac.user-menu>` be placed?

**Finding**: `mvp/templates/cotton/sidebar/footer.html` renders:

```html
<c-vars class />
<c-mvp.toolbar :attrs="attrs" class="sidebar-footer px-3 {{ class }}">
  {{ slot }}
</c-mvp.toolbar>
```

A developer using the component places it in the sidebar footer slot:

```html
{% block app.sidebar.footer %}
  <c-sidebar.footer>
    <c-dac.user-menu />
  </c-sidebar.footer>
{% endblock %}
```

No props are required. `<c-dac.user-menu />` reads all user data from `request.user`
directly. The `<c-sidebar.footer>` provides consistent padding and the `sidebar-footer` class.

---

## Research Task 5: Graceful URL Degradation in Templates

**Unknown**: How to avoid `NoReverseMatch` exceptions when `account-center` or
`account_logout` URLs are not registered in the host application.

**Finding**: Django's template `{% url %}` tag supports an assignment form:
`{% url 'some-url' as url_var %}`. When the URL cannot be resolved, `url_var` is set
to an empty string rather than raising `NoReverseMatch`. This is the canonical Django
pattern for optional URL rendering.

**Decision**: The `account_logout` URL reference uses the assignment form:

```django
{% url 'account_logout' as logout_url %}
{% if logout_url %}
  <form method="post" id="logoutForm" action="{{ logout_url }}" class="d-block m-0">
    {% csrf_token %}
  </form>
{% endif %}
```

The `account-center` URL is resolved inline (no `as`); it is always present when
`dac.urls` is included. If not included, the template raises — which is the intended
behaviour since the component is part of the `dac` package.

---

## Research Task 6: Anonymous User Guard

**Unknown**: The component should not error or render for unauthenticated users.
How to handle this in a Cotton template?

**Finding**: `request.user` is available in all Django templates when
`django.contrib.auth.context_processors.auth` is in `TEMPLATES[...]['OPTIONS']['context_processors']`
(the default Django configuration). `request.user.is_authenticated` returns `False`
for anonymous users.

**Decision**: Wrap the entire component output in `{% if request.user.is_authenticated %}`.
If the user is not authenticated, the component renders nothing (no HTML output, no errors).

---

## Summary of Decisions

| Decision | Chosen Approach | Rationale |
|---|---|---|
| Dropup mechanism | `<c-dropdown direction="up">` | Native django-cotton-bs5 component; no custom CSS |
| Custom trigger | `<c-slot name="button">` with `<c-button>` | Allows arbitrary HTML trigger with full prop forwarding |
| Logout action | `<c-dropdown.item type="submit" form="logoutForm">` + hidden `<form id="logoutForm">` | POST required; button linked to form outside the `<ul>` |
| Avatar | `<c-avatar size="sm" />` — no `src` prop | Full delegation to `<c-avatar>` for URL resolution and fallback |
| User data | Read from `request.user` directly | Zero-config; no caller configuration required |
| Zero props | No `<c-vars>` declaration | Component is a self-contained drop-in; all behaviour fixed |
| Avatar rendering | Always `<c-avatar src="{{ avatar_url }}" size="{{ avatar_size }}" />` | Single render path; SVG icon fallback built into `<c-avatar>`; customisation via component override |
| URL degradation | `{% url '...' as var %}` assignment form | Django-native; suppresses `NoReverseMatch` |
| Anonymous guard | `{% if request.user.is_authenticated %}` | Standard Django pattern; renders nothing for anon users |
| Component placement | Inside `<c-sidebar.footer>` block override | Follows existing django-mvp sidebar footer convention |
