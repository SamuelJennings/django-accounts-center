# Component Interface Contract: Email Verification Flow

**Feature**: 004-allauth-email-verification  
**Date**: 2026-05-11

---

## Component Dependency Graph

```
account/verification_sent.html
  └─ <c-entrance title="Verify Your Email Address">
       └─ <c-entrance.text center>
            {% blocktrans %}We have sent an email to you for verification...{% endblocktrans %}
          </c-entrance.text>

account/email_confirm.html
  └─ <c-entrance title="Confirm Email Address">
       ├─ [if confirmation and can_confirm]
       │    ├─ <c-entrance.text>
       │    │    {% blocktrans with email %}Please confirm that <a href="mailto:{{ email }}">{{ email }}</a> is an email address for user {{ user_display }}.{% endblocktrans %}
       │    │  </c-entrance.text>
       │    └─ <c-form method="post" action="{{ action_url }}">
       │         ├─ {% csrf_token %}
       │         ├─ {{ redirect_field }}
       │         └─ <c-button.stack>
       │              └─ <c-button type="submit" icon="check-circle" variant="primary">Confirm</c-button>
       │           </c-button.stack>
       │       </c-form>
       ├─ [elif confirmation and not can_confirm]
       │    └─ <c-entrance.text>
       │         {% blocktrans %}Unable to confirm {{ email }} because it is already confirmed by a different account.{% endblocktrans %}
       │       </c-entrance.text>
       └─ [else — no confirmation]
            └─ <c-entrance.text>
                 {% blocktrans %}This email confirmation link expired or is invalid. Please <a href="{{ email_url }}">issue a new email confirmation request</a>.{% endblocktrans %}
               </c-entrance.text>

account/confirm_email_verification_code.html
  └─ <c-allauth.confirm-code
          recipient="{{ email }}"
          action="{% url 'account_email_verification_sent' as u %}{{ u }}"
          resend-url="{% url 'account_email_verification_sent' as u %}{{ u }}"
          change-title="{% trans 'Use a different email address' %}"
          resend-supported />

account/account_inactive.html
  └─ <c-entrance title="Account Inactive">   [via account/base_entrance.html]
       └─ <c-entrance.text center>
            {% trans "This account is inactive." %}
          </c-entrance.text>
```

---

## Components Used

All components are already available from specs 001, 002, and 003. No new components
are created.

| Component | Source | Usage |
|---|---|---|
| `<c-entrance>` | `dac/addons/allauth` (spec 001) | Outer shell for all 4 pages |
| `<c-entrance.text>` | `dac/addons/allauth` (spec 001) | Informational/descriptive paragraphs |
| `<c-form>` | django-mvp | Form wrapper (email_confirm.html valid-key branch only) |
| `<c-button>` | django-cotton-bs5 | Submit button (email_confirm.html valid-key branch only) |
| `<c-button.stack>` | django-mvp | Button group (email_confirm.html valid-key branch only) |

---

## Component Attributes: Key Usages

### `<c-entrance.text>`

```html
<!-- verification_sent.html — centred informational paragraph -->
<c-entrance.text center>
  {% blocktrans %}We have sent an email to you for verification...{% endblocktrans %}
</c-entrance.text>

<!-- account_inactive.html — centred informational paragraph -->
<c-entrance.text center>
  {% trans "This account is inactive." %}
</c-entrance.text>

<!-- email_confirm.html — confirmation message (not centred; contains inline content) -->
<c-entrance.text>
  {% blocktrans with confirmation.email_address.email as email %}Please confirm that ...{% endblocktrans %}
</c-entrance.text>

<!-- email_confirm.html — invalid-key branch (not centred; contains inline link) -->
<c-entrance.text>
  {% blocktrans %}This email confirmation link expired or is invalid...{% endblocktrans %}
</c-entrance.text>
```

### `<c-button>` (email_confirm.html valid-key branch)

```html
<c-button.stack>
  <c-button type="submit"
            icon="check-circle"
            size="lg"
            variant="primary">
    {% trans "Confirm" %}
  </c-button>
</c-button.stack>
```

### `<c-form>` (email_confirm.html valid-key branch)

```html
{% url 'account_confirm_email' confirmation.key as action_url %}
<c-form method="post" action="{{ action_url }}">
  {% csrf_token %}
  {{ redirect_field }}
  <c-button.stack>
    ...
  </c-button.stack>
</c-form>
```

Note: No `<c-form.crispy>` is needed — there is no Django form object in this template;
only the CSRF token and redirect field are required inside the form.

---

## Constraints & Non-Negotiables

1. `confirm_email_verification_code.html` MUST use `<c-allauth.confirm-code>` and MUST
   declare `resend-supported` (email verification flow supports resend via quota).
2. `confirm_email_verification_code.html` uses fail-silent `{% url ... as u %}{{ u }}`
   patterns for `action` and `resend-url` so the template renders safely when
   `ACCOUNT_EMAIL_VERIFICATION_BY_CODE_ENABLED = False`.
3. `account_inactive.html` MUST extend `account/base_entrance.html`, NOT
   `allauth/layouts/entrance.html`.
4. All four templates MUST be free of `{% element %}` and `{% endelement %}` tags.
5. `<c-entrance.text>` without `center` modifier is used for paragraphs that contain
   inline links or user-specific content (email_confirm branches); `center` is used
   for purely informational messages.
6. The `resend-supported` attribute (on `<c-allauth.confirm-code>`) is a flow-level
   capability flag, separate from `can_resend` (view context, quota-based). When
   `resend-supported` is set and `can_resend=False`, the button is `disabled` — not
   hidden. When `resend-supported` is absent, no resend UI is rendered at all.
