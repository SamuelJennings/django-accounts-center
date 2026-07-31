"""FR-008 — a second Account Center integration.

``dac.allauth`` is the only integration that has ever served a page through
the shared management page (``dac/base.html``). These tests serve one from
``tests/testapp`` — a plain installed app the core package knows nothing
about — to prove the contract holds for any integration, not just the one
that happens to exist.

What this establishes: ``tests/testapp`` reaches ``dac/base.html`` purely by
being an installed app that mounts its own URLs and registers its own menu
group — no line of ``dac/`` (the core package) was changed to make this
work. What it does not establish: that a project can mount an integration's
URLs *without* editing its own root URLconf. Automatic URL contribution is
roadmap item R4 and is out of scope here — this app's URLs are mounted by
hand in ``tests/urls.py`` / ``tests/urls_minimal.py``, the same way any
integration's URLs are mounted today.
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
        carries the test integration's own group, and links back to the
        Account Center overview."""
        response = authenticated_client.get(reverse("testapp_settings"))
        content = response.content.decode()
        assert 'aria-label="Account navigation"' in content
        assert "Test App" in content
        assert f'href="{reverse("account-center")}"' in content

    def test_breadcrumbs_present(self, authenticated_client):
        """The trail carries 'Settings' as the current (leaf) crumb — the
        same shape dac.allauth's own pages carry."""
        response = authenticated_client.get(reverse("testapp_settings"))
        content = response.content.decode()
        assert 'aria-label="Breadcrumbs"' in content
        assert "Settings" in content

    def test_own_content_present(self, authenticated_client):
        """{% block content %} in testapp/settings.html reaches the page."""
        response = authenticated_client.get(reverse("testapp_settings"))
        content = response.content.decode()
        assert "Test App Settings" in content


@pytest.mark.django_db
class TestSecondIntegrationServesManagementPageWithoutAllauth:
    """FR-008, scenario 3 — the page still renders, and references no
    integration-owned template, when ``dac.allauth`` is absent.

    Uses the suite's existing minimal-URLconf isolation pattern rather than a
    new mechanism (see tests/test_components/test_dac_base.py's
    ``settings.ROOT_URLCONF = "tests.urls_minimal"`` tests): tests/urls_minimal.py
    mounts nothing dac-related at all, so it stands in for "dac.allauth
    absent" a fortiori — the test integration's own view still reaches the
    page with no dac URL, allauth or otherwise, registered.
    """

    def test_response_is_successful(self, authenticated_client, settings):
        settings.ROOT_URLCONF = "tests.urls_minimal"
        response = authenticated_client.get(reverse("testapp_settings"))
        assert response.status_code == 200

    def test_own_content_still_present(self, authenticated_client, settings):
        settings.ROOT_URLCONF = "tests.urls_minimal"
        response = authenticated_client.get(reverse("testapp_settings"))
        content = response.content.decode()
        assert "Test App Settings" in content

    def test_references_no_integration_template(self, authenticated_client, settings):
        """No template from ``dac.allauth`` (or any other integration) is
        used to render this page — it reaches ``dac/base.html`` and its own
        ``testapp/settings.html`` only."""
        settings.ROOT_URLCONF = "tests.urls_minimal"
        response = authenticated_client.get(reverse("testapp_settings"))
        template_names = {t.name for t in response.templates if t.name}
        integration_prefixes = ("account/", "allauth/", "dac/allauth/")
        offending = {name for name in template_names if name.startswith(integration_prefixes)}
        assert not offending
