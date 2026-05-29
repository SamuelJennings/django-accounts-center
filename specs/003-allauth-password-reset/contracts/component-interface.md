# Component Interface Contract: Password Reset Flow

**Feature**: 003-allauth-password-reset
**Date**: 2026-05-11
**Propagated**: 2026-05-11 — Updated from spec.md refinement

---

## Component Dependency Graph

```
account/password_reset.html
  └─ <c-entrance title="Password Reset">
       ├─ {% include "account/snippets/already_logged_in.html" %} (conditional)
       ├─ <c-text center> description </c-text>
       ├─ <c-form action=reset_url>
       │    ├─ <c-form.render form=form />
       │    ├─ {{ redirect_field }}
       │    └─ <c-button.stack>
       │         └─ <c-button type="submit" icon="send" variant="primary">Send email</c-button>
       │    </c-button.stack>
       └─ <c-text small> contact-us </c-text>

account/password_reset_done.html
  └─ <c-entrance title="Password Reset">
       ├─ {% include "account/snippets/already_logged_in.html" %} (conditional)
       └─ <c-text center> spam-folder/contact confirmation </c-text>

account/password_reset_from_key.html
  └─ <c-entrance title="Bad Token" | "Change Password">
       ├─ [token_fail branch]
       │    └─ <c-text> {% blocktrans %} link to password_reset {% endblocktrans %} </c-text>
       └─ [valid branch]
            ├─ <c-form action=action_url>
            │    ├─ <c-form.render form=form />
            │    ├─ {{ redirect_field }}
            │    └─ <c-button.stack>
            │         ├─ <c-button type="submit" icon="submit" variant="primary">Confirm</c-button>
            │         └─ <c-button type="submit" form="logout-from-stage" icon="x-circle">Cancel</c-button>
            └─ <form id="logout-from-stage"> (when cancel_url absent)

account/password_reset_from_key_done.html
  └─ <c-entrance title="Change Password">
       └─ <c-text center> "Your password is now changed." </c-text>

account/base_confirm_code.html
  └─ <c-entrance>  [title from {% block title %}]
       ├─ <p> "We've sent a code to {{ recipient }}…"
       ├─ <c-form action={{ action_url }}>
       │    ├─ <c-form.render form=verify_form unlabeled=True />
       │    ├─ {{ redirect_field }}
       │    └─ <c-button.stack>
       │         ├─ <c-button type="submit" tags=submit_button_tags>Confirm</c-button>
       │         ├─ <c-button form="resend">Request new code</c-button>  (can_resend)
       │         └─ <c-button href=cancel_url | form="logout-from-stage">Cancel</c-button>
       ├─ <form id="resend" action={{ action_url }}> (always)
       ├─ <form id="logout-from-stage"> (cancel_url absent)
       └─ <details> change section (can_change)
            └─ <c-form>
                 ├─ <c-form.render form=change_form />
                 ├─ {{ redirect_field }}
                 └─ <c-button name="action" value="change" type="submit">Change</c-button>

account/confirm_password_reset_code.html
  └─ extends account/base_confirm_code.html (block overrides only)
       ├─ {% block title_ %} — "Enter Password Reset Code"
       ├─ {% block recipient %} — <a href="mailto:{{ email }}">{{ email }}</a>
       ├─ {% block action_url %} — fail-silent {% url ... as var %}{{ var }}
       └─ {% block action_url_resend %} — fail-silent {% url ... as var %}{{ var }}
```

---

## Components Used

All components are already available from specs 001 and 002. No new components are created.

| Component | Source | Usage |
|---|---|---|
| `<c-entrance>` | `dac/addons/allauth` (spec 001) | Outer shell for all 4 standard pages |
| `<c-text>` | `dac/addons/allauth` (spec 001) | Informational/descriptive paragraphs (replaces raw `<p>`) |
| `<c-form>` | django-mvp | Form wrapper with CSRF and action |
| `<c-form.render>` | django-mvp | Renders allauth form fields via crispy |
| `<c-button>` | django-cotton-bs5 | Submit and link buttons |
| `<c-button.stack>` | django-mvp | Vertical button group |

---

## Component Attributes: Key Usages

### `<c-text>`

```html
<!-- Description paragraph (password_reset.html) -->
<c-text center>
  {% trans "Forgotten your password? Enter your email address below…" %}
</c-text>

<!-- Contact-us paragraph (password_reset.html) -->
<c-text text="{% trans "Please contact us if you have any trouble resetting your password." %}"
                 small />

<!-- Confirmation paragraph (password_reset_done.html) -->
<c-text center>
  {% blocktrans %}We have sent you an email…{% endblocktrans %}
</c-text>

<!-- Success paragraph (password_reset_from_key_done.html) -->
<c-text center>
  {% trans 'Your password is now changed.' %}
</c-text>

<!-- Invalid-token error (password_reset_from_key.html) -->
<c-text>
  {% blocktrans %}The password reset link was invalid…{% endblocktrans %}
</c-text>
```

### `<c-form>`

```html
<!-- password_reset.html -->
{% url 'account_reset_password' as reset_url %}
<c-form method="post" action="{{ reset_url }}">
  {% csrf_token %}
  <c-form.render form=form />
  {{ redirect_field }}
  <c-button.stack>
    <c-button text="{% trans "Send email" %}"
              icon="send"
              size="lg"
              type="submit"
              variant="primary" />
  </c-button.stack>
</c-form>

<!-- password_reset_from_key.html (valid branch) -->
<c-form method="post" action="{{ action_url }}">
  {% csrf_token %}
  <c-form.render form=form />
  {{ redirect_field }}
  <c-button.stack>
    <c-button text="{% trans "Confirm" %}"
              icon="submit"
              size="lg"
              type="submit"
              variant="primary" />
    {% if cancel_url %}
      <c-button text="{% trans "Cancel" %}"
                href="{{ cancel_url }}"
                icon="x-circle"
                size="lg"
                class="border-secondary-subtle" />
    {% else %}
      <c-button text="{% trans "Cancel" %}"
                icon="x-circle"
                type="submit"
                form="logout-from-stage"
                size="lg"
                class="border-secondary-subtle" />
    {% endif %}
  </c-button.stack>
</c-form>
```

### Hidden form pattern (cancel / resend)

```html
<!-- Always present in base_confirm_code.html -->
<form id="resend" method="post" action="{{ action_url }}">
  <input type="hidden" name="action" value="resend" />
  {{ redirect_field }}
  {% csrf_token %}
</form>

<!-- Present when cancel_url is absent -->
{% if not cancel_url %}
<form id="logout-from-stage" method="post" action="{% url 'account_logout' %}">
  <input type="hidden" name="next" value="{% url 'account_login' %}" />
  {% csrf_token %}
</form>
{% endif %}
```

---

## Constraints

- `{% load socialaccount %}` MUST NOT appear in any of these templates (no social provider integration in the password-reset flow).
- `{{ redirect_field }}` MUST be rendered raw (not escaped) inside each form body.
- `<c-form.render form=verify_form />` MUST use the `unlabeled=True` attribute on `base_confirm_code.html` to match the allauth original's `unlabeled=True` on `{% element fields %}`.
- The `#resend` and `#logout-from-stage` forms are always rendered as `<form>` elements (not Cotton `<c-form>`), because they are hidden auxiliary forms that do not wrap visible fields.
