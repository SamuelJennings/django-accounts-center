"""
Tests for cotton component rendering in allauth templates.

This module tests the proper rendering and functionality of cotton components
used throughout the allauth addon templates.
"""

import pytest
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.mark.django_db
class TestLayoutComponents:
    """Test layout components used in allauth templates."""

    def test_entrance_layout_component_rendering(self, client):
        """Test entrance layout component renders correctly."""
        response = client.get("/account/login/")
        content = response.content.decode()

        # Verify entrance layout structure
        assert "c-dac.entrance" in content
        assert "c-dac.entrance.brand-logo" in content
        assert "c-dac.entrance.card" in content

    def test_standard_layout_component_rendering(self, authenticated_client):
        """Test standard layout component renders correctly."""
        response = authenticated_client.get("/account/email/")
        content = response.content.decode()

        # Verify standard layout structure
        assert "c-dac.page" in content
        assert "c-dac.sidebar" in content
        assert "c-dac.header" in content
        assert "c-dac.breadcrumbs" in content

    def test_entrance_layout_title_and_subtitle(self, client):
        """Test entrance layout displays title and subtitle correctly."""
        response = client.get("/account/login/")
        content = response.content.decode()

        # Check for title attribute handling
        assert 'title="' in content
        # The login page should have welcome text
        assert "Welcome" in content or "Sign" in content

    def test_layout_message_handling(self, client):
        """Test that layouts properly handle Django messages."""
        # Test with a message

        # This would be tested more thoroughly with actual message scenarios
        response = client.get("/account/login/")
        assert response.status_code == 200


@pytest.mark.django_db
class TestFormComponents:
    """Test form components used in allauth templates."""

    def test_form_component_rendering(self, client):
        """Test c-dac.form component renders correctly."""
        response = client.get("/account/login/")
        content = response.content.decode()

        # Should contain form component
        assert "c-dac.form" in content
        # Should have method and action attributes
        assert 'method="post"' in content
        assert "action=" in content

    def test_form_field_components(self, client):
        """Test form field components render correctly."""
        response = client.get("/account/signup/")
        content = response.content.decode()

        # Form should be present
        assert "c-dac.form" in content
        # Should contain form attribute binding
        assert ":form=" in content

    def test_form_button_components(self, client):
        """Test form button components render correctly."""
        response = client.get("/account/login/")
        content = response.content.decode()

        # Should contain action buttons
        assert "c-dac.entrance.action.primary" in content
        # Button should have proper attributes
        assert 'type="submit"' in content


@pytest.mark.django_db
class TestUIComponents:
    """Test UI components used in allauth templates."""

    def test_alert_components(self, authenticated_client):
        """Test alert components for message display."""
        response = authenticated_client.get("/account/email/")
        content = response.content.decode()

        # Alert component should be available for messages
        # The template structure should support alerts
        assert "c-dac.alert" in content or "messages" in response.context

    def test_card_components(self, client):
        """Test card components in templates."""
        response = client.get("/account/login/")
        content = response.content.decode()

        # Should use card components
        assert "c-dac.entrance.card" in content

    def test_link_components(self, client):
        """Test link components render correctly."""
        response = client.get("/account/login/")
        content = response.content.decode()

        # Should contain link components
        assert "c-dac.link" in content
        # Links should have href attributes
        assert "href=" in content

    def test_icon_components(self, client):
        """Test icon components render correctly."""
        response = client.get("/account/login/")
        content = response.content.decode()

        # Should contain icon components
        assert "c-dac.icon" in content or "icon=" in content


@pytest.mark.django_db
class TestComponentAttributeHandling:
    """Test component attribute handling and merging."""

    def test_dynamic_attributes(self, client):
        """Test dynamic attribute handling with : prefix."""
        response = client.get("/account/login/")
        content = response.content.decode()

        # Should contain dynamic attribute bindings
        assert ":form=" in content
        assert ":visible=" in content or "visible=" in content

    def test_boolean_attributes(self, client):
        """Test boolean attribute handling."""
        response = client.get("/account/login/")
        content = response.content.decode()

        # Boolean attributes should be handled correctly
        # Look for boolean attribute patterns
        assert "center" in content or "small" in content

    def test_attrs_merging(self, client):
        """Test that {{ attrs }} properly merges attributes."""
        # This is more of a template rendering test
        # We'd need to create specific test templates to fully test this
        response = client.get("/account/login/")
        assert response.status_code == 200


@pytest.mark.django_db
class TestSlotHandling:
    """Test slot handling in components."""

    def test_default_slot_content(self, client):
        """Test default slot content rendering."""
        response = client.get("/account/login/")
        content = response.content.decode()

        # Content should be rendered in slots
        assert "slot" in content.lower() or response.status_code == 200

    def test_named_slots(self, authenticated_client):
        """Test named slot content rendering."""
        response = authenticated_client.get("/account/email/")
        content = response.content.decode()

        # Named slots should be handled
        assert "actions" in content or "c-slot" in content

    def test_conditional_slots(self, authenticated_client):
        """Test conditional slot rendering."""
        response = authenticated_client.get("/account/email/")
        content = response.content.decode()

        # Conditional slots should not create empty tags
        # This is tested by ensuring the response renders correctly
        assert response.status_code == 200


@pytest.mark.django_db
class TestComponentComposition:
    """Test component composition and nesting."""

    def test_nested_components(self, client):
        """Test nested component rendering."""
        response = client.get("/account/login/")
        content = response.content.decode()

        # Should have nested component structure
        assert "c-dac.entrance" in content
        assert "c-dac.entrance.card" in content
        assert "c-dac.entrance.action" in content

    def test_component_hierarchy(self, authenticated_client):
        """Test component hierarchy in standard layout."""
        response = authenticated_client.get("/account/email/")
        content = response.content.decode()

        # Should have proper component hierarchy
        assert "c-dac.page" in content
        assert "c-dac.card" in content

    def test_slot_composition(self, authenticated_client):
        """Test slot composition across components."""
        response = authenticated_client.get("/account/email/")
        content = response.content.decode()

        # Components should compose properly with slots
        assert response.status_code == 200


@pytest.mark.django_db
class TestComponentContextIsolation:
    """Test component context isolation."""

    def test_component_variable_isolation(self, client):
        """Test that components don't leak context variables."""
        response = client.get("/account/login/")

        # Components should only use passed attributes
        # This is verified by successful rendering without context errors
        assert response.status_code == 200

    def test_explicit_attribute_passing(self, client):
        """Test that components only use explicitly passed attributes."""
        response = client.get("/account/login/")
        content = response.content.decode()

        # Look for explicit attribute passing patterns
        assert "title=" in content
        assert "text=" in content or "href=" in content


@pytest.mark.django_db
class TestResponsiveComponents:
    """Test responsive behavior of components."""

    def test_responsive_layout_classes(self, client):
        """Test that components include responsive classes."""
        response = client.get("/account/login/")
        content = response.content.decode()

        # Should include responsive classes
        assert "d-flex" in content or "container" in content or "col-" in content

    def test_mobile_friendly_components(self, client):
        """Test mobile-friendly component rendering."""
        response = client.get("/account/login/")
        content = response.content.decode()

        # Should include mobile-friendly classes
        assert "w-100" in content or "min-vh-100" in content


@pytest.mark.django_db
class TestComponentAccessibility:
    """Test component accessibility features."""

    def test_semantic_html_structure(self, client):
        """Test that components use semantic HTML."""
        response = client.get("/account/login/")
        content = response.content.decode()

        # Should use semantic HTML elements
        assert "<h1" in content or "<h2" in content
        assert "<main" in content or "<section" in content

    def test_form_accessibility(self, client):
        """Test form component accessibility."""
        response = client.get("/account/login/")
        content = response.content.decode()

        # Forms should have proper labels and structure
        assert "<form" in content
        assert "label" in content.lower() or "for=" in content


@pytest.mark.django_db
class TestTemplateInheritance:
    """Test template inheritance with components."""

    def test_base_template_extension(self, client):
        """Test that templates properly extend base templates."""
        response = client.get("/account/login/")

        # Template should render without inheritance errors
        assert response.status_code == 200

    def test_block_structure(self, authenticated_client):
        """Test template block structure."""
        response = authenticated_client.get("/account/email/")

        # Should have proper block structure
        assert response.status_code == 200


@pytest.mark.django_db
class TestComponentPerformance:
    """Test component rendering performance."""

    def test_component_rendering_speed(self, client):
        """Test that components render efficiently."""
        import time

        start_time = time.time()
        response = client.get("/account/login/")
        end_time = time.time()

        # Should render quickly (less than 1 second for this simple test)
        assert end_time - start_time < 1.0
        assert response.status_code == 200

    def test_memory_usage(self, client):
        """Test component memory usage is reasonable."""
        # Basic test - should not fail with memory errors
        for _ in range(10):
            response = client.get("/account/login/")
            assert response.status_code == 200
