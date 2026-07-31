"""Breadcrumb resolution independent of a hidden entry's visibility.

``dac.menus.get_active_section`` names the current page's section for the
breadcrumb (``dac/base.html``). FR-006a requires that naming to survive a
menu entry hidden from the person viewing it — hiding is presentation only,
and the page frame around a hidden entry's own page must render exactly as
it does for anyone else. See specs/013-account-center-menu/research.md R2.
"""

import pytest
from django.urls import reverse


@pytest.mark.django_db
class TestBreadcrumbSurvivesHiddenEntry:
    def test_section_page_breadcrumb_survives_hidden_entry(self, ungated_client):
        """The gated entry's own page still carries its section breadcrumb
        for the person the entry is hidden from."""
        response = ungated_client.get(reverse("testapp_gated"))
        content = response.content.decode()
        assert 'aria-label="Breadcrumbs"' in content
        assert "Gated" in content

    def test_subpage_breadcrumb_survives_hidden_entry(self, ungated_client):
        """A sub-page of the hidden entry's section still names the section
        and links back to it, for the person the entry is hidden from."""
        response = ungated_client.get(reverse("testapp_gated_sub"))
        content = response.content.decode()
        assert 'aria-label="Breadcrumbs"' in content
        assert "Gated" in content
        assert f'href="{reverse("testapp_gated")}"' in content
