"""
Integration tests for the allauth email verification flow.

Covers:
  - T004 / US1: Verification-sent page (verification_sent.html)
  - T005 / US1+US2: Email confirmation page — valid-key and invalid-key branches (email_confirm.html)
  - T007 / US4: Account-inactive page (account_inactive.html)
  - T009 / US3: Code-based email verification (confirm_email_verification_code.html)
    NOTE: confirm_email_verification_code.html has no dedicated URL — it is served through
    allauth's stage pipeline. Tests use render_to_string directly (same pattern as spec 003's
    T012 tests for confirm_password_reset_code.html).
"""

import pytest
from allauth.account.forms import ConfirmEmailVerificationCodeForm
from django.contrib.auth import get_user_model
from django.template.loader import render_to_string
from django.urls import reverse

User = get_user_model()


# ---------------------------------------------------------------------------
# T004 / US1: verification_sent.html
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestVerificationSentView:
    """Tests for account/verification_sent.html."""

    def test_renders_200_for_anonymous(self, client):
        """account_email_verification_sent must return HTTP 200 for anonymous users."""
        response = client.get(reverse("account_email_verification_sent"))
        assert response.status_code == 200

    def test_no_element_tags_in_output(self, client):
        """Rendered HTML must not contain raw {% element %} tags."""
        response = client.get(reverse("account_email_verification_sent"))
        content = response.content.decode()
        assert "{% element" not in content
        assert "{% endelement" not in content

    def test_contains_descriptive_text(self, client):
        """Rendered HTML must contain non-empty descriptive paragraph text."""
        response = client.get(reverse("account_email_verification_sent"))
        content = response.content.decode()
        # The informational message must be present and non-empty
        assert len(content.strip()) > 0
        assert "email" in content.lower()

    def test_no_form_element(self, client):
        """verification_sent.html is purely informational — must contain no <form>."""
        response = client.get(reverse("account_email_verification_sent"))
        content = response.content.decode()
        assert "<form" not in content


# ---------------------------------------------------------------------------
# T005 / US1+US2: email_confirm.html
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestEmailConfirmView:
    """Tests for account/email_confirm.html — valid-key and invalid-key branches."""

    def _create_confirmed_user(self):
        """Create a verified user with an email address."""
        from allauth.account.models import EmailAddress

        user = User.objects.create_user(
            username="confirmuser",
            email="confirm@example.com",
            password="testpass123",
        )
        EmailAddress.objects.create(
            user=user,
            email="confirm@example.com",
            verified=False,
            primary=True,
        )
        return user

    def _get_confirmation_key(self, user):
        """Generate a fresh email confirmation key for the user's primary address."""
        from allauth.account.models import EmailAddress, EmailConfirmationHMAC

        email_address = EmailAddress.objects.get(user=user)
        confirmation = EmailConfirmationHMAC(email_address)
        return confirmation.key

    def test_valid_key_renders_200(self, client):
        """email_confirm.html with a valid key must return HTTP 200."""
        user = self._create_confirmed_user()
        key = self._get_confirmation_key(user)
        url = reverse("account_confirm_email", kwargs={"key": key})
        response = client.get(url)
        assert response.status_code == 200

    def test_valid_key_contains_form(self, client):
        """Valid-key branch must contain a <form> element."""
        user = self._create_confirmed_user()
        key = self._get_confirmation_key(user)
        url = reverse("account_confirm_email", kwargs={"key": key})
        response = client.get(url)
        content = response.content.decode()
        assert "<form" in content

    def test_valid_key_contains_submit_button_with_text(self, client):
        """Valid-key branch must contain a submit button with non-empty button text."""
        user = self._create_confirmed_user()
        key = self._get_confirmation_key(user)
        url = reverse("account_confirm_email", kwargs={"key": key})
        response = client.get(url)
        content = response.content.decode()
        # Must have a submit button
        assert 'type="submit"' in content
        # Button must have non-empty text (not checking specific label string)
        import re

        submit_buttons = re.findall(
            r'<button[^>]*type="submit"[^>]*>(.*?)</button>',
            content,
            re.DOTALL,
        )
        button_texts = [re.sub(r"<[^>]+>", "", btn).strip() for btn in submit_buttons]
        assert any(len(t) > 0 for t in button_texts), "Submit button must have non-empty text"

    def test_valid_key_contains_icon_element(self, client):
        """Valid-key branch must contain a rendered icon element (svg or i)."""
        user = self._create_confirmed_user()
        key = self._get_confirmation_key(user)
        url = reverse("account_confirm_email", kwargs={"key": key})
        response = client.get(url)
        content = response.content.decode()
        # Icon must render as <svg> or <i> element — not assert specific icon name
        assert "<svg" in content or "<i " in content or "<i>" in content

    def test_valid_key_contains_redirect_field(self, client):
        """Valid-key branch must render redirect_field hidden input inside the form."""
        user = self._create_confirmed_user()
        key = self._get_confirmation_key(user)
        url = reverse("account_confirm_email", kwargs={"key": key})
        response = client.get(url)
        content = response.content.decode()
        assert 'type="hidden"' in content

    def test_invalid_key_renders_200(self, client):
        """email_confirm.html with an invalid/expired key must return HTTP 200."""
        url = reverse("account_confirm_email", kwargs={"key": "invalid-key-that-does-not-exist"})
        response = client.get(url)
        assert response.status_code == 200

    def test_invalid_key_no_form(self, client):
        """Invalid-key branch must NOT contain a <form> element."""
        url = reverse("account_confirm_email", kwargs={"key": "invalid-key-that-does-not-exist"})
        response = client.get(url)
        content = response.content.decode()
        assert "<form" not in content

    def test_invalid_key_contains_email_management_link(self, client):
        """Invalid-key branch must contain a link pointing to the account_email URL."""
        url = reverse("account_confirm_email", kwargs={"key": "invalid-key-that-does-not-exist"})
        response = client.get(url)
        content = response.content.decode()
        email_management_url = reverse("account_email")
        assert email_management_url in content

    def test_no_element_tags_in_valid_key_output(self, client):
        """Rendered HTML for valid-key branch must not contain raw {% element %} tags."""
        user = self._create_confirmed_user()
        key = self._get_confirmation_key(user)
        url = reverse("account_confirm_email", kwargs={"key": key})
        response = client.get(url)
        content = response.content.decode()
        assert "{% element" not in content
        assert "{% endelement" not in content

    def test_no_element_tags_in_invalid_key_output(self, client):
        """Rendered HTML for invalid-key branch must not contain raw {% element %} tags."""
        url = reverse("account_confirm_email", kwargs={"key": "invalid-key-that-does-not-exist"})
        response = client.get(url)
        content = response.content.decode()
        assert "{% element" not in content
        assert "{% endelement" not in content


# ---------------------------------------------------------------------------
# T007 / US4: account_inactive.html
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestAccountInactiveView:
    """Tests for account/account_inactive.html."""

    def test_renders_200(self, client):
        """account_inactive must return HTTP 200."""
        response = client.get(reverse("account_inactive"))
        assert response.status_code == 200

    def test_contains_explanatory_message(self, client):
        """Rendered output must contain a non-empty explanatory message."""
        response = client.get(reverse("account_inactive"))
        content = response.content.decode()
        assert len(content.strip()) > 0
        assert "inactive" in content.lower()

    def test_no_element_tags(self, client):
        """Rendered output must not contain raw {% element %} tags."""
        response = client.get(reverse("account_inactive"))
        content = response.content.decode()
        assert "{% element" not in content
        assert "{% endelement" not in content

    def test_no_form_element(self, client):
        """account_inactive.html is informational — must contain no <form>."""
        response = client.get(reverse("account_inactive"))
        content = response.content.decode()
        assert "<form" not in content


# ---------------------------------------------------------------------------
# T009 / US3: confirm_email_verification_code.html
#
# This template has no dedicated URL — it is served through allauth's stage
# pipeline. Tests verify the template by rendering it directly with
# render_to_string (same pattern as spec 003's T012 / confirm_password_reset_code.html).
# ---------------------------------------------------------------------------


def _render_email_verification_code_template(rf, extra_context=None):
    """Render confirm_email_verification_code.html with explicit context."""
    form = ConfirmEmailVerificationCodeForm(code="000000")
    request = rf.get("/")
    ctx = {
        "verify_form": form,
        "redirect_field": '<input type="hidden" name="next" value="/" />',
        "email": "test@example.com",
        "can_resend": False,
        "can_change": False,
        "cancel_url": None,
        "SOCIALACCOUNT_ENABLED": False,
        "SOCIALACCOUNT_ONLY": False,
        "LOGIN_BY_CODE_ENABLED": True,
        "PASSKEY_LOGIN_ENABLED": False,
        "PASSKEY_SIGNUP_ENABLED": False,
        "login_url": "/accounts/login/",
        "signup_url": "/accounts/signup/",
        "signup_by_passkey_url": None,
        "site": None,
    }
    if extra_context:
        ctx.update(extra_context)
    return render_to_string("account/confirm_email_verification_code.html", ctx, request=request)


@pytest.mark.django_db
class TestConfirmEmailVerificationCodeTemplate:
    """Tests for account/confirm_email_verification_code.html via render_to_string."""

    def test_title_block_renders_correctly(self, rf):
        """Title block must render the correct heading text."""
        content = _render_email_verification_code_template(rf)
        assert "Enter Email Verification Code" in content

    def test_contains_code_input_field(self, rf):
        """Rendered output must contain a code-entry <input> field."""
        content = _render_email_verification_code_template(rf)
        assert "<input" in content

    def test_no_element_tags(self, rf):
        """Rendered output must not contain raw {% element %} tags."""
        content = _render_email_verification_code_template(rf)
        assert "{% element" not in content
        assert "{% endelement" not in content

    def test_template_renders_without_syntax_error(self, rf):
        """Template must render without a TemplateSyntaxError (fail-silent URL blocks)."""
        import django.template

        try:
            _render_email_verification_code_template(rf)
        except django.template.TemplateSyntaxError as exc:
            raise AssertionError(f"Template has syntax error: {exc}") from exc

    def test_recipient_email_displayed(self, rf):
        """Rendered output must display the recipient email address."""
        content = _render_email_verification_code_template(rf)
        assert "test@example.com" in content
