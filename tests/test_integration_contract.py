"""FR-008 — a second Account Center integration.

``dac.allauth`` is the only integration that has ever served a page through
the shared management page (``dac/base.html``). These tests serve one from
``tests/testapp`` — a plain installed app the core package knows nothing
about — to prove the contract holds for any integration, not just the one
that happens to exist.
"""

import pytest
from django.urls import reverse


@pytest.mark.django_db
class TestSecondIntegrationServesManagementPage:
    """FR-008, scenario 1 — the test integration's own management view
    renders through the shared management page carrying the sub menu, the
    breadcrumbs and its own content."""

    def test_response_is_successful(self, authenticated_client):
        response = authenticated_client.get(reverse("testapp_settings"))
        assert response.status_code == 200

    def test_sub_menu_present(self, authenticated_client):
        """The Account Center sub menu (dac/base.html's own aside) renders,
        and it carries the test integration's own group."""
        response = authenticated_client.get(reverse("testapp_settings"))
        content = response.content.decode()
        assert 'aria-label="Account navigation"' in content
        assert "Test App" in content

    def test_breadcrumbs_present(self, authenticated_client):
        """The trail is 'Account Center' (link) -> 'Settings' (current, plain
        text) — the same shape dac.allauth's own pages carry."""
        response = authenticated_client.get(reverse("testapp_settings"))
        content = response.content.decode()
        assert 'aria-label="Breadcrumbs"' in content
        assert f'href="{reverse("account-center")}"' in content
        assert "Settings" in content

    def test_own_content_present(self, authenticated_client):
        """{% block content %} in testapp/settings.html reaches the page."""
        response = authenticated_client.get(reverse("testapp_settings"))
        content = response.content.decode()
        assert "Test App Settings" in content
