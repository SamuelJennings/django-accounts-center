"""
Corrected tests for layout detection with proper URLs and ID-based checking.
"""

import pytest
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.mark.django_db
class TestLayoutDetection:
    """Test that correct layouts are used for different page types."""

    def test_login_page_uses_entrance_layout(self, client):
        """Test that login page uses entrance layout."""
        response = client.get("/account-center/account/login/")
        assert response.status_code == 200
        content = response.content.decode()

        # Should use entrance layout
        assert 'id="dac-entrance-layout"' in content
        assert "min-vh-100 d-flex align-items-center justify-content-center" in content
        assert "max-width: 28rem" in content

    def test_signup_page_uses_entrance_layout(self, client):
        """Test that signup page uses entrance layout."""
        response = client.get("/account-center/account/signup/")
        assert response.status_code == 200
        content = response.content.decode()

        # Should use entrance layout
        assert 'id="dac-entrance-layout"' in content
        assert "min-vh-100 d-flex align-items-center justify-content-center" in content

    def test_password_reset_uses_entrance_layout(self, client):
        """Test that password reset page uses entrance layout."""
        response = client.get("/account-center/account/password/reset/")
        assert response.status_code == 200
        content = response.content.decode()

        # Should use entrance layout
        assert 'id="dac-entrance-layout"' in content

    def test_account_center_home_uses_standard_layout(self, authenticated_client):
        """Test that account center home uses standard layout."""
        response = authenticated_client.get("/account-center/")
        assert response.status_code == 200
        content = response.content.decode()

        # Should use standard layout
        assert 'id="dac-standard-layout"' in content
        assert 'id="mainMenu"' in content

    def test_email_management_uses_standard_layout(self, authenticated_client):
        """Test that email management page uses standard layout."""
        response = authenticated_client.get("/account-center/account/email/")
        assert response.status_code == 200
        content = response.content.decode()

        # Should use standard layout
        assert 'id="dac-standard-layout"' in content
        assert 'id="mainMenu"' in content

    def test_password_change_uses_standard_layout(self, authenticated_client):
        """Test that password change page uses standard layout."""
        response = authenticated_client.get("/account-center/account/password/change/")
        assert response.status_code == 200
        content = response.content.decode()

        # Should use standard layout
        assert 'id="dac-standard-layout"' in content

    def test_anonymous_user_redirected_from_protected_pages(self, client):
        """Test that anonymous users are redirected from protected pages."""
        protected_urls = [
            "/account-center/account/email/",
            "/account-center/account/password/change/",
        ]

        for url in protected_urls:
            response = client.get(url)
            # Should redirect to login
            assert response.status_code == 302
            assert "login" in response.url

    def test_layout_excludes_opposite_components(self, client, authenticated_client):
        """Test that entrance layout excludes standard components and vice versa."""
        # Test entrance layout excludes standard components
        entrance_response = client.get("/account-center/account/login/")
        entrance_content = entrance_response.content.decode()

        assert 'id="dac-entrance-layout"' in entrance_content
        assert 'id="mainMenu"' not in entrance_content  # Should not have sidebar
        assert "offcanvas-md" not in entrance_content

        # Test standard layout excludes entrance components
        standard_response = authenticated_client.get("/account-center/")
        standard_content = standard_response.content.decode()

        assert 'id="dac-standard-layout"' in standard_content
        assert "max-width: 28rem" not in standard_content  # Should not have constrained width


@pytest.mark.django_db
class TestComponentRendering:
    """Test that specific components render correctly."""

    def test_entrance_layout_renders_brand_logo(self, client):
        """Test that entrance layout includes brand logo."""
        response = client.get("/account-center/account/login/")
        content = response.content.decode()

        # Should include brand logo
        assert "img-fluid" in content
        assert "dac_bg_transparent.svg" in content

    def test_entrance_layout_renders_card(self, client):
        """Test that entrance layout includes card styling."""
        response = client.get("/account-center/account/login/")
        content = response.content.decode()

        # Should include card styling
        assert "card shadow border-0" in content
        assert "card-body" in content

    def test_standard_layout_renders_sidebar(self, authenticated_client):
        """Test that standard layout includes sidebar."""
        response = authenticated_client.get("/account-center/")
        content = response.content.decode()

        # Should include sidebar elements
        assert 'id="mainMenu"' in content
        assert "offcanvas-md offcanvas-start" in content

    def test_form_rendering_in_layouts(self, client):
        """Test that forms render correctly in layouts."""
        response = client.get("/account-center/account/login/")
        content = response.content.decode()

        # Should include form elements
        assert "<form" in content
        assert 'name="login"' in content or 'id="id_login"' in content
        assert 'name="password"' in content or 'id="id_password"' in content


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
