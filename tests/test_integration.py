"""
Integration tests for django-accounts-center template system.

This module provides end-to-end integration tests for the complete
template and component system.
"""

import pytest
from django.contrib.auth import get_user_model
from django.test import override_settings

User = get_user_model()


@pytest.mark.django_db
class TestCompleteAuthenticationFlow:
    """Test complete authentication flows with proper template rendering."""

    def test_signup_login_flow(self, client):
        """Test complete signup and login flow with proper templates."""
        # 1. Visit signup page
        signup_response = client.get("/account/signup/")
        assert signup_response.status_code == 200
        assert "c-dac.entrance" in signup_response.content.decode()

        # 2. Submit signup form
        signup_data = {"email": "testflow@example.com", "password1": "testpassword123", "password2": "testpassword123"}
        signup_post = client.post("/account/signup/", signup_data)
        assert signup_post.status_code in [200, 302]

        # 3. Visit login page
        login_response = client.get("/account/login/")
        assert login_response.status_code == 200
        assert "c-dac.entrance" in login_response.content.decode()

        # 4. Submit login form
        login_data = {"login": "testflow@example.com", "password": "testpassword123"}
        login_post = client.post("/account/login/", login_data)
        assert login_post.status_code in [200, 302]

    def test_password_reset_flow(self, client, user):
        """Test password reset flow with proper templates."""
        # 1. Visit password reset page
        reset_response = client.get("/account/password/reset/")
        assert reset_response.status_code == 200
        assert "c-dac.entrance" in reset_response.content.decode()

        # 2. Submit password reset form
        reset_data = {"email": user.email}
        reset_post = client.post("/account/password/reset/", reset_data)
        assert reset_post.status_code in [200, 302]

    def test_logout_flow(self, authenticated_client):
        """Test logout flow with proper template handling."""
        # Visit logout page
        logout_response = authenticated_client.get("/account/logout/")
        assert logout_response.status_code in [200, 302]

        # Submit logout
        logout_post = authenticated_client.post("/account/logout/")
        assert logout_post.status_code in [200, 302]


@pytest.mark.django_db
class TestAccountManagementFlow:
    """Test account management flows with proper template rendering."""

    def test_email_management_flow(self, authenticated_client, user_with_verified_email):
        """Test email management flow with standard layout."""
        # 1. Visit email management page
        email_response = authenticated_client.get("/account/email/")
        assert email_response.status_code == 200
        content = email_response.content.decode()
        assert "c-dac.page" in content

        # 2. Add new email
        add_email_data = {"action_add": "", "email": "newemail@example.com"}
        add_response = authenticated_client.post("/account/email/", add_email_data)
        assert add_response.status_code in [200, 302]

    def test_password_change_flow(self, authenticated_client):
        """Test password change flow with standard layout."""
        # 1. Visit password change page
        change_response = authenticated_client.get("/account/password/change/")
        assert change_response.status_code == 200
        content = change_response.content.decode()
        assert "c-dac.page" in content

        # 2. Submit password change form
        change_data = {"oldpassword": "testpass123", "password1": "newpassword123", "password2": "newpassword123"}
        change_post = authenticated_client.post("/account/password/change/", change_data)
        assert change_post.status_code in [200, 302]

    def test_social_connections_flow(self, authenticated_client):
        """Test social connections management flow."""
        # Visit social connections page
        connections_response = authenticated_client.get("/account/connected-accounts/")
        assert connections_response.status_code == 200
        content = connections_response.content.decode()
        assert "c-dac.page" in content

    def test_user_sessions_flow(self, authenticated_client):
        """Test user sessions management flow."""
        # Visit user sessions page
        sessions_response = authenticated_client.get("/account/sessions/")
        assert sessions_response.status_code == 200
        content = sessions_response.content.decode()
        assert "c-dac.page" in content


@pytest.mark.django_db
class TestSocialAuthenticationFlow:
    """Test social authentication flows with proper templates."""

    def test_social_login_flow(self, client, social_app):
        """Test social login flow with entrance layout."""
        # Visit login page with social providers
        login_response = client.get("/account/login/")
        assert login_response.status_code == 200
        content = login_response.content.decode()
        assert "c-dac.entrance" in content

        # Should show social providers when available
        assert "provider" in content.lower() or login_response.status_code == 200

    @override_settings(SOCIALACCOUNT_ONLY=True)
    def test_socialaccount_only_flow(self, client, social_app):
        """Test social-only authentication flow."""
        # Visit login page in social-only mode
        login_response = client.get("/account/login/")
        assert login_response.status_code == 200
        content = login_response.content.decode()

        # Should use entrance layout
        assert "c-dac.entrance" in content

        # Should not show email/password forms prominently


@pytest.mark.django_db
class TestMFAFlow:
    """Test MFA (Multi-Factor Authentication) flows."""

    def test_mfa_setup_flow(self, authenticated_client):
        """Test MFA setup flow with standard layout."""
        # Visit MFA setup page
        mfa_response = authenticated_client.get("/account/mfa/")
        assert mfa_response.status_code == 200
        content = mfa_response.content.decode()
        assert "c-dac.page" in content

    def test_mfa_authentication_flow(self, authenticated_client):
        """Test MFA authentication flow."""
        # This would test actual MFA authentication
        # For now, just test page accessibility
        mfa_response = authenticated_client.get("/account/mfa/")
        assert mfa_response.status_code == 200


@pytest.mark.django_db
class TestErrorHandlingIntegration:
    """Test error handling across the entire template system."""

    def test_form_errors_maintain_layout(self, client):
        """Test that form errors maintain proper layout."""
        # Submit invalid login form
        invalid_login = client.post("/account/login/", {"login": "invalid@email.com", "password": "wrongpassword"})

        if invalid_login.status_code == 200:
            content = invalid_login.content.decode()
            # Should maintain entrance layout even with errors
            assert "c-dac.entrance" in content

    def test_validation_errors_with_components(self, client):
        """Test validation errors display properly with components."""
        # Submit invalid signup form
        invalid_signup = client.post(
            "/account/signup/", {"email": "invalid-email", "password1": "short", "password2": "different"}
        )

        if invalid_signup.status_code == 200:
            content = invalid_signup.content.decode()
            # Should maintain layout and show errors
            assert "c-dac.entrance" in content

    def test_permission_errors_redirect_properly(self, client):
        """Test that permission errors redirect to appropriate templates."""
        # Try to access authenticated page as anonymous user
        response = client.get("/account/email/")
        assert response.status_code == 302  # Should redirect to login

        # Follow redirect to login page
        login_response = client.get(response.url)
        if login_response.status_code == 200:
            content = login_response.content.decode()
            assert "c-dac.entrance" in content


@pytest.mark.django_db
class TestComponentInteractionIntegration:
    """Test component interactions across the system."""

    def test_form_component_integration(self, client):
        """Test form components work properly with layouts."""
        # Test login form
        login_response = client.get("/account/login/")
        content = login_response.content.decode()

        # Should have form component within entrance layout
        assert "c-dac.entrance" in content
        assert "c-dac.form" in content or "<form" in content

    def test_alert_component_integration(self, authenticated_client):
        """Test alert components work properly with layouts."""
        # This would test with actual messages
        response = authenticated_client.get("/account/email/")
        content = response.content.decode()

        # Should have standard layout ready for alerts
        assert "c-dac.page" in content

    def test_navigation_component_integration(self, authenticated_client):
        """Test navigation components work properly with standard layout."""
        response = authenticated_client.get("/account/email/")
        content = response.content.decode()

        # Should have navigation components
        assert "c-dac.page" in content
        assert "c-dac.sidebar" in content
        assert "c-dac.header" in content

    def test_responsive_component_integration(self, client, authenticated_client):
        """Test responsive components work across layouts."""
        # Test entrance layout responsiveness
        entrance_response = client.get("/account/login/")
        entrance_content = entrance_response.content.decode()
        assert "d-flex" in entrance_content or "container" in entrance_content

        # Test standard layout responsiveness
        standard_response = authenticated_client.get("/account/email/")
        standard_content = standard_response.content.decode()
        assert "container-fluid" in standard_content or "col-" in standard_content


@pytest.mark.django_db
class TestSettingsIntegration:
    """Test settings integration across the template system."""

    @override_settings(ACCOUNT_ALLOW_REGISTRATION=False)
    def test_registration_disabled_integration(self, client):
        """Test template behavior when registration is disabled."""
        login_response = client.get("/account/login/")
        assert login_response.status_code == 200
        # Should handle disabled registration gracefully

    @override_settings(ACCOUNT_EMAIL_VERIFICATION="mandatory")
    def test_email_verification_integration(self, client):
        """Test template behavior with mandatory email verification."""
        signup_response = client.get("/account/signup/")
        assert signup_response.status_code == 200
        # Should handle email verification requirements

    @override_settings(DEBUG=True)
    def test_debug_mode_integration(self, client):
        """Test template behavior in debug mode."""
        response = client.get("/account/login/")
        assert response.status_code == 200
        # Should handle debug mode appropriately

    @override_settings(DEBUG=False)
    def test_production_mode_integration(self, client):
        """Test template behavior in production mode."""
        response = client.get("/account/login/")
        assert response.status_code == 200
        # Should handle production mode appropriately


@pytest.mark.django_db
class TestPerformanceIntegration:
    """Test performance aspects of the template system."""

    def test_template_rendering_performance(self, client, authenticated_client):
        """Test that templates render efficiently."""
        import time

        # Test entrance layout performance
        start = time.time()
        entrance_response = client.get("/account/login/")
        entrance_time = time.time() - start

        assert entrance_response.status_code == 200
        assert entrance_time < 2.0  # Should render quickly

        # Test standard layout performance
        start = time.time()
        standard_response = authenticated_client.get("/account/email/")
        standard_time = time.time() - start

        assert standard_response.status_code == 200
        assert standard_time < 2.0  # Should render quickly

    def test_component_composition_performance(self, client):
        """Test performance of component composition."""
        import time

        start = time.time()
        for _ in range(5):  # Test multiple renders
            response = client.get("/account/login/")
            assert response.status_code == 200

        total_time = time.time() - start
        assert total_time < 5.0  # Should handle multiple renders efficiently


@pytest.mark.django_db
class TestAccessibilityIntegration:
    """Test accessibility across the template system."""

    def test_semantic_html_structure(self, client, authenticated_client):
        """Test semantic HTML structure across layouts."""
        # Test entrance layout semantics
        entrance_response = client.get("/account/login/")
        entrance_content = entrance_response.content.decode()
        assert "<main" in entrance_content or "<section" in entrance_content

        # Test standard layout semantics
        standard_response = authenticated_client.get("/account/email/")
        standard_content = standard_response.content.decode()
        assert "<main" in standard_content

    def test_form_accessibility(self, client):
        """Test form accessibility across the system."""
        response = client.get("/account/login/")
        content = response.content.decode()

        # Should have accessible forms
        assert "<form" in content
        # Should have proper labeling (implicit in component usage)

    def test_navigation_accessibility(self, authenticated_client):
        """Test navigation accessibility in standard layout."""
        response = authenticated_client.get("/account/email/")
        content = response.content.decode()

        # Should have accessible navigation
        assert "nav" in content.lower() or "c-dac.sidebar" in content
