# Research: MFA Management Templates

**Feature**: 011-mfa-management-templates
**Status**: Complete — all unknowns resolved

## Summary

All core implementation patterns are established in prior specs (001–010). Six targeted
research areas were resolved: the allauth MFA context API, `<c-form.field>` textarea
limitation, `<c-form.card>` slot mechanics (confirmed by `password_change.html`),
WebAuthn JS preservation, Bootstrap table pattern, and screenshot naming for 11 states.

## Decisions

### Decision 1: Template inheritance fix strategy

**Decision**: Change only `mfa/base_manage.html` extends line to `dac/base.html`;
leave all sub-base templates (`mfa/totp/base.html`, `mfa/recovery_codes/base.html`,
`mfa/webauthn/base.html`) untouched.
**Rationale**: The single-point fix propagates the DAC layout to all nine content
templates without requiring sub-base changes. Minimises diff surface area per
Principle V. Identical approach to `account/base_manage.html` (spec 006),
`socialaccount/base_manage.html` (spec 009), and `usersessions/base_manage.html`
(spec 010).
**Alternatives considered**: Flatten all content templates to extend `dac/base.html`
directly — rejected as unnecessary when the base template fix achieves the same result.

### Decision 2: MFA context API — authenticators dict and configuration flags

**Decision**: Templates consume the following context variables, provided by allauth
MFA views without any Python changes:

- `authenticators` — dict keyed by type string: `authenticators.totp` (single instance
  or falsy), `authenticators.recovery_codes` (single instance or falsy),
  `authenticators.webauthn` (list, possibly empty)
- `MFA_SUPPORTED_TYPES` — list of enabled method strings (e.g., `["totp", "webauthn",
  "recovery_codes"]`)
- `is_mfa_enabled` — bool; True when the user has at least one active MFA method
- `MFA_RECOVERY_CODES_SHOW_ONCE` — bool; when True, the recovery codes view renders
  a "I have saved my recovery codes" checkbox
- `totp_svg_data_uri` — base64 SVG data URI for the QR code (activate_form.html)
- `form.secret` — TOTP secret string (activate_form.html)
- `unused_codes` — list of unused recovery code strings (recovery_codes/index.html)
- `total_count` — total recovery code count (recovery_codes/index.html)
- `unused_code_count` — count of existing unused codes (recovery_codes/generate.html)
- `authenticators` — list of WebAuthn `Authenticator` model instances
  (webauthn/authenticator_list.html)
- `authenticator` — single `Authenticator` instance (edit_form.html,
  authenticator_confirm_delete.html)
**Rationale**: Confirmed by inspection of the existing DAC MFA templates and allauth
MFA view source. No view overrides required.
**Alternatives considered**: None — this is the allauth public API.

### Decision 3: `<c-form.field type="textarea">` — component extended to support slot content

**Decision**: The recovery codes textarea in `mfa/recovery_codes/index.html` MUST be
rendered using `<c-form.field type="textarea">` with recovery code strings placed
in the default slot.
**Rationale**: The `<c-form.field>` component was extended to support a `type`
attribute with a `"textarea"` branch that renders a proper `<textarea>{{ slot }}</textarea>`
open/close pair (instead of a self-closing input). This allows pre-populated textarea
content via Django Cotton's default slot mechanism. Usage:

```django
<c-form.field type="textarea" id="recovery_codes" readonly
                  rows="{{ unused_codes|length }}" label="{% trans 'Unused codes' %}">
  {# djlint:off #}{% for code in unused_codes %}{% if forloop.counter0 %}
{% endif %}{{ code }}{% endfor %}{# djlint:on #}
</c-form.field>
```

**Implementation note — whitespace**: The component template places `{{ slot }}` on
its own indented line, adding a leading newline to the slot content. The
`{# djlint:off #}` guard around the codes loop prevents djlint from reformatting the
content, but implementers should verify the rendered textarea has no unwanted leading
blank line. The `id="recovery_codes"` hard dependency of `mfa/js/recovery_codes.js`
is preserved via `{{ attrs }}`.
**Alternatives considered**: Raw Bootstrap HTML `<textarea>` — superseded by the
component extension, which keeps the wrapper markup consistent with other form fields.

### Decision 4: `<c-form.card>` slot mechanics confirmed

**Decision**: `<c-form.card>` with `<c-slot name="actions">` places submit buttons
in the card-header toolbar (not the card body). Default slot content is rendered
inside the card body when `form-obj` is not passed (or is falsy).
**Rationale**: Confirmed by `account/password_change.html` which uses exactly this
pattern — `<c-form.card ... :form-obj="form">` with `<c-slot name="actions">`.
`<c-form.card>` passes undeclared attrs (including `title`) through to `<c-card :attrs="attrs">`,
so `<c-card>` renders the card-header toolbar when `title` is provided. `<c-form>` inside
`<c-form.card>` handles CSRF automatically for POST forms — no explicit `{% csrf_token %}`
is needed in template content.
**For templates with custom content** (TOTP activate form, WebAuthn add/edit):
do not pass `form-obj`; put content in the default slot. `<c-form.card>` renders
`{{ slot }}` (default) when `form_obj` is falsy.
**For simple no-visible-field forms** (deactivate, generate, remove):
pass `:form-obj="form"` with default `renderer="crispy"` to handle form rendering.
**Alternatives considered**: Manual `{% csrf_token %}` in every template — rejected;
`<c-form.card>` + `<c-form>` handle it automatically.

### Decision 5: WebAuthn JavaScript preservation

**Decision**: In `mfa/webauthn/add_form.html`, the following block MUST be preserved
verbatim after all element-tag replacements:

```html
{% include "mfa/webauthn/snippets/scripts.html" %}
{{ js_data|json_script:"js_data" }}
<script data-allauth-onload="allauth.webauthn.forms.addForm" type="application/json">
  {
    "ids": {
      "add": "mfa_webauthn_add",
      "passwordless": "{{ form.passwordless.auto_id }}",
      "credential": "{{ form.credential.auto_id }}",
      "data": "js_data"
    }
  }
</script>
```

The button that triggers credential creation MUST retain `id="mfa_webauthn_add"`.
**Rationale**: `mfa/webauthn/snippets/scripts.html` loads `webauthn-json.js`,
`webauthn.js`, and `account/js/onload.js`. The JSON script block supplies the
`allauth.webauthn.forms.addForm` onload handler with the DOM IDs it looks for.
Changing any ID would silently break the credential creation flow.
**Alternatives considered**: None — the JS is a hard constraint.

### Decision 6: Bootstrap table inside `<c-card>` (no `<c-table>` component)

**Decision**: `mfa/webauthn/authenticator_list.html` renders authenticators in a
raw Bootstrap `<table class="table">` placed directly inside a `<c-card>` default
slot. `<c-badge>` provides type indicators.
**Rationale**: No `<c-table>` component exists in django-mvp, django-cotton-bs5, or
DAC. Identical decision to spec 010 (usersessions). The WebAuthn key list is the only
table in the MFA addon; no reuse case justifies a custom component. Principle IX
one-off exemption applies.
**Alternatives considered**: Custom `<c-table>` component — rejected; same rationale
as spec 010.

### Decision 7: Screenshot naming (11 states)

**Decision**: 22 PNGs named as follows (one desktop + one mobile per state):

```
mfa-overview-active           # MFA overview: TOTP active + recovery codes set up
mfa-overview-inactive         # MFA overview: nothing active (fresh/inactive state)
mfa-totp-activate             # TOTP activate form (with QR code)
mfa-totp-deactivate           # TOTP deactivate confirmation
mfa-recovery-codes-view       # Recovery codes view (with codes)
mfa-recovery-codes-generate   # Recovery codes generate confirmation
mfa-webauthn-list             # WebAuthn key list with registered keys
mfa-webauthn-list-empty       # WebAuthn key list empty state
mfa-webauthn-add              # WebAuthn add security key form
mfa-webauthn-edit             # WebAuthn edit security key form
mfa-webauthn-remove           # WebAuthn remove security key confirmation
```

**Rationale**: Lowercase-kebab naming consistent with existing screenshot files
(e.g., `sessions-multiple.png`, `email-verified.png`). Prefixed with `mfa-` to
namespace all MFA screenshots at a glance in `docs/_static/`.
**Alternatives considered**: Prefixed with template path segment (e.g., `totp-activate`)
— rejected as less descriptive in the directory listing where context is lost.

## Prior Art (Established Patterns)

| Pattern | Established in |
|---|---|
| `{% extends "dac/base.html" %}` chain fix on base_manage | Spec 006 (`account/base_manage.html`) |
| `{% block title %}` for visible page heading | Spec 006 (`account/email.html`) |
| `{% block page.breadcrumbs %}` with `{{ block.super }}` + item | Spec 006 (`account/email.html`) |
| `{% block page.content %}` override | Spec 005 (`dac/base.html` contract) |
| `<c-badge variant="primary/secondary/warning">` | Spec 009 (`socialaccount/connections.html`) |
| `<c-button variant="danger">` for destructive actions | Spec 009 (`socialaccount/connections.html`) |
| `<c-card title="...">` + `<c-slot name="actions">` for overview panels | Spec 006 (`account/email.html`) |
| `<c-form.card>` + `<c-slot name="actions">` for form submit | Spec 007 (`account/password_change.html`) |
| Bootstrap table inside `<c-card>` (no `<c-table>`) | Spec 010 (`usersessions/usersession_list.html`) |
| Integration test pattern for allauth addon views | Spec 006 (`test_email_management_view.py`) |
| Screenshot test pattern (N states × 2 viewports: desktop + mobile) | Spec 006 (`test_email_management_screenshots.py`) |
| Raw HTML for one-off markup (Principle IX exemption) | Spec 010 (user-agent truncation) |
