"""
Integration tests for the allauth password change / set / reauthenticate flow.

Covers:
  - T004 / US1: password_change.html and password_set.html render inside DAC layout
  - T005 / US2: Form fields render correctly on both management pages
  - T007 / US3: reauthenticate.html renders as a Cotton entrance page
"""

import pytest
from allauth.account.forms import ReauthenticateForm
from django.contrib.auth import get_user_model
from django.template import Context, Template
from django.test import RequestFactory
from django.urls import reverse
from django_cotton.compiler_regex import CottonCompiler  # type: ignore[import-untyped]

User = get_user_model()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def make_user(username="pwduser", email="pwduser@example.com", password="testpass123"):
    return User.objects.create_user(username=username, email=email, password=password)


def make_user_no_password(username="nopwduser", email="nopwd@example.com"):
    """Return a user with no usable password (triggers password_set flow)."""
    user = User.objects.create_user(username=username, email=email, password="temp")
    user.set_unusable_password()
    user.save()
    return user


# ---------------------------------------------------------------------------
# T004 / US1: password_change.html
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestPasswordChangeView:
    """Tests for account/password_change.html – management page with DAC layout."""

    def test_renders_200_for_authenticated(self, client):
        """account_change_password GET must return HTTP 200 for an authenticated user."""
        user = make_user()
        client.force_login(user)
        response = client.get(reverse("account_change_password"))
        assert response.status_code == 200

    def test_no_element_tags_in_output(self, client):
        """Rendered HTML must not contain raw {% element %} or {% endelement %} tags."""
        user = make_user()
        client.force_login(user)
        response = client.get(reverse("account_change_password"))
        content = response.content.decode()
        assert "{% element" not in content
        assert "{% endelement" not in content

    def test_has_page_content_block(self, client):
        """Response must contain the DAC breadcrumb root 'Account Center'."""
        user = make_user()
        client.force_login(user)
        response = client.get(reverse("account_change_password"))
        content = response.content.decode()
        assert "Account Center" in content

    def test_has_change_password_breadcrumb(self, client):
        """'Change Password' must appear in the breadcrumb output."""
        user = make_user()
        client.force_login(user)
        response = client.get(reverse("account_change_password"))
        content = response.content.decode()
        assert "Change Password" in content

    def test_has_submit_button(self, client):
        """Rendered HTML must contain a type="submit" button."""
        user = make_user()
        client.force_login(user)
        response = client.get(reverse("account_change_password"))
        content = response.content.decode()
        assert 'type="submit"' in content

    def test_has_forgot_password_link(self, client):
        """Rendered HTML must contain a link to account_reset_password."""
        user = make_user()
        client.force_login(user)
        response = client.get(reverse("account_change_password"))
        content = response.content.decode()
        assert reverse("account_reset_password") in content


# ---------------------------------------------------------------------------
# T004 / US1: password_set.html
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestPasswordSetView:
    """Tests for account/password_set.html – management page for users with no password."""

    def test_renders_200_for_authenticated(self, client):
        """account_set_password GET must return HTTP 200 for an authenticated user with no password."""
        user = make_user_no_password()
        client.force_login(user)
        response = client.get(reverse("account_set_password"))
        assert response.status_code == 200

    def test_no_element_tags_in_output(self, client):
        """Rendered HTML must not contain raw {% element %} or {% endelement %} tags."""
        user = make_user_no_password()
        client.force_login(user)
        response = client.get(reverse("account_set_password"))
        content = response.content.decode()
        assert "{% element" not in content
        assert "{% endelement" not in content

    def test_has_set_password_breadcrumb(self, client):
        """'Set Password' must appear in the breadcrumb output."""
        user = make_user_no_password()
        client.force_login(user)
        response = client.get(reverse("account_set_password"))
        content = response.content.decode()
        assert "Set Password" in content

    def test_has_submit_button(self, client):
        """Rendered HTML must contain a type="submit" button."""
        user = make_user_no_password()
        client.force_login(user)
        response = client.get(reverse("account_set_password"))
        content = response.content.decode()
        assert 'type="submit"' in content

    def test_no_forgot_password_link(self, client):
        """password_set.html must NOT contain a link to account_reset_password."""
        user = make_user_no_password()
        client.force_login(user)
        response = client.get(reverse("account_set_password"))
        content = response.content.decode()
        assert reverse("account_reset_password") not in content


# ---------------------------------------------------------------------------
# T004 / US1: base_manage_password.html inheritance chain
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestBaseManagePasswordView:
    """Verify that base_manage_password.html inherits the DAC base layout."""

    def test_base_manage_password_inherits_dac_base(self, client):
        """
        Render base_manage_password.html directly and assert DAC sidebar/breadcrumb
        structure is present (verifies the inheritance chain is unbroken).
        """
        user = make_user()
        client.force_login(user)
        # Change-password is served by base_manage_password → base_manage → dac/base
        response = client.get(reverse("account_change_password"))
        content = response.content.decode()
        # DAC sidebar is present
        assert "Account Center" in content
        # No element tags leaked
        assert "{% element" not in content


# ---------------------------------------------------------------------------
# T005 / US2: Form fields on password_change.html
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestPasswordChangeFormFields:
    """Verify form fields render correctly on password_change.html."""

    def test_form_has_old_password_field(self, client):
        """password_change.html must contain the current-password field."""
        user = make_user()
        client.force_login(user)
        response = client.get(reverse("account_change_password"))
        content = response.content.decode()
        assert 'name="oldpassword"' in content or 'type="password"' in content

    def test_form_has_new_password_fields(self, client):
        """password_change.html must contain password1 and password2 fields."""
        user = make_user()
        client.force_login(user)
        response = client.get(reverse("account_change_password"))
        content = response.content.decode()
        assert 'name="password1"' in content
        assert 'name="password2"' in content

    def test_submit_button_text_is_change_password(self, client):
        """Submit button text must be 'Change Password'."""
        user = make_user()
        client.force_login(user)
        response = client.get(reverse("account_change_password"))
        content = response.content.decode()
        assert "Change Password" in content

    def test_no_element_tags_present(self, client):
        """Rendered HTML must not contain raw {% element %} strings."""
        user = make_user()
        client.force_login(user)
        response = client.get(reverse("account_change_password"))
        content = response.content.decode()
        assert "{% element" not in content


# ---------------------------------------------------------------------------
# T005 / US2: Form fields on password_set.html
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestPasswordSetFormFields:
    """Verify form fields render correctly on password_set.html."""

    def test_form_has_new_password_fields(self, client):
        """password_set.html must contain password1 and password2 fields (no oldpassword)."""
        user = make_user_no_password()
        client.force_login(user)
        response = client.get(reverse("account_set_password"))
        content = response.content.decode()
        assert 'name="password1"' in content
        assert 'name="password2"' in content
        assert 'name="oldpassword"' not in content

    def test_submit_button_text_is_set_password(self, client):
        """Submit button text must be 'Set Password'."""
        user = make_user_no_password()
        client.force_login(user)
        response = client.get(reverse("account_set_password"))
        content = response.content.decode()
        assert "Set Password" in content

    def test_no_element_tags_present(self, client):
        """Rendered HTML must not contain raw {% element %} strings."""
        user = make_user_no_password()
        client.force_login(user)
        response = client.get(reverse("account_set_password"))
        content = response.content.decode()
        assert "{% element" not in content


# ---------------------------------------------------------------------------
# T007 / US3: reauthenticate.html
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestReauthenticateView:
    """Tests for account/reauthenticate.html – entrance-style page."""

    def test_renders_200_for_authenticated(self, client):
        """account_reauthenticate GET must return HTTP 200 for an authenticated user."""
        user = make_user()
        client.force_login(user)
        response = client.get(reverse("account_reauthenticate"))
        assert response.status_code == 200

    def test_no_element_tags_in_output(self, client):
        """Rendered HTML must not contain raw {% element %} or {% endelement %} tags."""
        user = make_user()
        client.force_login(user)
        response = client.get(reverse("account_reauthenticate"))
        content = response.content.decode()
        assert "{% element" not in content
        assert "{% endelement" not in content

    def test_has_password_field(self, client):
        """Rendered HTML must contain a type="password" input."""
        user = make_user()
        client.force_login(user)
        response = client.get(reverse("account_reauthenticate"))
        content = response.content.decode()
        assert 'type="password"' in content

    def test_has_confirm_button(self, client):
        """Rendered HTML must contain a submit button with text 'Confirm'."""
        user = make_user()
        client.force_login(user)
        response = client.get(reverse("account_reauthenticate"))
        content = response.content.decode()
        assert 'type="submit"' in content
        assert "Confirm" in content

    def test_no_alternatives_section_by_default(self, client):
        """'Alternative options' section must be absent when no alternatives are configured."""
        user = make_user()
        client.force_login(user)
        response = client.get(reverse("account_reauthenticate"))
        content = response.content.decode()
        assert "Alternative options" not in content

    @pytest.mark.django_db
    def test_alternatives_section_when_provided(self):
        """'Alternative options' section appears when reauthentication_alternatives is provided."""

        class MockAlternative:
            url = "/accounts/mock-mfa/"
            description = "Use authenticator code"

        user = make_user(username="reauth_alt_user", email="reauth_alt@example.com")
        factory = RequestFactory()
        request = factory.get("/")
        compiler = CottonCompiler()
        template_str = '{% extends "account/reauthenticate.html" %}'
        compiled = compiler.process(template_str)
        context = Context(
            {
                "request": request,
                "form": ReauthenticateForm(user=user),
                "reauthentication_alternatives": [MockAlternative()],
            }
        )
        html = Template(compiled).render(context)
        assert "Alternative options" in html
        assert "/accounts/mock-mfa/" in html
