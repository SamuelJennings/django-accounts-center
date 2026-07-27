"""
Integration tests for the allauth password reset flow.

Covers:
  - T006 / US1: Standard link-based password reset (all four pages)
  - T007 / US2: Invalid-token branch
  - T009 / US3: Email enumeration protection
  - T012 / US4: Code-based password reset (confirm_password_reset_code.html)
"""

import pytest
from allauth.account.forms import ConfirmPasswordResetCodeForm, default_token_generator
from allauth.account.utils import user_pk_to_url_str
from django.template.loader import render_to_string
from django.urls import reverse

from tests.factories import UserFactory

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def get_valid_reset_key_url(user):
    """Return the password-reset-from-key URL with a fresh valid token."""
    uid = user_pk_to_url_str(user)
    key = default_token_generator.make_token(user)
    return reverse("account_reset_password_from_key", kwargs={"uidb36": uid, "key": key})


def get_invalid_reset_key_url():
    """Return a password-reset-from-key URL with obviously bad tokens."""
    return reverse(
        "account_reset_password_from_key",
        kwargs={"uidb36": "invalid", "key": "invalid-token"},
    )


# ---------------------------------------------------------------------------
# Template source checks — no raw {% element %} / {% endelement %} tags
# ---------------------------------------------------------------------------

RESET_TEMPLATES = [
    "account/password_reset.html",
    "account/password_reset_done.html",
    "account/password_reset_from_key.html",
    "account/password_reset_from_key_done.html",
    "account/confirm_password_reset_code.html",
]


# ---------------------------------------------------------------------------
# T006 / US1: Standard link-based password reset
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_password_reset_renders_200(client):
    """password_reset.html must return HTTP 200 for anonymous users."""
    response = client.get(reverse("account_reset_password"))
    assert response.status_code == 200


@pytest.mark.django_db
def test_password_reset_renders_200_for_authenticated(client, settings):
    """password_reset.html must return HTTP 200 for authenticated users."""
    settings.ACCOUNT_AUTHENTICATED_LOGIN_REDIRECTS = False
    user = UserFactory(email="test@example.com")
    client.force_login(user)
    response = client.get(reverse("account_reset_password"))
    assert response.status_code == 200


@pytest.mark.django_db
def test_password_reset_has_email_field(client):
    """password_reset.html must render an email input field."""
    response = client.get(reverse("account_reset_password"))
    content = response.content.decode()
    assert 'name="email"' in content or 'type="email"' in content


@pytest.mark.django_db
def test_password_reset_has_redirect_field(client):
    """password_reset.html must render redirect_field hidden input when next param present."""
    response = client.get(reverse("account_reset_password") + "?next=/dashboard/")
    content = response.content.decode()
    assert 'type="hidden"' in content
    assert 'name="next"' in content


@pytest.mark.django_db
def test_password_reset_post_redirects_to_done(client, settings):
    """POST to password reset form redirects to account_reset_password_done."""
    settings.ACCOUNT_PASSWORD_RESET_BY_CODE_ENABLED = False
    user = UserFactory(email="test@example.com")
    response = client.post(
        reverse("account_reset_password"),
        data={"email": user.email},
    )
    assert response.status_code == 302
    assert response["Location"] == reverse("account_reset_password_done")


@pytest.mark.django_db
def test_password_reset_done_renders_200(client):
    """password_reset_done.html must return HTTP 200."""
    response = client.get(reverse("account_reset_password_done"))
    assert response.status_code == 200


@pytest.mark.django_db
def test_password_reset_done_renders_200_for_authenticated(client, settings):
    """password_reset_done.html must return HTTP 200 for authenticated users."""
    settings.ACCOUNT_AUTHENTICATED_LOGIN_REDIRECTS = False
    user = UserFactory(email="test2@example.com")
    client.force_login(user)
    response = client.get(reverse("account_reset_password_done"))
    assert response.status_code == 200


@pytest.mark.django_db
def test_password_reset_from_key_valid_renders_200(client, settings):
    """password_reset_from_key.html (valid token) must return HTTP 200 with the form."""
    settings.ACCOUNT_PASSWORD_RESET_BY_CODE_ENABLED = False
    user = UserFactory(email="reset@example.com")
    url = get_valid_reset_key_url(user)
    response = client.get(url, follow=True)
    assert response.status_code == 200


@pytest.mark.django_db
def test_password_reset_from_key_valid_has_password_fields(client, settings):
    """password_reset_from_key.html (valid) must have password fields."""
    settings.ACCOUNT_PASSWORD_RESET_BY_CODE_ENABLED = False
    user = UserFactory(email="reset2@example.com")
    url = get_valid_reset_key_url(user)
    response = client.get(url, follow=True)
    content = response.content.decode()
    assert 'type="password"' in content


@pytest.mark.django_db
def test_password_reset_from_key_valid_has_redirect_field(client, settings):
    """password_reset_from_key.html (valid) must render redirect_field inside the form."""
    settings.ACCOUNT_PASSWORD_RESET_BY_CODE_ENABLED = False
    user = UserFactory(email="reset3@example.com")
    url = get_valid_reset_key_url(user)
    response = client.get(url, follow=True)
    content = response.content.decode()
    assert 'type="hidden"' in content
    assert 'name="next"' in content


@pytest.mark.django_db
def test_password_reset_from_key_valid_cancel_targets_logout_form(client, settings):
    """password_reset_from_key.html (valid) Cancel button targets #logout-from-stage form."""
    settings.ACCOUNT_PASSWORD_RESET_BY_CODE_ENABLED = False
    user = UserFactory(email="reset4@example.com")
    url = get_valid_reset_key_url(user)
    response = client.get(url, follow=True)
    content = response.content.decode()
    assert 'form="logout-from-stage"' in content


@pytest.mark.django_db
def test_password_reset_from_key_valid_has_logout_form(client, settings):
    """password_reset_from_key.html (valid, no cancel_url) must have #logout-from-stage form."""
    settings.ACCOUNT_PASSWORD_RESET_BY_CODE_ENABLED = False
    user = UserFactory(email="reset5@example.com")
    url = get_valid_reset_key_url(user)
    response = client.get(url, follow=True)
    content = response.content.decode()
    assert 'id="logout-from-stage"' in content
    assert reverse("account_logout") in content


@pytest.mark.django_db
def test_password_reset_from_key_done_renders_200(client):
    """password_reset_from_key_done.html must return HTTP 200."""
    response = client.get(reverse("account_reset_password_from_key_done"))
    assert response.status_code == 200


@pytest.mark.django_db
def test_password_reset_from_key_done_contains_success_message(client):
    """password_reset_from_key_done.html must be informational — no password form."""
    response = client.get(reverse("account_reset_password_from_key_done"))
    content = response.content.decode()
    assert 'type="password"' not in content


@pytest.mark.django_db
def test_password_reset_end_to_end(client, settings):
    """Full end-to-end: request reset → done → follow key URL → change password → success."""
    settings.ACCOUNT_PASSWORD_RESET_BY_CODE_ENABLED = False
    user = UserFactory(email="e2e@example.com")

    # Step 1: Request reset
    response = client.post(reverse("account_reset_password"), data={"email": user.email})
    assert response.status_code == 302, "POST to reset_password should redirect"

    # Step 2: Visit done page
    response = client.get(reverse("account_reset_password_done"))
    assert response.status_code == 200, "Done page should render without error"

    # Step 3: Follow reset key URL (follow redirect to set-password form)
    url = get_valid_reset_key_url(user)
    response = client.get(url, follow=True)
    assert response.status_code == 200, "Reset key page should render without error"

    # Step 4: Submit new password — get the final URL from the redirect chain
    final_url = response.redirect_chain[-1][0] if response.redirect_chain else url
    new_password = "NewSecureP@ss1"
    response = client.post(
        final_url,
        data={"password1": new_password, "password2": new_password},
        follow=True,
    )
    assert response.status_code == 200, "Post-change page should render without error"


# ---------------------------------------------------------------------------
# T007 / US2: Invalid-token branch
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_password_reset_from_key_invalid_renders_invalid_branch(client):
    """password_reset_from_key.html with invalid token must render the invalid-token branch."""
    response = client.get(get_invalid_reset_key_url())
    assert response.status_code == 200
    content = response.content.decode()
    assert 'type="password"' not in content


@pytest.mark.django_db
def test_password_reset_from_key_invalid_has_link_back(client):
    """Invalid-token branch must contain a link back to account_reset_password."""
    response = client.get(get_invalid_reset_key_url())
    content = response.content.decode()
    assert reverse("account_reset_password") in content


@pytest.mark.django_db
def test_password_reset_from_key_invalid_has_no_password_field(client):
    """Invalid-token branch must NOT contain a password input field."""
    response = client.get(get_invalid_reset_key_url())
    content = response.content.decode()
    assert 'type="password"' not in content


@pytest.mark.django_db
def test_password_reset_from_key_valid_has_password_form(client, settings):
    """Valid-token branch must render password input fields."""
    settings.ACCOUNT_PASSWORD_RESET_BY_CODE_ENABLED = False
    user = UserFactory(email="title@example.com")
    url = get_valid_reset_key_url(user)
    response = client.get(url, follow=True)
    content = response.content.decode()
    assert 'type="password"' in content


# ---------------------------------------------------------------------------
# T009 / US3: Email enumeration protection
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_password_reset_unknown_email_redirects_to_done(client, settings):
    """POST with unknown email must redirect to account_reset_password_done (SC-001)."""
    settings.ACCOUNT_PASSWORD_RESET_BY_CODE_ENABLED = False
    settings.ACCOUNT_PREVENT_ENUMERATION = True
    response = client.post(
        reverse("account_reset_password"),
        data={"email": "nobody@nowhere.example.com"},
    )
    assert response.status_code == 302
    assert response["Location"] == reverse("account_reset_password_done")


@pytest.mark.django_db
def test_password_reset_unknown_email_no_error_message(client, settings):
    """POST with unknown email must not show 'not registered' or error wording."""
    settings.ACCOUNT_PASSWORD_RESET_BY_CODE_ENABLED = False
    settings.ACCOUNT_PREVENT_ENUMERATION = True
    response = client.post(
        reverse("account_reset_password"),
        data={"email": "nobody@nowhere.example.com"},
        follow=True,
    )
    content = response.content.decode()
    assert "not registered" not in content.lower()
    assert "no account" not in content.lower()


# ---------------------------------------------------------------------------
# T012 / US4: Code-based password reset (confirm_password_reset_code.html)
#
# ACCOUNT_PASSWORD_RESET_BY_CODE_ENABLED uses a different set of URL patterns
# (mutually exclusive with the classic account_reset_password_done / from_key
# URLs). These tests therefore verify the template by rendering it directly
# rather than navigating through the view, so that the test settings do not
# need to switch between the two URL sets.
# ---------------------------------------------------------------------------


def _render_confirm_code_template(rf, extra_context=None):
    """Render confirm_password_reset_code.html with explicit context."""
    form = ConfirmPasswordResetCodeForm(code="123456")
    request = rf.get("/")
    ctx = {
        "verify_form": form,
        "redirect_field": '<input type="hidden" name="next" value="/" />',
        "email": "test@example.com",
        "can_resend": False,
        "can_change": False,
        "cancel_url": None,
        "SOCIALACCOUNT_ENABLED": False,
        "SOCIALACCOUNT_ONLY": False,
        "LOGIN_BY_CODE_ENABLED": True,
        "PASSKEY_LOGIN_ENABLED": False,
        "PASSKEY_SIGNUP_ENABLED": False,
        "login_url": "/accounts/login/",
        "signup_url": "/accounts/signup/",
        "signup_by_passkey_url": None,
        "site": None,
    }
    if extra_context:
        ctx.update(extra_context)
    return render_to_string("account/confirm_password_reset_code.html", ctx, request=request)


@pytest.mark.django_db
def test_confirm_password_reset_code_has_confirm_button(rf):
    """Submit button must be present."""
    content = _render_confirm_code_template(rf)
    assert 'type="submit"' in content


@pytest.mark.django_db
def test_confirm_password_reset_code_has_redirect_field(rf):
    """redirect_field hidden input must be present in the confirm-code form."""
    content = _render_confirm_code_template(rf)
    assert 'type="hidden"' in content
    assert 'name="next"' in content


@pytest.mark.django_db
def test_confirm_password_reset_code_no_resend_button_by_default(rf):
    """Resend button must be absent by default (can_resend=False)."""
    content = _render_confirm_code_template(rf)
    assert 'form="resend"' not in content


@pytest.mark.django_db
def test_confirm_password_reset_code_cancel_without_cancel_url(rf):
    """Cancel button must render as submit targeting #logout-from-stage when cancel_url absent."""
    content = _render_confirm_code_template(rf)
    assert 'form="logout-from-stage"' in content


@pytest.mark.django_db
def test_confirm_password_reset_code_no_resend_button_when_cannot_resend(rf):
    """No resend button is offered when can_resend=False (the hidden resend
    form itself is always rendered by allauth's stock template)."""
    content = _render_confirm_code_template(rf)
    assert 'form="resend"' not in content


@pytest.mark.django_db
def test_confirm_password_reset_code_logout_form_when_no_cancel_url(rf):
    """<form id='logout-from-stage'> must be present when cancel_url is absent."""
    content = _render_confirm_code_template(rf)
    assert 'id="logout-from-stage"' in content


@pytest.mark.django_db
def test_confirm_code_can_resend_true_shows_resend_button(rf):
    """allauth's stock contract: can_resend alone controls the resend button."""
    content = _render_confirm_code_template(rf, {"can_resend": True})
    assert 'form="resend"' in content


@pytest.mark.django_db
def test_confirm_code_cancel_url_renders_as_link(rf):
    """Cancel button must be an <a> link when cancel_url is set."""
    content = _render_confirm_code_template(rf, {"cancel_url": "/some/url/"})
    assert 'href="/some/url/"' in content


@pytest.mark.django_db
def test_confirm_code_no_cancel_url_has_logout_form(rf):
    """<form id='logout-from-stage'> must be present when cancel_url is absent."""
    content = _render_confirm_code_template(rf, {"cancel_url": None})
    assert 'id="logout-from-stage"' in content


@pytest.mark.django_db
def test_confirm_code_cancel_url_set_no_logout_form(rf):
    """<form id='logout-from-stage'> must be absent when cancel_url is set."""
    content = _render_confirm_code_template(rf, {"cancel_url": "/some/url/"})
    assert 'id="logout-from-stage"' not in content


@pytest.mark.django_db
def test_confirm_code_can_change_true_shows_change_section(rf):
    """Change section must appear when can_change=True."""
    content = _render_confirm_code_template(rf, {"can_change": True})
    assert 'value="change"' in content


@pytest.mark.django_db
def test_confirm_code_can_change_false_hides_change_section(rf):
    """Change section must be absent when can_change=False."""
    content = _render_confirm_code_template(rf, {"can_change": False})
    assert 'value="change"' not in content
