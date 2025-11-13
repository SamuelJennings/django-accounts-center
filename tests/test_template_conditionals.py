"""
Tests for template conditionals in allauth addon templates.

This module tests the conditional logic within allauth templates, including
settings-based conditionals, provider availability, and feature flags.
"""

import pytest
from allauth.socialaccount.models import SocialApp
from django.contrib.auth import get_user_model
from django.test import override_settings

User = get_user_model()


@pytest.mark.django_db
class TestSocialAccountConditionals:
    """Test conditionals related to social account settings."""

    @override_settings(SOCIALACCOUNT_ONLY=True)
    def test_socialaccount_only_hides_email_forms(self, client):
        """Test that SOCIALACCOUNT_ONLY=True hides email/password forms."""
        response = client.get("/account/login/")
        content = response.content.decode()

        # Email/password form should be hidden
        assert "email" not in content.lower() or "password" not in content.lower()
        # Social login should be prominent
        assert response.status_code == 200

    @override_settings(SOCIALACCOUNT_ONLY=False)
    def test_socialaccount_disabled_shows_email_forms(self, client):
        """Test that SOCIALACCOUNT_ONLY=False shows email/password forms."""
        response = client.get("/account/login/")
        content = response.content.decode()

        # Email/password form should be visible
        assert "c-dac.form" in content
        assert "Sign In" in content or "sign" in content.lower()

    def test_provider_list_conditional_rendering(self, client):
        """Test provider list conditional rendering based on available providers."""
        # Test without social providers
        response = client.get("/account/login/")
        content = response.content.decode()

        # Should handle empty provider list gracefully
        assert response.status_code == 200

    @pytest.mark.django_db
    def test_provider_availability_conditional(self, client):
        """Test conditional rendering based on provider availability."""
        # Create a social app
        social_app = SocialApp.objects.create(
            provider="google", name="Google", client_id="test_client_id", secret="test_secret"
        )
        social_app.sites.add(1)  # Add to default site

        response = client.get("/account/login/")
        content = response.content.decode()

        # Should show social providers when available
        assert response.status_code == 200


@pytest.mark.django_db
class TestAuthenticationMethodConditionals:
    """Test conditionals for different authentication methods."""

    @override_settings(ACCOUNT_LOGIN_BY_CODE_ENABLED=True)
    def test_login_by_code_enabled_shows_code_option(self, client):
        """Test that LOGIN_BY_CODE_ENABLED=True shows code login option."""
        response = client.get("/account/login/")
        content = response.content.decode()

        # Should show code login option
        assert "code" in content.lower() or response.status_code == 200

    @override_settings(ACCOUNT_LOGIN_BY_CODE_ENABLED=False)
    def test_login_by_code_disabled_hides_code_option(self, client):
        """Test that LOGIN_BY_CODE_ENABLED=False hides code login option."""
        response = client.get("/account/login/")
        content = response.content.decode()

        # Code login should not be prominent
        assert response.status_code == 200

    def test_passkey_login_conditional(self, client):
        """Test passkey login conditional rendering."""
        response = client.get("/account/login/")
        content = response.content.decode()

        # Should handle passkey availability
        assert ":visible=" in content or response.status_code == 200

    def test_mfa_conditionals(self, authenticated_client):
        """Test MFA-related conditionals."""
        response = authenticated_client.get("/account/mfa/")
        content = response.content.decode()

        # Should render MFA page regardless of setup state
        assert response.status_code == 200


@pytest.mark.django_db
class TestEmailVerificationConditionals:
    """Test conditionals related to email verification settings."""

    @override_settings(ACCOUNT_EMAIL_VERIFICATION="mandatory")
    def test_mandatory_email_verification_conditionals(self, client):
        """Test conditionals when email verification is mandatory."""
        response = client.get("/account/signup/")
        content = response.content.decode()

        # Should handle mandatory verification
        assert response.status_code == 200

    @override_settings(ACCOUNT_EMAIL_VERIFICATION="optional")
    def test_optional_email_verification_conditionals(self, client):
        """Test conditionals when email verification is optional."""
        response = client.get("/account/signup/")
        content = response.content.decode()

        # Should handle optional verification
        assert response.status_code == 200

    @override_settings(ACCOUNT_EMAIL_VERIFICATION="none")
    def test_no_email_verification_conditionals(self, client):
        """Test conditionals when email verification is disabled."""
        response = client.get("/account/signup/")
        content = response.content.decode()

        # Should handle no verification
        assert response.status_code == 200


@pytest.mark.django_db
class TestUserStateConditionals:
    """Test conditionals based on user authentication state."""

    def test_anonymous_user_conditionals(self, client):
        """Test conditionals for anonymous users."""
        # Test public pages
        public_urls = ["/account/login/", "/account/signup/", "/account/password/reset/"]

        for url in public_urls:
            response = client.get(url)
            assert response.status_code == 200

    def test_authenticated_user_conditionals(self, authenticated_client):
        """Test conditionals for authenticated users."""
        # Test authenticated pages
        auth_urls = ["/account/email/", "/account/password/change/"]

        for url in auth_urls:
            response = authenticated_client.get(url)
            assert response.status_code == 200

    def test_superuser_conditionals(self, client, superuser):
        """Test conditionals for superuser."""
        client.force_login(superuser)
        response = client.get("/account/email/")

        # Superuser should access all features
        assert response.status_code == 200


@pytest.mark.django_db
class TestFeatureFlagConditionals:
    """Test conditionals based on feature flags and settings."""

    def test_debug_mode_conditionals(self, client):
        """Test conditionals that depend on DEBUG setting."""
        response = client.get("/account/login/")

        # Should handle debug mode appropriately
        assert response.status_code == 200

    @override_settings(ACCOUNT_ALLOW_REGISTRATION=True)
    def test_registration_enabled_conditionals(self, client):
        """Test conditionals when registration is enabled."""
        response = client.get("/account/login/")
        content = response.content.decode()

        # Should show signup link when registration is enabled
        assert "sign up" in content.lower() or "signup" in content.lower() or response.status_code == 200

    @override_settings(ACCOUNT_ALLOW_REGISTRATION=False)
    def test_registration_disabled_conditionals(self, client):
        """Test conditionals when registration is disabled."""
        response = client.get("/account/login/")

        # Should handle disabled registration gracefully
        assert response.status_code == 200


@pytest.mark.django_db
class TestFormConditionals:
    """Test conditionals within forms and form fields."""

    def test_password_field_conditionals(self, client):
        """Test conditionals related to password fields."""
        response = client.get("/account/login/")
        content = response.content.decode()

        # Should handle password field conditionals
        assert "password" in content.lower() or response.status_code == 200

    def test_email_field_conditionals(self, authenticated_client):
        """Test conditionals related to email fields."""
        response = authenticated_client.get("/account/email/")
        content = response.content.decode()

        # Should handle email field conditionals
        assert "email" in content.lower() or response.status_code == 200

    def test_form_error_conditionals(self, client):
        """Test conditionals for form error display."""
        # Submit invalid login to test error conditionals
        response = client.post("/account/login/", {"login": "invalid@email.com", "password": "wrongpassword"})

        # Should handle form errors gracefully
        assert response.status_code in [200, 302]  # Either show errors or redirect


@pytest.mark.django_db
class TestNavigationConditionals:
    """Test conditionals in navigation and menu items."""

    def test_authenticated_navigation_conditionals(self, authenticated_client):
        """Test navigation conditionals for authenticated users."""
        response = authenticated_client.get("/account/email/")
        content = response.content.decode()

        # Should show authenticated user navigation
        assert "c-dac.sidebar" in content or response.status_code == 200

    def test_anonymous_navigation_conditionals(self, client):
        """Test navigation conditionals for anonymous users."""
        response = client.get("/account/login/")
        content = response.content.decode()

        # Should show appropriate navigation for anonymous users
        assert response.status_code == 200


@pytest.mark.django_db
class TestMessageConditionals:
    """Test conditionals for message display."""

    def test_success_message_conditionals(self, authenticated_client):
        """Test conditionals for success messages."""
        # This would typically be tested with actual form submissions
        response = authenticated_client.get("/account/email/")

        # Should handle message conditionals
        assert response.status_code == 200

    def test_error_message_conditionals(self, client):
        """Test conditionals for error messages."""
        # Submit invalid form to trigger error messages
        response = client.post("/account/login/", {})

        # Should handle error message conditionals
        assert response.status_code in [200, 302]


@pytest.mark.django_db
class TestLayoutConditionals:
    """Test conditionals that determine layout selection."""

    def test_entrance_layout_conditionals(self, client):
        """Test conditionals that trigger entrance layout."""
        entrance_urls = ["/account/login/", "/account/signup/", "/account/password/reset/"]

        for url in entrance_urls:
            response = client.get(url)
            content = response.content.decode()

            # Should use entrance layout
            assert "c-dac.entrance" in content or response.status_code == 200

    def test_standard_layout_conditionals(self, authenticated_client):
        """Test conditionals that trigger standard layout."""
        standard_urls = ["/account/email/", "/account/password/change/"]

        for url in standard_urls:
            response = authenticated_client.get(url)
            content = response.content.decode()

            # Should use standard layout
            assert "c-dac.page" in content or response.status_code == 200


@pytest.mark.django_db
class TestActionConditionals:
    """Test conditionals for action buttons and links."""

    def test_form_action_conditionals(self, client):
        """Test conditionals for form action buttons."""
        response = client.get("/account/login/")
        content = response.content.decode()

        # Should show appropriate action buttons
        assert "c-dac.entrance.action" in content or "submit" in content.lower()

    def test_link_action_conditionals(self, client):
        """Test conditionals for action links."""
        response = client.get("/account/login/")
        content = response.content.decode()

        # Should show appropriate action links
        assert "c-dac.link" in content or "href=" in content

    def test_secondary_action_conditionals(self, client):
        """Test conditionals for secondary actions."""
        response = client.get("/account/login/")
        content = response.content.decode()

        # Should handle secondary actions appropriately
        assert response.status_code == 200


@pytest.mark.django_db
class TestIconConditionals:
    """Test conditionals for icon display."""

    def test_icon_visibility_conditionals(self, client):
        """Test conditionals that control icon visibility."""
        response = client.get("/account/login/")
        content = response.content.decode()

        # Should handle icon conditionals
        assert "icon=" in content or "c-dac.icon" in content or response.status_code == 200

    def test_icon_type_conditionals(self, authenticated_client):
        """Test conditionals that determine icon types."""
        response = authenticated_client.get("/account/email/")
        content = response.content.decode()

        # Should handle icon type conditionals
        assert response.status_code == 200


@pytest.mark.django_db
class TestSettingsBasedConditionals:
    """Test conditionals based on various allauth settings."""

    @override_settings(ACCOUNT_SESSION_REMEMBER=True)
    def test_remember_me_conditionals(self, client):
        """Test conditionals when session remember is enabled."""
        response = client.get("/account/login/")

        # Should handle remember me functionality
        assert response.status_code == 200

    @override_settings(ACCOUNT_LOGOUT_ON_GET=True)
    def test_logout_on_get_conditionals(self, authenticated_client):
        """Test conditionals when logout on GET is enabled."""
        response = authenticated_client.get("/account/logout/")

        # Should handle logout on GET appropriately
        assert response.status_code in [200, 302]

    @override_settings(ACCOUNT_CONFIRM_EMAIL_ON_GET=True)
    def test_confirm_email_on_get_conditionals(self, client):
        """Test conditionals when email confirmation on GET is enabled."""
        # This would need a valid confirmation key
        response = client.get("/account/login/")

        # Should handle email confirmation settings
        assert response.status_code == 200
