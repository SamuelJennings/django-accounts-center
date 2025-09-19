"""
Tests for allauth URL resolution and template rendering.

This module tests that all allauth URLs properly resolve to the correct views
and render the expected templates with appropriate layouts.
"""

import pytest
from allauth.account.models import EmailAddress
from django.contrib.auth import get_user_model
from django.test import override_settings
from django.urls import resolve, reverse

User = get_user_model()


@pytest.mark.django_db
class TestAllauthURLResolution:
    """Test allauth URL resolution and basic view functionality."""

    def test_account_login_url_resolution(self):
        """Test account_login URL resolves correctly."""
        url = reverse("account_login")
        assert url == "/account/login/"

        resolved = resolve(url)
        assert resolved.view_name == "account_login"

    def test_account_signup_url_resolution(self):
        """Test account_signup URL resolves correctly."""
        url = reverse("account_signup")
        assert url == "/account/signup/"

        resolved = resolve(url)
        assert resolved.view_name == "account_signup"

    def test_account_logout_url_resolution(self):
        """Test account_logout URL resolves correctly."""
        url = reverse("account_logout")
        assert url == "/account/logout/"

        resolved = resolve(url)
        assert resolved.view_name == "account_logout"

    def test_password_reset_url_resolution(self):
        """Test password reset URL resolves correctly."""
        url = reverse("account_reset_password")
        assert url == "/account/password/reset/"

        resolved = resolve(url)
        assert resolved.view_name == "account_reset_password"

    def test_password_change_url_resolution(self):
        """Test password change URL resolves correctly."""
        url = reverse("account_change_password")
        assert url == "/account/password/change/"

        resolved = resolve(url)
        assert resolved.view_name == "account_change_password"

    def test_account_email_url_resolution(self):
        """Test account email management URL resolves correctly."""
        url = reverse("account_email")
        assert url == "/account/email/"

        resolved = resolve(url)
        assert resolved.view_name == "account_email"

    def test_socialaccount_connections_url_resolution(self):
        """Test social account connections URL resolves correctly."""
        url = reverse("socialaccount_connections")
        assert url == "/account/connected-accounts/"

        resolved = resolve(url)
        assert resolved.view_name == "socialaccount_connections"

    def test_usersessions_list_url_resolution(self):
        """Test user sessions list URL resolves correctly."""
        url = reverse("usersessions_list")
        assert url == "/account/sessions/"

        resolved = resolve(url)
        assert resolved.view_name == "usersessions_list"

    def test_mfa_index_url_resolution(self):
        """Test MFA index URL resolves correctly."""
        url = reverse("mfa_index")
        assert url == "/account/mfa/"

        resolved = resolve(url)
        assert resolved.view_name == "mfa_index"


@pytest.mark.django_db
class TestEntranceLayoutTemplates:
    """Test templates that should use entrance layout."""

    def test_login_page_uses_entrance_layout(self, client):
        """Test login page uses entrance layout."""
        response = client.get(reverse("account_login"))
        assert response.status_code == 200

        # Check that entrance layout components are present
        content = response.content.decode()
        assert "c-dac.layout.entrance" in content
        assert "c-dac.entrance.card" in content
        assert "c-dac.entrance.brand-logo" in content

    def test_signup_page_uses_entrance_layout(self, client):
        """Test signup page uses entrance layout."""
        response = client.get(reverse("account_signup"))
        assert response.status_code == 200

        content = response.content.decode()
        assert "c-dac.layout.entrance" in content
        assert "c-dac.entrance.card" in content

    def test_password_reset_uses_entrance_layout(self, client):
        """Test password reset page uses entrance layout."""
        response = client.get(reverse("account_reset_password"))
        assert response.status_code == 200

        content = response.content.decode()
        assert "c-dac.layout.entrance" in content

    @override_settings(ACCOUNT_EMAIL_VERIFICATION="mandatory")
    def test_email_confirm_uses_entrance_layout(self, client, user):
        """Test email confirmation page uses entrance layout."""
        # Create an email confirmation scenario
        email = EmailAddress.objects.create(user=user, email=user.email, verified=False, primary=True)
        key = email.send_confirmation()

        response = client.get(reverse("account_confirm_email", args=[key.key]))
        assert response.status_code == 200

        content = response.content.decode()
        assert "c-dac.layout.entrance" in content


@pytest.mark.django_db
class TestStandardLayoutTemplates:
    """Test templates that should use standard layout."""

    def test_email_management_uses_standard_layout(self, authenticated_client):
        """Test email management page uses standard layout."""
        response = authenticated_client.get(reverse("account_email"))
        assert response.status_code == 200

        content = response.content.decode()
        assert "c-dac.layout.standard" in content
        assert "c-dac.sidebar" in content
        assert "c-dac.header" in content

    def test_password_change_uses_standard_layout(self, authenticated_client):
        """Test password change page uses standard layout."""
        response = authenticated_client.get(reverse("account_change_password"))
        assert response.status_code == 200

        content = response.content.decode()
        assert "c-dac.layout.standard" in content

    def test_social_connections_uses_standard_layout(self, authenticated_client):
        """Test social connections page uses standard layout."""
        response = authenticated_client.get(reverse("socialaccount_connections"))
        assert response.status_code == 200

        content = response.content.decode()
        assert "c-dac.layout.standard" in content

    def test_user_sessions_uses_standard_layout(self, authenticated_client):
        """Test user sessions page uses standard layout."""
        response = authenticated_client.get(reverse("usersessions_list"))
        assert response.status_code == 200

        content = response.content.decode()
        assert "c-dac.layout.standard" in content

    def test_mfa_index_uses_standard_layout(self, authenticated_client):
        """Test MFA index page uses standard layout."""
        response = authenticated_client.get(reverse("mfa_index"))
        assert response.status_code == 200

        content = response.content.decode()
        assert "c-dac.layout.standard" in content


@pytest.mark.django_db
class TestTemplateAccessControl:
    """Test that templates require appropriate authentication."""

    def test_authenticated_templates_redirect_anonymous(self, client):
        """Test that authenticated-only templates redirect anonymous users."""
        authenticated_urls = [
            "account_email",
            "account_change_password",
            "socialaccount_connections",
            "usersessions_list",
            "mfa_index",
        ]

        for url_name in authenticated_urls:
            response = client.get(reverse(url_name))
            assert response.status_code == 302  # Redirect to login
            assert "login" in response.url

    def test_public_templates_accessible_anonymous(self, client):
        """Test that public templates are accessible to anonymous users."""
        public_urls = [
            "account_login",
            "account_signup",
            "account_reset_password",
        ]

        for url_name in public_urls:
            response = client.get(reverse(url_name))
            assert response.status_code == 200

    def test_authenticated_templates_accessible_to_users(self, authenticated_client):
        """Test that authenticated templates are accessible to logged-in users."""
        authenticated_urls = [
            "account_email",
            "account_change_password",
            "socialaccount_connections",
            "usersessions_list",
            "mfa_index",
        ]

        for url_name in authenticated_urls:
            response = authenticated_client.get(reverse(url_name))
            assert response.status_code == 200


@pytest.mark.django_db
class TestTemplateContext:
    """Test that templates receive expected context data."""

    def test_login_template_context(self, client):
        """Test login template receives correct context."""
        response = client.get(reverse("account_login"))
        assert response.status_code == 200

        # Check for form in context
        assert "form" in response.context
        assert response.context["form"].__class__.__name__ == "LoginForm"

    def test_signup_template_context(self, client):
        """Test signup template receives correct context."""
        response = client.get(reverse("account_signup"))
        assert response.status_code == 200

        # Check for form in context
        assert "form" in response.context
        assert response.context["form"].__class__.__name__ == "SignupForm"

    def test_email_template_context(self, authenticated_client, user):
        """Test email management template receives correct context."""
        response = authenticated_client.get(reverse("account_email"))
        assert response.status_code == 200

        # Check for email-related context
        assert "emailaddresses" in response.context
        assert "form" in response.context

    def test_social_connections_context(self, authenticated_client):
        """Test social connections template receives correct context."""
        response = authenticated_client.get(reverse("socialaccount_connections"))
        assert response.status_code == 200

        # Should have social account context
        assert "socialaccounts" in response.context or "object_list" in response.context


@pytest.mark.django_db
class TestCustomURLsIntegration:
    """Test integration with custom DAC addon URLs."""

    def test_custom_email_url_resolution(self):
        """Test custom email URL from dac.addons.allauth.urls resolves."""
        url = reverse("account_email")
        assert url == "/account/email/"

    def test_custom_password_change_url_resolution(self):
        """Test custom password change URL resolves."""
        url = reverse("account_change_password")
        assert url == "/account/password/change/"

    def test_custom_social_connections_url_resolution(self):
        """Test custom social connections URL resolves."""
        url = reverse("socialaccount_connections")
        assert url == "/account/connected-accounts/"

    def test_custom_sessions_url_resolution(self):
        """Test custom sessions URL resolves."""
        url = reverse("usersessions_list")
        assert url == "/account/sessions/"

    def test_custom_mfa_url_resolution(self):
        """Test custom MFA URL resolves."""
        url = reverse("mfa_index")
        assert url == "/account/mfa/"
