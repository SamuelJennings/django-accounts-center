"""Breadcrumb resolution independent of a hidden entry's visibility.

``dac.menus.get_active_section`` names the current page's section for the
breadcrumb (``dac/base.html``). FR-006a requires that naming to survive a
menu entry hidden from the person viewing it — hiding is presentation only,
and the page frame around a hidden entry's own page must render exactly as
it does for anyone else. See specs/013-account-center-menu/research.md R2.
"""

import pytest
from bs4 import BeautifulSoup
from django.urls import reverse


def _menu_labels(response):
    """The set of menu-entry labels rendered in the Account Center nav.

    Every entry and group heading renders its label inside a ``<span>``
    within ``<aside aria-label="Account navigation">`` (mvp's
    ``cotton/menu/item.html`` and ``cotton/menu/group.html``) — one ``aside``
    holds both the mobile dropdown and the desktop card, so this counts each
    label once regardless of which of the two render sites shows it.
    """
    soup = BeautifulSoup(response.content, "html.parser")
    aside = soup.find("aside", attrs={"aria-label": "Account navigation"})
    return {span.get_text(strip=True) for span in aside.find_all("span")}


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


@pytest.mark.django_db
class TestMenuDiffersByPerson:
    def test_menu_differs_in_exactly_the_gated_entry(self, gated_client, ungated_client):
        """Two people with the same installed apps read menus that differ in
        exactly the entry the visibility check applies to, and nothing else."""
        gated_labels = _menu_labels(gated_client.get(reverse("account-center")))
        ungated_labels = _menu_labels(ungated_client.get(reverse("account-center")))

        assert "Gated" in gated_labels
        assert "Gated" not in ungated_labels
        assert gated_labels - ungated_labels == {"Gated"}
        assert ungated_labels - gated_labels == set()
