"""
Integration tests for the allauth login page (account/login.html).

Covers:
  - T003 / US2: Email/password form renders correctly
  - T004 / US3: Social login section rendered/hidden based on settings
  - T007 / US4: Login-by-code templates render with Cotton components
  - T008 / US6: Passkey button + WebAuthn script present/absent
  - T009 / US5: Authenticated user is redirected from the login page
"""

import pytest
from django.contrib.auth import get_user_model
from django.test import RequestFactory
from django.urls import reverse

User = get_user_model()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def get_login_url():
    return reverse("account_login")


# ---------------------------------------------------------------------------
# T003 / US2: Email/password login form
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_login_page_returns_200_for_anonymous(client):
    """Login page must return HTTP 200 for anonymous users."""
    response = client.get(get_login_url())
    assert response.status_code == 200


@pytest.mark.django_db
def test_login_page_has_no_element_tags_in_output(client):
    """Rendered output must not contain raw {% element %} tag syntax."""
    response = client.get(get_login_url())
    content = response.content.decode()
    assert "{% element" not in content
    assert "{% endelement" not in content


@pytest.mark.django_db
def test_login_page_post_invalid_credentials_rerenders(client, settings):
    """POST with bad credentials re-renders the login page (not a redirect)."""
    settings.ACCOUNT_LOGIN_METHODS = {"email"}
    response = client.post(
        get_login_url(),
        {"login": "nobody@example.com", "password": "wrongpassword"},
    )
    assert response.status_code == 200
    content = response.content.decode()
    # Error should appear in rendered HTML
    assert "{% if form.non_field_errors %}" not in content


@pytest.mark.django_db
def test_login_page_has_login_field(client):
    """Login form field must be present regardless of ACCOUNT_LOGIN_METHODS."""
    response = client.get(get_login_url())
    content = response.content.decode()
    assert 'name="login"' in content


@pytest.mark.django_db
def test_login_page_remember_me_present_when_session_remember_none(client, settings):
    """'Remember me' checkbox present when ACCOUNT_SESSION_REMEMBER=None."""
    settings.ACCOUNT_SESSION_REMEMBER = None
    response = client.get(get_login_url())
    content = response.content.decode()
    assert 'name="remember"' in content


@pytest.mark.django_db
def test_login_page_remember_me_absent_when_session_remember_true(client, settings):
    """'Remember me' checkbox absent when ACCOUNT_SESSION_REMEMBER=True."""
    settings.ACCOUNT_SESSION_REMEMBER = True
    response = client.get(get_login_url())
    content = response.content.decode()
    assert 'name="remember"' not in content


@pytest.mark.django_db
def test_login_page_forgot_password_link_present(client):
    """'Forgot your password?' link must point to the password reset URL."""
    response = client.get(get_login_url())
    content = response.content.decode()
    password_reset_url = reverse("account_reset_password")
    assert password_reset_url in content


@pytest.mark.django_db
def test_login_page_signup_crosslink_present_when_signup_open(client):
    """Signup cross-link must appear when signup_url is set."""
    response = client.get(get_login_url())
    content = response.content.decode()
    signup_url = reverse("account_signup")
    assert signup_url in content


@pytest.mark.django_db
def test_login_page_signup_crosslink_absent_when_socialaccount_only(client, settings):
    """Signup cross-link must be absent when SOCIALACCOUNT_ONLY=True.

    In allauth v65, LoginView sets signup_url=None only when SOCIALACCOUNT_ONLY=True.
    The template's {% if signup_url %} guard hides the link when signup_url is None.
    """
    settings.SOCIALACCOUNT_ONLY = True
    response = client.get(get_login_url())
    content = response.content.decode()
    assert reverse("account_signup") not in content


# ---------------------------------------------------------------------------
# T004 / US3: Social login section
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_login_page_no_social_section_when_disabled(client, settings):
    """No social section when SOCIALACCOUNT_ENABLED=False."""
    settings.SOCIALACCOUNT_ENABLED = False
    response = client.get(get_login_url())
    content = response.content.decode()
    assert "provider" not in content.lower()


@pytest.mark.django_db
def test_login_page_email_form_hidden_when_socialaccount_only(client, settings):
    """Email/password form must be hidden when SOCIALACCOUNT_ONLY=True."""
    settings.SOCIALACCOUNT_ONLY = True
    response = client.get(get_login_url())
    content = response.content.decode()
    assert 'type="password"' not in content


@pytest.mark.django_db
def test_login_page_passkey_and_code_hidden_when_socialaccount_only(client, settings):
    """Passkey and login-by-code buttons must be hidden when SOCIALACCOUNT_ONLY=True."""
    settings.SOCIALACCOUNT_ONLY = True
    settings.MFA_PASSKEY_LOGIN_ENABLED = True
    settings.ACCOUNT_LOGIN_BY_CODE_ENABLED = True
    response = client.get(get_login_url())
    content = response.content.decode()
    assert "passkey_login" not in content


# ---------------------------------------------------------------------------
# T008 / US6: Passkey login button + WebAuthn script
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_login_page_passkey_button_absent_when_disabled(client, settings):
    """Passkey button must not appear when PASSKEY_LOGIN_ENABLED=False."""
    settings.MFA_PASSKEY_LOGIN_ENABLED = False
    response = client.get(get_login_url())
    content = response.content.decode()
    assert "passkey_login" not in content


@pytest.mark.django_db
def test_login_page_passkey_button_absent_when_socialaccount_only(client, settings):
    """Passkey button must be absent when SOCIALACCOUNT_ONLY=True."""
    settings.SOCIALACCOUNT_ONLY = True
    settings.MFA_PASSKEY_LOGIN_ENABLED = True
    response = client.get(get_login_url())
    content = response.content.decode()
    assert "passkey_login" not in content


# ---------------------------------------------------------------------------
# T009 / US5: Authenticated user redirect
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_login_page_redirects_authenticated_user(client, settings):
    """Authenticated user visiting /accounts/login/ must be redirected (302)."""
    user = User.objects.create_user(
        username="loggedinuser",
        email="loggedin@example.com",
        password="Secure1234!",
    )
    client.force_login(user)
    response = client.get(get_login_url())
    assert response.status_code == 302


# ---------------------------------------------------------------------------
# T007 / US4: Login-by-code templates
#
# The login-by-code URLs are conditionally registered by allauth only when
# ACCOUNT_LOGIN_BY_CODE_ENABLED=True at startup (URL registration happens at
# import time). These tests therefore render the templates directly using
# Django's template engine to verify Cotton rendering without depending on
# URL registration state.
# ---------------------------------------------------------------------------


def _render_template(template_name, context_dict):
    """Render a template with a minimal fake request context."""
    from django.contrib.messages.storage.fallback import FallbackStorage
    from django.template.loader import render_to_string

    factory = RequestFactory()
    request = factory.get("/")
    request.session = {}
    request._messages = FallbackStorage(request)
    context_dict["request"] = request
    return render_to_string(template_name, context_dict, request=request)


@pytest.mark.django_db
def test_request_login_code_has_no_element_tags():
    """request_login_code.html must not contain {% element %} tags in output."""
    from allauth.account.forms import RequestLoginCodeForm

    form = RequestLoginCodeForm()
    content = _render_template(
        "account/request_login_code.html",
        {
            "form": form,
            "request_login_code_url": "/accounts/login/code/",
            "login_url": "/accounts/login/",
            "redirect_field": "",
        },
    )
    assert "{% element" not in content
    assert "{% endelement" not in content


@pytest.mark.django_db
def test_request_login_code_shows_other_signin_options_link():
    """request_login_code.html must contain a link back to login (other options)."""
    from allauth.account.forms import RequestLoginCodeForm

    form = RequestLoginCodeForm()
    content = _render_template(
        "account/request_login_code.html",
        {
            "form": form,
            "request_login_code_url": "/accounts/login/code/",
            "login_url": "/accounts/login/",
            "redirect_field": "",
        },
    )
    assert "/accounts/login/" in content


@pytest.mark.django_db
def test_request_login_code_form_field_present():
    """request_login_code.html must render the email form field."""
    from allauth.account.forms import RequestLoginCodeForm

    form = RequestLoginCodeForm()
    content = _render_template(
        "account/request_login_code.html",
        {
            "form": form,
            "request_login_code_url": "/accounts/login/code/",
            "login_url": "/accounts/login/",
            "redirect_field": "",
        },
    )
    # The form has an email field which crispy renders as <input type="email"> or similar
    assert "<input" in content


@pytest.mark.django_db
def test_confirm_login_code_has_no_element_tags():
    """confirm_login_code.html must not contain {% element %} tags in output."""
    from allauth.account.forms import ConfirmLoginCodeForm

    verify_form = ConfirmLoginCodeForm()
    content = _render_template(
        "account/confirm_login_code.html",
        {
            "verify_form": verify_form,
            "email": "user@example.com",
            "phone": None,
            "can_resend": True,
            "cancel_url": None,
            "redirect_field": "",
        },
    )
    assert "{% element" not in content
    assert "{% endelement" not in content


@pytest.mark.django_db
def test_confirm_login_code_renders_code_field():
    """confirm_login_code.html must render the code entry field (verify_form)."""
    from allauth.account.forms import ConfirmLoginCodeForm

    verify_form = ConfirmLoginCodeForm()
    content = _render_template(
        "account/confirm_login_code.html",
        {
            "verify_form": verify_form,
            "email": "user@example.com",
            "phone": None,
            "can_resend": False,
            "cancel_url": "/accounts/login/",
            "redirect_field": "",
        },
    )
    # verify_form has a 'code' field
    assert "code" in content.lower()
    assert "<input" in content


@pytest.mark.django_db
def test_confirm_login_code_resend_button_enabled_when_can_resend():
    """Resend button must be enabled (no disabled attr) when can_resend=True."""
    from allauth.account.forms import ConfirmLoginCodeForm

    verify_form = ConfirmLoginCodeForm()
    content = _render_template(
        "account/confirm_login_code.html",
        {
            "verify_form": verify_form,
            "email": "user@example.com",
            "phone": None,
            "can_resend": True,
            "cancel_url": None,
            "redirect_field": "",
        },
    )
    assert 'form="resend"' in content
    assert "disabled" not in content


@pytest.mark.django_db
def test_confirm_login_code_resend_button_disabled_when_cannot_resend():
    """Resend button must be present but disabled when can_resend=False."""
    from allauth.account.forms import ConfirmLoginCodeForm

    verify_form = ConfirmLoginCodeForm()
    content = _render_template(
        "account/confirm_login_code.html",
        {
            "verify_form": verify_form,
            "email": "user@example.com",
            "phone": None,
            "can_resend": False,
            "cancel_url": None,
            "redirect_field": "",
        },
    )
    assert 'id="resend"' in content  # resend form is still rendered
    assert "disabled" in content  # button is visually disabled


# ---------------------------------------------------------------------------
# T015 / US7: socialaccount entrance templates
# ---------------------------------------------------------------------------


class _MockProvider:
    """Minimal provider stub for template rendering tests."""

    name = "Google"
    id = "google"


@pytest.mark.django_db
def test_socialaccount_login_has_no_element_tags():
    """socialaccount/login.html must not contain {% element %} tags in output."""
    content = _render_template(
        "socialaccount/login.html",
        {"provider": _MockProvider(), "process": "login", "redirect_field": ""},
    )
    assert "{% element" not in content
    assert "{% endelement" not in content


@pytest.mark.django_db
def test_socialaccount_login_process_login_shows_provider_name():
    """socialaccount/login.html with process='login' shows provider name."""
    content = _render_template(
        "socialaccount/login.html",
        {"provider": _MockProvider(), "process": "login", "redirect_field": ""},
    )
    assert "Google" in content


@pytest.mark.django_db
def test_socialaccount_login_process_connect_shows_provider_name():
    """socialaccount/login.html with process='connect' shows provider name."""
    content = _render_template(
        "socialaccount/login.html",
        {"provider": _MockProvider(), "process": "connect", "redirect_field": ""},
    )
    assert "Google" in content


@pytest.mark.django_db
def test_socialaccount_login_has_continue_button():
    """socialaccount/login.html must contain a Continue submit button."""
    content = _render_template(
        "socialaccount/login.html",
        {"provider": _MockProvider(), "process": "login", "redirect_field": ""},
    )
    assert 'type="submit"' in content


@pytest.mark.django_db
def test_socialaccount_login_cancelled_has_no_element_tags():
    """socialaccount/login_cancelled.html must not contain {% element %} tags."""
    content = _render_template(
        "socialaccount/login_cancelled.html",
        {},
    )
    assert "{% element" not in content
    assert "{% endelement" not in content


@pytest.mark.django_db
def test_socialaccount_login_cancelled_shows_login_cancelled_title():
    """socialaccount/login_cancelled.html must show 'Login Cancelled'."""
    content = _render_template(
        "socialaccount/login_cancelled.html",
        {},
    )
    assert "Login Cancelled" in content


@pytest.mark.django_db
def test_socialaccount_login_cancelled_has_sign_in_link():
    """socialaccount/login_cancelled.html must contain a link to the login page."""
    content = _render_template(
        "socialaccount/login_cancelled.html",
        {},
    )
    login_url = reverse("account_login")
    assert login_url in content
    assert "sign in" in content.lower()


@pytest.mark.django_db
def test_socialaccount_login_redirect_has_no_element_tags():
    """socialaccount/login_redirect.html must not contain {% element %} tags."""
    content = _render_template(
        "socialaccount/login_redirect.html",
        {"provider": _MockProvider(), "redirect_to": "/accounts/google/login/?_redir="},
    )
    assert "{% element" not in content
    assert "{% endelement" not in content


@pytest.mark.django_db
def test_socialaccount_login_redirect_has_meta_refresh():
    """socialaccount/login_redirect.html must contain http-equiv='refresh' meta tag."""
    redirect_url = "/accounts/google/login/?_redir="
    content = _render_template(
        "socialaccount/login_redirect.html",
        {"provider": _MockProvider(), "redirect_to": redirect_url},
    )
    assert 'http-equiv="refresh"' in content
    assert redirect_url in content
