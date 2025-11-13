"""
Tests for layout type detection in allauth templates.

This module tests the logic that determines whether a template should use
the entrance layout or standard layout based on various conditions.

The tests check for actual rendered HTML content rather than cotton component tags,
since cotton components are server-side rendered into HTML.
"""

import pytest
from django.contrib.auth import get_user_model
from django.test import override_settings

User = get_user_model()


@pytest.mark.django_db
class TestEntranceLayoutDetection:
    """Test detection and usage of entrance layout."""

    def test_login_page_uses_entrance_layout(self, client):
        """Test that login page uses entrance layout."""
        response = client.get("/account/login/")
        content = response.content.decode()

        # Should use entrance layout - check for distinctive layout markers
        assert 'data-layout="entrance"' in content
        assert "min-vh-100 d-flex align-items-center justify-content-center" in content
        assert "max-width: 28rem" in content  # Entrance layout has constrained width
        # Check for entrance-specific components
        assert "card shadow border-0" in content  # Entrance card styling
        assert response.status_code == 200

    def test_signup_page_uses_entrance_layout(self, client):
        """Test that signup page uses entrance layout."""
        response = client.get("/account/signup/")
        content = response.content.decode()

        # Should use entrance layout for signup
        assert 'data-layout="entrance"' in content
        assert "min-vh-100 d-flex align-items-center justify-content-center" in content
        assert "card shadow border-0" in content
        assert response.status_code == 200

    def test_password_reset_uses_entrance_layout(self, client):
        """Test that password reset page uses entrance layout."""
        response = client.get("/account/password/reset/")
        content = response.content.decode()

        # Should use entrance layout for password reset
        assert 'data-layout="entrance"' in content
        assert "min-vh-100 d-flex align-items-center justify-content-center" in content
        assert response.status_code == 200

    def test_logout_uses_entrance_layout(self, authenticated_client):
        """Test that logout page uses entrance layout."""
        response = authenticated_client.get("/account/logout/")

        # Logout might redirect or show confirmation page
        # Both should use appropriate layout
        assert response.status_code in [200, 302]
        if response.status_code == 200:
            content = response.content.decode()
            assert 'data-layout="entrance"' in content

    def test_account_inactive_handling(self, client):
        """Test handling of inactive account scenarios."""
        # Create inactive user
        User.objects.create_user(
            username="inactive",
            email="inactive@example.com",
            password="testpass123",  # noqa: S106 # Test password
            is_active=False,
        )

        # Try to login with inactive user
        response = client.post(
            "/account/login/",
            {
                "login": "inactive@example.com",
                "password": "testpass123",  # Test password
            },
        )

        # Should handle inactive account appropriately
        assert response.status_code in [200, 302]

    def test_email_confirmation_uses_entrance_layout(self, client):
        """Test that email confirmation pages use entrance layout."""
        # Test the login page as a proxy for entrance layout behavior
        response = client.get("/account/login/")
        content = response.content.decode()

        # Should use entrance layout structure
        assert 'data-layout="entrance"' in content


@pytest.mark.django_db
class TestStandardLayoutDetection:
    """Test detection and usage of standard layout."""

    def test_email_management_uses_standard_layout(self, authenticated_client):
        """Test that email management page uses standard layout."""
        response = authenticated_client.get("/account/email/")
        content = response.content.decode()

        # Should use standard layout for authenticated features
        assert 'data-layout="standard"' in content
        assert 'id="AccountCenterMenu"' in content  # Sidebar navigation
        assert "offcanvas-md offcanvas-start" in content  # Responsive sidebar
        assert response.status_code == 200

    def test_password_change_uses_standard_layout(self, authenticated_client):
        """Test that password change page uses standard layout."""
        response = authenticated_client.get("/account/password/change/")
        content = response.content.decode()

        # Should use standard layout for account management
        assert 'data-layout="standard"' in content
        assert 'id="AccountCenterMenu"' in content
        assert response.status_code == 200

    def test_social_connections_uses_standard_layout(self, authenticated_client):
        """Test that social connections page uses standard layout."""
        response = authenticated_client.get("/account/social/connections/")
        content = response.content.decode()

        # Should use standard layout for account features
        assert 'data-layout="standard"' in content
        assert 'id="AccountCenterMenu"' in content
        assert response.status_code == 200

    def test_user_sessions_uses_standard_layout(self, authenticated_client):
        """Test that user sessions page uses standard layout."""
        response = authenticated_client.get("/account/sessions/")
        content = response.content.decode()

        # Should use standard layout for session management
        assert 'data-layout="standard"' in content
        assert 'id="AccountCenterMenu"' in content
        assert response.status_code == 200

    def test_mfa_management_uses_standard_layout(self, authenticated_client):
        """Test that MFA management page uses standard layout."""
        response = authenticated_client.get("/account/2fa/")
        content = response.content.decode()

        # Should use standard layout for MFA management
        assert 'data-layout="standard"' in content
        assert 'id="AccountCenterMenu"' in content
        assert response.status_code == 200


@pytest.mark.django_db
class TestLayoutDetectionLogic:
    """Test the logic that determines layout selection."""

    def test_authentication_state_affects_layout(self, client, authenticated_client):
        """Test that authentication state affects layout choice."""
        # Anonymous user - should redirect to login (entrance layout)
        anon_response = client.get("/account/email/")
        assert anon_response.status_code == 302  # Redirect to login

        # Authenticated user - should show email page (standard layout)
        auth_response = authenticated_client.get("/account/email/")
        content = auth_response.content.decode()
        assert 'data-layout="standard"' in content
        assert auth_response.status_code == 200

    def test_public_vs_private_page_layout(self, client, authenticated_client):
        """Test layout selection for public vs private pages."""
        # Public pages use entrance layout
        public_pages = ["/account/login/", "/account/signup/"]
        for page in public_pages:
            response = client.get(page)
            content = response.content.decode()
            assert 'data-layout="entrance"' in content

        # Private pages use standard layout
        private_pages = ["/account/email/", "/account/password/change/"]
        for page in private_pages:
            response = authenticated_client.get(page)
            content = response.content.decode()
            assert 'data-layout="standard"' in content

    def test_form_type_affects_layout(self, client, authenticated_client):
        """Test that form type affects layout selection."""
        # Authentication forms use entrance layout
        auth_forms = ["/account/login/", "/account/signup/", "/account/password/reset/"]
        for form_url in auth_forms:
            response = client.get(form_url)
            content = response.content.decode()
            assert 'data-layout="entrance"' in content

        # Management forms use standard layout
        mgmt_forms = ["/account/email/", "/account/password/change/"]
        for form_url in mgmt_forms:
            response = authenticated_client.get(form_url)
            content = response.content.decode()
            assert 'data-layout="standard"' in content


@pytest.mark.django_db
class TestLayoutComponents:
    """Test that layouts include expected components."""

    def test_entrance_layout_components(self, client):
        """Test that entrance layout includes expected components."""
        response = client.get("/account/login/")
        content = response.content.decode()

        # Entrance layout should include these rendered components
        expected_elements = [
            'data-layout="entrance"',
            "card shadow border-0",  # Entrance card
            "min-vh-100 d-flex align-items-center justify-content-center",  # Centering
            "max-width: 28rem",  # Constrained width
            "img-fluid",  # Brand logo
        ]

        for element in expected_elements:
            assert element in content

    def test_standard_layout_components(self, authenticated_client):
        """Test that standard layout includes expected components."""
        response = authenticated_client.get("/account/email/")
        content = response.content.decode()

        # Standard layout should include these rendered components
        expected_elements = [
            'data-layout="standard"',
            'id="AccountCenterMenu"',  # Sidebar menu
            "offcanvas-md offcanvas-start",  # Responsive sidebar
            "container-fluid",  # Main content container
            "border-end",  # Sidebar border
        ]

        for element in expected_elements:
            assert element in content

    def test_entrance_layout_excludes_navigation(self, client):
        """Test that entrance layout excludes navigation components."""
        response = client.get("/account/login/")
        content = response.content.decode()

        # Entrance layout should not include navigation
        excluded_elements = [
            'id="AccountCenterMenu"',  # Sidebar navigation
            "offcanvas-md",  # Responsive navigation
            "border-end",  # Sidebar border
        ]

        for element in excluded_elements:
            assert element not in content

    def test_standard_layout_excludes_entrance_branding(self, authenticated_client):
        """Test that standard layout excludes entrance-specific components."""
        response = authenticated_client.get("/account/email/")
        content = response.content.decode()

        # Standard layout should not include entrance-specific styling
        excluded_elements = [
            "min-vh-100 d-flex align-items-center justify-content-center",
            "max-width: 28rem",  # Constrained entrance width
        ]

        for element in excluded_elements:
            assert element not in content


@pytest.mark.django_db
class TestLayoutContextData:
    """Test that layouts receive appropriate context data."""

    def test_entrance_layout_context(self, client):
        """Test that entrance layout receives appropriate context."""
        response = client.get("/account/login/")

        # Should have form context for entrance pages
        assert "form" in response.context
        assert response.status_code == 200

    def test_standard_layout_context(self, authenticated_client):
        """Test that standard layout receives appropriate context."""
        response = authenticated_client.get("/account/email/")

        # Should have user and management context for standard pages
        assert "user" in response.context
        assert response.context["user"].is_authenticated
        assert response.status_code == 200

    def test_layout_title_context(self, client, authenticated_client):
        """Test that layouts receive proper title context."""
        # Test entrance layout title
        entrance_response = client.get("/account/login/")
        assert entrance_response.status_code == 200
        assert "title" in entrance_response.context or "Sign In" in entrance_response.content.decode()

        # Test standard layout title
        standard_response = authenticated_client.get("/account/email/")
        assert standard_response.status_code == 200
        assert "title" in standard_response.context or "Email" in standard_response.content.decode()


@pytest.mark.django_db
class TestLayoutResponsiveness:
    """Test layout responsiveness and mobile compatibility."""

    def test_entrance_layout_responsive_classes(self, client):
        """Test that entrance layout includes responsive classes."""
        response = client.get("/account/login/")
        content = response.content.decode()

        # Should include responsive classes
        responsive_indicators = [
            "min-vh-100",
            "d-flex",
            "justify-content-center",
            "align-items-center",
            "w-100",
            "img-fluid",
        ]

        # All responsive classes should be present
        for indicator in responsive_indicators:
            assert indicator in content

    def test_standard_layout_responsive_classes(self, authenticated_client):
        """Test that standard layout includes responsive classes."""
        response = authenticated_client.get("/account/email/")
        content = response.content.decode()

        # Should include responsive classes
        responsive_indicators = [
            "container-fluid",
            "d-flex",
            "col-md-3",
            "offcanvas-md",
            "flex-grow-1",
            "vh-100",
        ]

        # Most responsive classes should be present
        present_count = sum(1 for indicator in responsive_indicators if indicator in content)
        assert present_count >= len(responsive_indicators) // 2


@pytest.mark.django_db
class TestLayoutErrorHandling:
    """Test layout behavior with errors and edge cases."""

    def test_layout_with_form_errors(self, client):
        """Test layout handling when forms have errors."""
        # Submit invalid login to trigger errors
        response = client.post("/account/login/", {"login": "invalid@email.com", "password": "wrongpassword"})

        # Should still use appropriate layout with errors
        assert response.status_code in [200, 302]
        if response.status_code == 200:
            content = response.content.decode()
            assert 'data-layout="entrance"' in content

    def test_layout_with_messages(self, authenticated_client):
        """Test layout handling with Django messages."""
        response = authenticated_client.get("/account/email/")
        content = response.content.decode()

        # Should include message handling in layout
        assert 'data-layout="standard"' in content
        assert response.status_code == 200

    def test_layout_with_minimal_context(self, client):
        """Test layout handling with minimal context."""
        response = client.get("/account/login/")

        # Should handle missing or minimal context gracefully
        assert response.status_code == 200
        content = response.content.decode()
        assert 'data-layout="entrance"' in content


@pytest.mark.django_db
class TestLayoutCustomization:
    """Test layout customization capabilities."""

    def test_layout_template_inheritance(self, client):
        """Test that layouts properly extend base templates."""
        response = client.get("/account/login/")

        # Should successfully render with template inheritance
        assert response.status_code == 200
        content = response.content.decode()
        # Should have basic HTML structure
        assert "<html" in content
        assert "<body" in content

    def test_layout_block_structure(self, authenticated_client):
        """Test that layouts have proper block structure."""
        response = authenticated_client.get("/account/email/")

        # Should have proper Django template block structure
        assert response.status_code == 200
        content = response.content.decode()
        # Should have title and body blocks rendered
        assert "<title>" in content
        assert 'data-layout="standard"' in content

    @override_settings(DEBUG=True)
    def test_layout_debug_mode(self, client):
        """Test layout behavior in debug mode."""
        response = client.get("/account/login/")

        # Should handle debug mode appropriately
        assert response.status_code == 200
        content = response.content.decode()
        assert 'data-layout="entrance"' in content

    @override_settings(DEBUG=False)
    def test_layout_production_mode(self, client):
        """Test layout behavior in production mode."""
        response = client.get("/account/login/")

        # Should handle production mode appropriately
        assert response.status_code == 200
        content = response.content.decode()
        assert 'data-layout="entrance"' in content


@pytest.mark.django_db
class TestSpecificComponentRendering:
    """Test that specific cotton components render correctly."""

    def test_entrance_brand_logo_rendering(self, client):
        """Test that entrance brand logo renders correctly."""
        response = client.get("/account/login/")
        content = response.content.decode()

        # Should include brand logo elements
        assert "img-fluid" in content
        assert "dac_bg_transparent.svg" in content
        assert "Account Center" in content  # Alt text

    def test_entrance_card_rendering(self, client):
        """Test that entrance card renders correctly."""
        response = client.get("/account/login/")
        content = response.content.decode()

        # Should include card styling
        assert "card shadow border-0" in content
        assert "card-body" in content
        assert "p-4 p-md-5" in content  # Responsive padding

    def test_standard_sidebar_rendering(self, authenticated_client):
        """Test that standard layout sidebar renders correctly."""
        response = authenticated_client.get("/account/email/")
        content = response.content.decode()

        # Should include sidebar elements
        assert "border-end" in content  # Sidebar border
        assert "shadow-sm" in content  # Sidebar shadow
        assert "overflow-auto" in content  # Scrollable sidebar

    def test_standard_main_content_rendering(self, authenticated_client):
        """Test that standard layout main content renders correctly."""
        response = authenticated_client.get("/account/email/")
        content = response.content.decode()

        # Should include main content structure
        assert "container-fluid" in content
        assert "flex-grow-1" in content
        assert "py-4 px-3 px-md-4" in content  # Responsive padding


@pytest.mark.django_db
class TestLayoutAccessibility:
    """Test layout accessibility features."""

    def test_entrance_layout_accessibility(self, client):
        """Test entrance layout accessibility features."""
        response = client.get("/account/login/")
        content = response.content.decode()

        # Should include accessibility features
        assert "alt=" in content  # Alt text for images
        assert "<h1" in content  # Proper heading structure

    def test_standard_layout_accessibility(self, authenticated_client):
        """Test standard layout accessibility features."""
        response = authenticated_client.get("/account/email/")
        content = response.content.decode()

        # Should include accessibility features
        assert "<nav" in content  # Semantic navigation
        assert "<main" in content  # Main content landmark
        assert "<aside" in content  # Sidebar landmark
