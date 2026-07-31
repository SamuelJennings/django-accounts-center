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
    nested in an ``<li>`` within ``<aside aria-label="Account navigation">``
    (mvp's ``cotton/menu/item.html`` and ``cotton/menu/group.html``) — one
    ``aside`` holds both the mobile dropdown and the desktop card, so this
    counts each label once regardless of which of the two render sites shows
    it. The ``<li>`` filter excludes the mobile dropdown's own toggle button,
    which also carries a ``<span>`` with the active section's label
    (``dac/base.html``'s ``account_section`` mobile button, FR-006a) but is
    not itself a menu entry.
    """
    soup = BeautifulSoup(response.content, "html.parser")
    aside = soup.find("aside", attrs={"aria-label": "Account navigation"})
    return {span.get_text(strip=True) for span in aside.find_all("span") if span.find_parent("li")}


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


@pytest.mark.django_db
class TestGatedEntryVisibilityCheck:
    """FR-001, FR-002, FR-003: the developer-facing contract US-1 rests on —
    an integration attaches a visibility check to a menu entry, and the
    Account Center asks it per request for whoever is looking. Not tested
    here: that ``check`` is called or that a false result hides an item —
    that is flex-menus' own behaviour (tasks.md Phase 3, "Not tested here").
    """

    def test_gated_entry_present_for_the_person_it_applies_to(self, gated_client):
        response = gated_client.get(reverse("account-center"))
        assert "Gated" in _menu_labels(response)

    def test_gated_entry_absent_for_the_person_it_does_not_apply_to(self, ungated_client):
        response = ungated_client.get(reverse("account-center"))
        assert "Gated" not in _menu_labels(response)


@pytest.mark.django_db
class TestPageUnaffectedByHiddenEntry:
    def test_other_entries_content_and_messages_render_the_same(self, gated_client, ungated_client):
        """The gated entry's own page renders the same for the person it is
        hidden from as for the person it applies to, apart from that one
        entry (FR-006): the other menu entries, the content region and the
        messages region are unaffected."""
        gated_response = gated_client.get(reverse("testapp_gated"))
        ungated_response = ungated_client.get(reverse("testapp_gated"))

        assert _menu_labels(gated_response) - {"Gated"} == _menu_labels(ungated_response)

        gated_soup = BeautifulSoup(gated_response.content, "html.parser")
        ungated_soup = BeautifulSoup(ungated_response.content, "html.parser")

        gated_h1 = gated_soup.find("h1")
        ungated_h1 = ungated_soup.find("h1")
        assert gated_h1 is not None
        assert gated_h1.get_text(strip=True) == "Test App Settings"
        assert ungated_h1 is not None
        assert ungated_h1.get_text(strip=True) == gated_h1.get_text(strip=True)

        gated_messages = gated_soup.find("div", class_="toast")
        ungated_messages = ungated_soup.find("div", class_="toast")
        assert gated_messages is not None
        assert ungated_messages is not None
        assert str(gated_messages) == str(ungated_messages)
