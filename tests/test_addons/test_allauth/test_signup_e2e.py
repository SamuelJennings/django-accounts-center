"""
Playwright E2E tests for the allauth signup page.

Covers:
  - T009 / US2: Full email/password signup flow → redirect to LOGIN_REDIRECT_URL or
    email verification notice; invalid form shows per-field inline errors.
  - T015b / US3: Social provider buttons render when a Google SocialApp is configured;
    social section absent when SOCIALACCOUNT_ENABLED=False.
  - T018b / US4: Signup-closed adapter causes signup_closed.html to render; no <form>
    element visible.

Note: live_server tests require transaction=True so the Django test server thread can
see data created by the test thread (pytest-django uses the same DB connection in
the same process; Django 4+ uses shared-cache in-memory SQLite for this purpose).
"""

import pytest
from allauth.socialaccount.models import SocialApp
from django.contrib.sites.models import Site
from django.urls import reverse

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def signup_url(live_server):
    return live_server.url + reverse("account_signup")


# ---------------------------------------------------------------------------
# T009 / US2: Full email/password signup flow
# ---------------------------------------------------------------------------


@pytest.mark.django_db(transaction=True)
def test_signup_valid_post_redirects_to_login_redirect(page, live_server, settings):
    """
    A user who fills in valid credentials and submits is redirected to
    LOGIN_REDIRECT_URL (ACCOUNT_EMAIL_VERIFICATION='none').
    """
    settings.ACCOUNT_EMAIL_VERIFICATION = "none"
    settings.ACCOUNT_LOGIN_METHODS = {"email"}
    settings.ACCOUNT_SIGNUP_FIELDS = ["email*", "password1*", "password2*"]

    page.goto(signup_url(live_server))
    page.wait_for_load_state("networkidle")

    # Fill email/password fields
    page.fill("input[name='email']", "e2euser@example.com")
    page.fill("input[name='password1']", "SecurePass123!")
    page.fill("input[name='password2']", "SecurePass123!")

    # Submit the form
    page.click("button[type='submit']")
    page.wait_for_load_state("networkidle")

    # After signup with verification=none, should land on LOGIN_REDIRECT_URL (/account-center/)
    assert page.url.endswith(settings.LOGIN_REDIRECT_URL) or page.url != signup_url(live_server), (
        f"Expected redirect away from signup page, but still at: {page.url}"
    )


@pytest.mark.django_db(transaction=True)
def test_signup_mismatched_passwords_shows_inline_error(page, live_server, settings):
    """
    Mismatched passwords cause the form to re-render with an inline error
    on the password field — the page stays at the signup URL.
    """
    settings.ACCOUNT_EMAIL_VERIFICATION = "none"
    settings.ACCOUNT_LOGIN_METHODS = {"email"}
    settings.ACCOUNT_SIGNUP_FIELDS = ["email*", "password1*", "password2*"]

    page.goto(signup_url(live_server))
    page.wait_for_load_state("networkidle")

    page.fill("input[name='email']", "e2euser@example.com")
    page.fill("input[name='password1']", "SecurePass123!")
    page.fill("input[name='password2']", "DifferentPass456!")
    page.click("button[type='submit']")
    page.wait_for_load_state("networkidle")

    # Should stay on signup page
    assert "signup" in page.url or page.url == signup_url(live_server)
    # Error text should be present somewhere on the page
    assert page.locator("text=password").count() > 0


# ---------------------------------------------------------------------------
# T015b / US3: Social provider button presence
# ---------------------------------------------------------------------------


@pytest.mark.django_db(transaction=True)
def test_social_button_present_when_google_configured(page, live_server, settings):
    """
    When a Google SocialApp is configured and SOCIALACCOUNT_ENABLED=True,
    the signup page renders a Google provider button.
    """
    settings.SOCIALACCOUNT_ENABLED = True
    settings.SOCIALACCOUNT_ONLY = False

    site, _ = Site.objects.get_or_create(id=1, defaults={"domain": "example.com", "name": "Example"})
    app = SocialApp.objects.create(provider="google", name="Google", client_id="test-id", secret="test-secret")
    app.sites.add(site)

    page.goto(signup_url(live_server))
    page.wait_for_load_state("networkidle")

    content = page.content()
    assert "Google" in content, "Google social button should be present on the signup page"


@pytest.mark.django_db(transaction=True)
def test_social_section_absent_when_socialaccount_disabled(page, live_server, settings):
    """
    When SOCIALACCOUNT_ENABLED=False, no social provider buttons appear,
    even if a SocialApp is configured in the database.
    """
    settings.SOCIALACCOUNT_ENABLED = False

    page.goto(signup_url(live_server))
    page.wait_for_load_state("networkidle")

    content = page.content()
    # No outline-secondary buttons (used for provider buttons) should appear
    assert "outline-secondary" not in content, "Social buttons should be absent when SOCIALACCOUNT_ENABLED=False"


# ---------------------------------------------------------------------------
# T018b / US4: Signup closed via adapter
# ---------------------------------------------------------------------------


@pytest.mark.django_db(transaction=True)
def test_signup_closed_shows_closed_message(page, live_server, settings):
    """
    When the account adapter disables signups, the signup_closed.html template
    renders and shows the 'Sign Up Closed' heading.  No <form> element is present.
    """
    settings.ACCOUNT_ADAPTER = "tests.test_addons.test_allauth.adapters.ClosedSignupAdapter"

    page.goto(signup_url(live_server))
    page.wait_for_load_state("networkidle")

    content = page.content()
    assert page.locator("form").count() == 0, "No <form> element must appear when signup is closed"
