"""
Tests for django-accounts-center template tags.
"""

from unittest.mock import Mock, patch

from django.template import Context
from django.test import TestCase, override_settings

from dac.templatetags.dac import get_setting, render_form


class TestDACTemplateTags(TestCase):
    """Tests for DAC template tags."""

    def test_get_setting_existing(self):
        """Test get_setting returns existing setting value."""
        with override_settings(TEST_SETTING="test_value"):
            result = get_setting("TEST_SETTING")
            assert result == "test_value"

    def test_get_setting_missing_with_default(self):
        """Test get_setting returns default for missing setting."""
        result = get_setting("NON_EXISTENT_SETTING", "default_value")
        assert result == "default_value"

    def test_get_setting_missing_without_default(self):
        """Test get_setting returns None for missing setting without default."""
        result = get_setting("NON_EXISTENT_SETTING")
        assert result is None

    def test_render_form_with_helper(self):
        """Test render_form with form that has helper."""
        # Create a mock form with helper
        mock_form = Mock()
        mock_helper = Mock()
        mock_helper.form_id = "existing_id"
        mock_helper.attrs = {}
        mock_form.helper = mock_helper
        mock_form.__class__.__name__ = "TestForm"

        context = Context({})

        with patch("dac.templatetags.dac.CrispyFormNode") as mock_crispy_node:
            mock_node = Mock()
            mock_crispy_node.return_value = mock_node
            mock_node.render.return_value = "<form>...</form>"

            result = render_form(context, mock_form, action="/test/")

            # Verify helper attributes were set
            assert mock_helper.attrs == {"action": "/test/"}
            assert context["form"] == mock_form
            assert context["helper"] == mock_helper

    def test_render_form_without_helper(self):
        """Test render_form with form that doesn't have helper."""
        # Create a mock form without helper
        mock_form = Mock()
        mock_form.helper = None
        mock_form.__class__.__name__ = "TestForm"

        context = Context({})

        with patch("dac.templatetags.dac.FormHelper") as mock_form_helper:
            with patch("dac.templatetags.dac.CrispyFormNode") as mock_crispy_node:
                mock_helper = Mock()
                mock_helper.form_id = None
                mock_form_helper.return_value = mock_helper

                mock_node = Mock()
                mock_crispy_node.return_value = mock_node
                mock_node.render.return_value = "<form>...</form>"

                result = render_form(context, mock_form, method="post")

                # Verify helper was created and form_id was set
                mock_form_helper.assert_called_once()
                assert mock_helper.form_id == "testform"
                assert mock_helper.attrs == {"method": "post"}

    def test_render_form_form_id_generation(self):
        """Test that form ID is generated correctly from class name."""
        mock_form = Mock()
        mock_form.helper = None
        mock_form.__class__.__name__ = "MyComplexFormName"

        context = Context({})

        with patch("dac.templatetags.dac.FormHelper") as mock_form_helper:
            with patch("dac.templatetags.dac.CrispyFormNode") as mock_crispy_node:
                mock_helper = Mock()
                mock_helper.form_id = None
                mock_form_helper.return_value = mock_helper

                mock_node = Mock()
                mock_crispy_node.return_value = mock_node
                mock_node.render.return_value = "<form>...</form>"

                render_form(context, mock_form)

                # Verify form_id is lowercase class name
                assert mock_helper.form_id == "mycomplexformname"
