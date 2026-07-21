"""Breadcrumb rendering on Account Center pages.

dac/base.html renders an "Account Center → <section>" trail derived from
AccountCenterMenu (dac.menus.get_active_section): the section crumb is plain
text on the section page itself and a link on sub-pages; the overview page
renders no breadcrumbs at all.
"""

import pytest
from django.urls import reverse

from tests.factories import UserFactory


@pytest.mark.django_db
class TestAccountBreadcrumbs:
    def _login(self, client):
        user = UserFactory()
        client.force_login(user)
        return user

    def test_section_page_has_trail_with_current_as_text(self, client):
        """On /email/ the trail is 'Account Center' (link) → 'Email' (text)."""
        self._login(client)
        response = client.get(reverse("account_email"))
        content = response.content.decode()
        assert 'aria-label="Breadcrumbs"' in content
        assert f'href="{reverse("account-center")}"' in content
        assert "Email" in content

    def test_subpage_section_crumb_is_link(self, client):
        """On a page below a section root, the section crumb links back to it."""
        self._login(client)
        # mfa/webauthn list is a sub-page of the Two-factor section
        response = client.get(reverse("mfa_list_webauthn"))
        content = response.content.decode()
        assert 'aria-label="Breadcrumbs"' in content
        assert f'href="{reverse("mfa_index")}"' in content

    def test_overview_page_has_no_breadcrumbs(self, client):
        """A single-crumb trail is noise — the overview renders none."""
        self._login(client)
        response = client.get(reverse("account-center"))
        assert 'aria-label="Breadcrumbs"' not in response.content.decode()
