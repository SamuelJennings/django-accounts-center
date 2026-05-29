"""
Integration tests for the allauth email management flow.

Covers:
  - T004 / US1: Single-email change flow (email_change.html, ACCOUNT_CHANGE_EMAIL=True)
  - T006 / US2: Multi-email address manager (email.html, ACCOUNT_CHANGE_EMAIL=False)
  - T008 / US3: Verified email required gate page (verified_email_required.html)

Notes on test design:
  - allauth's EmailView.template_name is a class-level attribute evaluated at
    import time (not request time), so per-test settings.ACCOUNT_CHANGE_EMAIL=True
    cannot change which template allauth serves via the account_email URL.
    A dedicated test URL ("account_email_change_test") uses a subclass of EmailView
    with the template name hard-coded to "account/email_change.html".
  - A dedicated test URL ("account_email_multi_test") uses a subclass of EmailView
    with the template name hard-coded to "account/email.html".
  - allauth 65.x does not register a URL for the verified_email_required gate page;
    the decorator renders the template inline.  A test-only URL is registered in
    tests/urls.py under the name "account_verified_email_required".
  - To prevent allauth's sync_user_email_address() from auto-creating an
    EmailAddress from user.email, "no-email" branch tests create users with
    email="" so the sync is a no-op.
"""

import pytest
from django.template.loader import get_template
from django.urls import reverse

from tests.factories import EmailAddressFactory, UserFactory

# ---------------------------------------------------------------------------
# Template source checks — no raw {% element %} / {% endelement %} tags
# ---------------------------------------------------------------------------

EMAIL_MANAGEMENT_TEMPLATES = [
    "account/email_change.html",
    "account/email.html",
    "account/verified_email_required.html",
]


@pytest.mark.parametrize("template_name", EMAIL_MANAGEMENT_TEMPLATES)
def test_no_raw_element_tags_in_templates(template_name):
    """No email-management template may contain raw {% element %} tags."""
    source = get_template(template_name).template.source
    assert "{% element" not in source
    assert "{% endelement" not in source


# ---------------------------------------------------------------------------
# T004 / US1: email_change.html (ACCOUNT_CHANGE_EMAIL = True)
#
# Uses the test-only URL "account_email_change_test" which maps to an EmailView
# subclass that hard-codes template_name = "account/email_change.html".
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestEmailChangeView:
    """Tests for account/email_change.html — single-email change flow."""

    def test_renders_200_for_authenticated(self, client, settings):
        """account_email_change_test GET must return HTTP 200 for an authenticated user."""
        settings.ACCOUNT_CHANGE_EMAIL = True
        user = UserFactory()
        EmailAddressFactory(user=user)
        client.force_login(user)
        response = client.get(reverse("account_email_change_test"))
        assert response.status_code == 200

    def test_current_email_input_present(self, client, settings):
        """Rendered HTML must contain a disabled #current_email input with user's email as value."""
        settings.ACCOUNT_CHANGE_EMAIL = True
        user = UserFactory()
        EmailAddressFactory(user=user)
        client.force_login(user)
        response = client.get(reverse("account_email_change_test"))
        content = response.content.decode()
        assert 'id="current_email"' in content
        assert 'type="email"' in content
        assert "disabled" in content
        assert user.email in content

    def test_change_email_input_present(self, client, settings):
        """Rendered HTML must contain an <input name='email'> for the new address field."""
        settings.ACCOUNT_CHANGE_EMAIL = True
        user = UserFactory()
        EmailAddressFactory(user=user)
        client.force_login(user)
        response = client.get(reverse("account_email_change_test"))
        content = response.content.decode()
        assert 'name="email"' in content

    def test_action_add_button_present(self, client, settings):
        """Rendered HTML must contain a submit button with name='action_add'."""
        settings.ACCOUNT_CHANGE_EMAIL = True
        user = UserFactory()
        EmailAddressFactory(user=user)
        client.force_login(user)
        response = client.get(reverse("account_email_change_test"))
        content = response.content.decode()
        assert 'name="action_add"' in content

    def test_pending_email_branch_new_email_input(self, client, settings):
        """When a pending new address exists, #new_email disabled input with that value must appear."""
        settings.ACCOUNT_CHANGE_EMAIL = True
        user = UserFactory()
        EmailAddressFactory(user=user)
        # Create the pending email address directly
        EmailAddressFactory(user=user, email="pending@example.com", verified=False, primary=False)
        client.force_login(user)
        response = client.get(reverse("account_email_change_test"))
        content = response.content.decode()
        assert 'id="new_email"' in content
        assert "pending@example.com" in content

    def test_pending_email_branch_resend_button_present(self, client, settings):
        """When a pending new address exists, a re-send verification button must appear."""
        settings.ACCOUNT_CHANGE_EMAIL = True
        user = UserFactory()
        EmailAddressFactory(user=user)
        EmailAddressFactory(user=user, email="pending@example.com", verified=False, primary=False)
        client.force_login(user)
        response = client.get(reverse("account_email_change_test"))
        content = response.content.decode()
        assert 'name="action_send"' in content

    def test_pending_email_branch_cancel_button_present(self, client, settings):
        """When a pending new address exists and current_emailaddress is set, cancel button must appear."""
        settings.ACCOUNT_CHANGE_EMAIL = True
        user = UserFactory()
        EmailAddressFactory(user=user)
        EmailAddressFactory(user=user, email="pending@example.com", verified=False, primary=False)
        client.force_login(user)
        response = client.get(reverse("account_email_change_test"))
        content = response.content.decode()
        assert 'name="action_remove"' in content

    def test_pending_email_branch_hidden_form_present(self, client, settings):
        """When a pending new address exists, a hidden #pending-email form must be in the HTML."""
        settings.ACCOUNT_CHANGE_EMAIL = True
        user = UserFactory()
        EmailAddressFactory(user=user)
        EmailAddressFactory(user=user, email="pending@example.com", verified=False, primary=False)
        client.force_login(user)
        response = client.get(reverse("account_email_change_test"))
        content = response.content.decode()
        assert 'id="pending-email"' in content

    def test_no_email_branch_shows_alert_warning(self, client, settings):
        """When user has no email addresses, alert-warning must appear in rendered output.

        User is created with email="" so sync_user_email_address() does not
        auto-create an EmailAddress record from user.email.
        """
        settings.ACCOUNT_CHANGE_EMAIL = True
        user = UserFactory(email="")
        # No EmailAddress records — sync_user_email_address is a no-op for empty email
        client.force_login(user)
        response = client.get(reverse("account_email_change_test"))
        content = response.content.decode()
        assert "alert-warning" in content


# ---------------------------------------------------------------------------
# T006 / US2: email.html (ACCOUNT_CHANGE_EMAIL = False)
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestEmailMultiView:
    """Tests for account/email.html — multi-email address manager."""

    def test_renders_200_for_authenticated(self, client, settings):
        """account_email GET must return HTTP 200 for authenticated user with two emails."""
        settings.ACCOUNT_CHANGE_EMAIL = False
        user = UserFactory()
        EmailAddressFactory(user=user)
        EmailAddressFactory(user=user, email="second@example.com", verified=False, primary=False)
        client.force_login(user)
        response = client.get(reverse("account_email_multi_test"))
        assert response.status_code == 200

    def test_verified_address_has_badge(self, client, settings):
        """The verified address must have a sibling .badge element in its label."""
        settings.ACCOUNT_CHANGE_EMAIL = False
        user = UserFactory()
        EmailAddressFactory(user=user)
        client.force_login(user)
        response = client.get(reverse("account_email_multi_test"))
        content = response.content.decode()
        assert "badge" in content

    def test_primary_address_has_badge(self, client, settings):
        """The primary address must have a sibling .badge element in its label."""
        settings.ACCOUNT_CHANGE_EMAIL = False
        user = UserFactory()
        EmailAddressFactory(user=user)
        EmailAddressFactory(user=user, email="second@example.com", verified=False, primary=False)
        client.force_login(user)
        response = client.get(reverse("account_email_multi_test"))
        content = response.content.decode()
        assert "badge" in content

    def test_action_primary_button_present(self, client, settings):
        """action_primary button must be present for a non-primary address."""
        settings.ACCOUNT_CHANGE_EMAIL = False
        user = UserFactory()
        EmailAddressFactory(user=user)
        EmailAddressFactory(user=user, email="second@example.com", primary=False)
        client.force_login(user)
        response = client.get(reverse("account_email_multi_test"))
        content = response.content.decode()
        assert 'name="action_primary"' in content

    def test_action_send_button_present(self, client, settings):
        """action_send button must be present for an unverified address."""
        settings.ACCOUNT_CHANGE_EMAIL = False
        user = UserFactory()
        EmailAddressFactory(user=user)
        EmailAddressFactory(user=user, email="second@example.com", verified=False, primary=False)
        client.force_login(user)
        response = client.get(reverse("account_email_multi_test"))
        content = response.content.decode()
        assert 'name="action_send"' in content

    def test_action_remove_button_present(self, client, settings):
        """action_remove button must be present in rendered output."""
        settings.ACCOUNT_CHANGE_EMAIL = False
        user = UserFactory()
        EmailAddressFactory(user=user)
        client.force_login(user)
        response = client.get(reverse("account_email_multi_test"))
        content = response.content.decode()
        assert 'name="action_remove"' in content

    def test_js_block_present(self, client, settings):
        """Rendered output must contain the account/js/account.js script tag."""
        settings.ACCOUNT_CHANGE_EMAIL = False
        user = UserFactory()
        EmailAddressFactory(user=user)
        client.force_login(user)
        response = client.get(reverse("account_email_multi_test"))
        content = response.content.decode()
        assert "account/js/account.js" in content

    def test_no_address_branch_shows_alert_warning(self, client, settings):
        """When user has no email addresses, alert-warning must appear in rendered output.

        User is created with email="" so sync_user_email_address() does not
        auto-create an EmailAddress record from user.email.
        """
        settings.ACCOUNT_CHANGE_EMAIL = False
        user = UserFactory(email="")
        client.force_login(user)
        response = client.get(reverse("account_email_multi_test"))
        content = response.content.decode()
        assert "alert-warning" in content


# ---------------------------------------------------------------------------
# T008 / US3: verified_email_required.html
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestVerifiedEmailRequiredView:
    """Tests for account/verified_email_required.html — gate page."""

    def test_renders_200_for_authenticated(self, client):
        """account_verified_email_required must return HTTP 200 for an authenticated user."""
        user = UserFactory()
        client.force_login(user)
        response = client.get(reverse("account_verified_email_required"))
        assert response.status_code == 200

    def test_account_email_link_present(self, client):
        """Rendered HTML must contain a link to account_email URL."""
        user = UserFactory()
        client.force_login(user)
        response = client.get(reverse("account_verified_email_required"))
        content = response.content.decode()
        email_url = reverse("account_email")
        assert f'href="{email_url}"' in content

    def test_at_least_one_paragraph_present(self, client):
        """Rendered HTML must contain at least one non-empty <p> element."""
        user = UserFactory()
        client.force_login(user)
        response = client.get(reverse("account_verified_email_required"))
        content = response.content.decode()
        assert "<p>" in content or "<p " in content
