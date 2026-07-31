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
    """FR-002: the visibility check an integration declares is asked on every
    request, not once when the menu is built. ``AccountCenterMenu`` is
    assembled at import, so the answer must not be captured at import, at
    sign-in, or in any cache in between. Not tested here: that ``check`` is
    called or that a false result hides an item — that is flex-menus' own
    behaviour (tasks.md Phase 3, "Not tested here"). That an entry is present
    for one person and absent for another is TestMenuDiffersByPerson.
    """

    def test_check_is_asked_again_when_the_answer_changes(self, ungated_client, ungated_person):
        """The same signed-in person, unchanged session, reads a different
        menu once the fact their entry's check consults changes."""
        from django.contrib.auth.models import Group

        from tests.testapp.menus import GATED_GROUP_NAME

        assert "Gated" not in _menu_labels(ungated_client.get(reverse("account-center")))

        group, _ = Group.objects.get_or_create(name=GATED_GROUP_NAME)
        ungated_person.groups.add(group)

        assert "Gated" in _menu_labels(ungated_client.get(reverse("account-center")))


@pytest.mark.django_db
class TestAllauthEntriesUnchanged:
    """FR-007: dac.allauth's own entries continue to appear exactly as they
    did before this feature, for a signed-in person. dac.allauth contributes
    no visibility check on any of its entries, so this is US-1's compatibility
    guarantee (FR-005) exercised against the one real integration shipped in
    this repo, not the test integration."""

    def test_allauth_entries_render_as_before(self, authenticated_client):
        response = authenticated_client.get(reverse("account-center"))
        labels = _menu_labels(response)
        assert {
            "Email",
            "Password",
            "Connected accounts",
            "Two-factor authentication",
            "Sessions",
        } <= labels


@pytest.mark.django_db
class TestUngatedEntryStaysVisible:
    """FR-005: an entry contributed with no visibility check stays visible
    whenever its integration is installed, regardless of who is looking —
    declaring a check is optional, and silence means visible."""

    def test_ungated_entry_present_for_both_people(self, gated_client, ungated_client):
        gated_labels = _menu_labels(gated_client.get(reverse("account-center")))
        ungated_labels = _menu_labels(ungated_client.get(reverse("account-center")))
        assert "Ungated" in gated_labels
        assert "Ungated" in ungated_labels


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
