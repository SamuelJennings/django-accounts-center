"""
Tests for layout type detection in allauth templates.

This module tests that allauth URLs properly resolve with expected template layouts
(standard or entrance) and that conditionals within templates work correctly.
"""

import pytest
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.mark.django_db
class TestEntranceLayoutDetection:
    """Test detection and usage of entrance layout for authentication pages."""

    def test_login_page_uses_entrance_layout(self, client):
        """Test that login page uses entrance layout."""
        response = client.get("/account-center/account/login/")
        assert response.status_code == 200
        content = response.content.decode()

        # Check for entrance layout ID
        assert 'id="dac-entrance-layout"' in content
        # Check for entrance layout specific styling
        assert "min-vh-100 d-flex align-items-center justify-content-center" in content
        assert "max-width: 28rem" in content

    def test_signup_page_uses_entrance_layout(self, client):
        """Test that signup page uses entrance layout."""
        response = client.get("/account-center/account/signup/")
        assert response.status_code == 200
        content = response.content.decode()

        assert 'id="dac-entrance-layout"' in content
        assert "min-vh-100 d-flex align-items-center justify-content-center" in content

    def test_password_reset_uses_entrance_layout(self, client):
        """Test that password reset page uses entrance layout."""
        response = client.get("/account-center/account/password/reset/")
        assert response.status_code == 200
        content = response.content.decode()

        assert 'id="dac-entrance-layout"' in content

    def test_logout_confirmation_uses_entrance_layout(self, authenticated_client):
        """Test that logout confirmation page uses entrance layout."""
        response = authenticated_client.get("/account-center/account/logout/")
        # May redirect or show confirmation
        assert response.status_code in [200, 302]
        if response.status_code == 200:
            content = response.content.decode()
            assert 'id="dac-entrance-layout"' in content


@pytest.mark.django_db
class TestStandardLayoutDetection:
    """Test detection and usage of standard layout for account management pages."""

    def test_account_center_home_uses_standard_layout(self, authenticated_client):
        """Test that account center home uses standard layout."""
        response = authenticated_client.get("/account-center/")
        assert response.status_code == 200
        content = response.content.decode()

        assert 'id="dac-standard-layout"' in content
        assert 'id="AccountCenterMenu"' in content

    def test_email_management_uses_standard_layout(self, authenticated_client):
        """Test that email management page uses standard layout."""
        response = authenticated_client.get("/account-center/account/email/")
        assert response.status_code == 200
        content = response.content.decode()

        assert 'id="dac-standard-layout"' in content
        assert 'id="AccountCenterMenu"' in content

    def test_password_change_uses_standard_layout(self, authenticated_client):
        """Test that password change page uses standard layout."""
        response = authenticated_client.get("/account-center/account/password/change/")
        assert response.status_code == 200
        content = response.content.decode()

        assert 'id="dac-standard-layout"' in content

    def test_social_connections_uses_standard_layout(self, authenticated_client):
        """Test that social connections page uses standard layout."""
        response = authenticated_client.get("/account-center/account/social/connections/")
        assert response.status_code in [200, 404]  # 404 if social auth not fully configured
        if response.status_code == 200:
            content = response.content.decode()
            assert 'id="dac-standard-layout"' in content


@pytest.mark.django_db
class TestLayoutAuthentication:
    """Test layout behavior based on authentication state."""

    def test_anonymous_user_redirected_from_protected_pages(self, client):
        """Test that anonymous users are redirected from protected pages."""
        protected_urls = [
            "/account-center/",
            "/account-center/account/email/",
            "/account-center/account/password/change/",
        ]

        for url in protected_urls:
            response = client.get(url)
            assert response.status_code == 302
            assert "login" in response.url

    def test_authenticated_user_access_to_account_pages(self, authenticated_client):
        """Test that authenticated users can access account management pages."""
        response = authenticated_client.get("/account-center/account/email/")
        assert response.status_code == 200
        content = response.content.decode()
        assert 'id="dac-standard-layout"' in content

    def test_layout_excludes_opposite_components(self, client, authenticated_client):
        """Test that layouts exclude components from the other layout type."""
        # Entrance layout should not have sidebar
        entrance_response = client.get("/account-center/account/login/")
        entrance_content = entrance_response.content.decode()
        assert 'id="dac-entrance-layout"' in entrance_content
        assert 'id="AccountCenterMenu"' not in entrance_content

        # Standard layout should not have entrance constraints
        standard_response = authenticated_client.get("/account-center/")
        standard_content = standard_response.content.decode()
        assert 'id="dac-standard-layout"' in standard_content
        assert "max-width: 28rem" not in standard_content


@pytest.mark.django_db
class TestComponentRendering:
    """Test that cotton components render correctly in layouts."""

    def test_entrance_layout_renders_brand_logo(self, client):
        """Test that entrance layout includes brand logo component."""
        response = client.get("/account-center/account/login/")
        content = response.content.decode()

        # Brand logo should be rendered
        assert "img-fluid" in content
        assert "dac_bg_transparent.svg" in content or "Account Center" in content

    def test_entrance_layout_renders_card(self, client):
        """Test that entrance layout includes card component."""
        response = client.get("/account-center/account/login/")
        content = response.content.decode()

        # Card styling should be present
        assert "card shadow border-0" in content
        assert "card-body" in content

    def test_standard_layout_renders_sidebar(self, authenticated_client):
        """Test that standard layout includes sidebar component."""
        response = authenticated_client.get("/account-center/")
        content = response.content.decode()

        # Sidebar should be present
        assert 'id="AccountCenterMenu"' in content
        assert "offcanvas-md offcanvas-start" in content

    def test_standard_layout_renders_header(self, authenticated_client):
        """Test that standard layout includes header component."""
        response = authenticated_client.get("/account-center/")
        content = response.content.decode()

        # Header should be present (main content container)
        assert "container-fluid" in content

    def test_form_rendering_in_entrance_layout(self, client):
        """Test that forms render correctly in entrance layout."""
        response = client.get("/account-center/account/login/")
        content = response.content.decode()

        # Login form should be present
        assert "<form" in content
        # Common form field names/IDs
        form_indicators = ['name="login"', 'id="id_login"', 'name="password"', 'id="id_password"']
        assert any(indicator in content for indicator in form_indicators)


@pytest.mark.django_db
class TestResponsiveDesign:
    """Test responsive design elements in layouts."""

    def test_entrance_layout_responsive_classes(self, client):
        """Test that entrance layout includes responsive classes."""
        response = client.get("/account-center/account/login/")
        content = response.content.decode()

        responsive_classes = [
            "min-vh-100",
            "d-flex",
            "align-items-center",
            "justify-content-center",
            "w-100",
        ]

        for css_class in responsive_classes:
            assert css_class in content

    def test_standard_layout_responsive_classes(self, authenticated_client):
        """Test that standard layout includes responsive classes."""
        response = authenticated_client.get("/account-center/")
        content = response.content.decode()

        responsive_classes = [
            "d-flex",
            "offcanvas-md",
            "col-md-3",
            "container-fluid",
        ]

        for css_class in responsive_classes:
            assert css_class in content


@pytest.mark.django_db
class TestErrorHandling:
    """Test layout behavior with errors and edge cases."""

    def test_layout_with_form_errors(self, client):
        """Test layout handling when forms have errors."""
        # Submit invalid login to trigger errors
        response = client.post(
            "/account-center/account/login/", {"login": "invalid@email.com", "password": "wrongpassword"}
        )

        # Should still use entrance layout even with errors
        assert response.status_code in [200, 302]
        if response.status_code == 200:
            content = response.content.decode()
            assert 'id="dac-entrance-layout"' in content

    def test_layout_with_django_messages(self, authenticated_client):
        """Test layout handling with Django messages."""
        response = authenticated_client.get("/account-center/")
        content = response.content.decode()

        # Should include standard layout with message handling capability
        assert 'id="dac-standard-layout"' in content
        assert response.status_code == 200


@pytest.mark.django_db
class TestTemplateInheritance:
    """Test that layouts properly extend base templates."""

    def test_entrance_layout_extends_base(self, client):
        """Test that entrance layout properly extends base template."""
        response = client.get("/account-center/account/login/")
        content = response.content.decode()

        # Should have basic HTML structure
        assert "<html" in content
        assert "<body" in content
        assert "<title>" in content

    def test_standard_layout_extends_base(self, authenticated_client):
        """Test that standard layout properly extends base template."""
        response = authenticated_client.get("/account-center/")
        content = response.content.decode()

        # Should have basic HTML structure
        assert "<html" in content
        assert "<body" in content
        assert "<title>" in content


@pytest.mark.django_db
class TestAccessibilityFeatures:
    """Test layout accessibility features."""

    def test_entrance_layout_accessibility(self, client):
        """Test entrance layout accessibility features."""
        response = client.get("/account-center/account/login/")
        content = response.content.decode()

        # Should include accessibility features
        accessibility_indicators = [
            "alt=",  # Alt text for images
            "<h1",  # Proper heading structure
        ]

        # At least some accessibility features should be present
        assert any(indicator in content for indicator in accessibility_indicators)

    def test_standard_layout_accessibility(self, authenticated_client):
        """Test standard layout accessibility features."""
        response = authenticated_client.get("/account-center/")
        content = response.content.decode()

        # Should include semantic HTML
        semantic_elements = [
            "<nav",  # Semantic navigation
            "<main",  # Main content landmark
            "<aside",  # Sidebar landmark
        ]

        # At least some semantic elements should be present
        assert any(element in content for element in semantic_elements)


@pytest.mark.django_db
class TestUrlPatterns:
    """Test that allauth URL patterns resolve correctly."""

    def test_login_url_resolves(self, client):
        """Test that login URL resolves correctly."""
        response = client.get("/account-center/account/login/")
        assert response.status_code == 200

    def test_signup_url_resolves(self, client):
        """Test that signup URL resolves correctly."""
        response = client.get("/account-center/account/signup/")
        assert response.status_code == 200

    def test_password_reset_url_resolves(self, client):
        """Test that password reset URL resolves correctly."""
        response = client.get("/account-center/account/password/reset/")
        assert response.status_code == 200

    def test_protected_urls_require_authentication(self, client):
        """Test that protected URLs redirect unauthenticated users."""
        protected_urls = [
            "/account-center/",
            "/account-center/account/email/",
            "/account-center/account/password/change/",
        ]

        for url in protected_urls:
            response = client.get(url)
            assert response.status_code == 302
            assert "login" in response.url

    def test_authenticated_urls_work(self, authenticated_client):
        """Test that authenticated URLs work for logged-in users."""
        authenticated_urls = [
            "/account-center/",
            "/account-center/account/email/",
            "/account-center/account/password/change/",
        ]

        for url in authenticated_urls:
            response = authenticated_client.get(url)
            assert response.status_code == 200
