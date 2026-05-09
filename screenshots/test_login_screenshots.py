"""
Playwright viewport screenshot tests for the allauth login page.

Covers FR-011 / Principle XIII: Multi-Viewport Screenshot Coverage.

Captures screenshots at three canonical viewport sizes for each of the seven
visually distinct settings permutations, saving them to docs/_static/{tier}/.

Viewports:
  - desktop  : 1440×900
  - tablet   : 768×1024
  - mobile   : 390×844

Permutations:
  - login-page-social-disabled  : SOCIALACCOUNT_ENABLED=False (email/password form only)
  - login-page-social-enabled   : Google SocialApp + SOCIALACCOUNT_ENABLED=True (buttons + form)
  - login-page-social-only      : Google SocialApp + SOCIALACCOUNT_ONLY=True (buttons only)
  - login-page-login-by-code    : ACCOUNT_LOGIN_BY_CODE_ENABLED=True (code button visible)
  - login-page-passkey-enabled  : MFA_PASSKEY_LOGIN_ENABLED=True (passkey button visible)
  - login-request-code-page     : account/request_login_code.html
  - login-confirm-code-page     : account/confirm_login_code.html

Agent visual verification (Principle XIII, NON-NEGOTIABLE):
  After TVAL-3 runs this test suite, the implementing agent MUST open and inspect
  every generated docs/_static/{desktop,tablet,mobile}/login-*.png file
  before marking T011 complete.
"""

from pathlib import Path

import pytest
from allauth.socialaccount.models import SocialApp
from django.contrib.sites.models import Site
from django.urls import reverse

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parents[1]  # django-accounts-center/
SCREENSHOT_ROOT = REPO_ROOT / "docs" / "_static"

VIEWPORTS = [
    ("desktop", 1440, 900),
    ("tablet", 768, 1024),
    ("mobile", 390, 844),
]

PERMUTATIONS = [
    "login-page-social-disabled",
    "login-page-social-enabled",
    "login-page-social-only",
    "login-page-login-by-code",
    "login-page-passkey-enabled",
    "login-request-code-page",
    "login-confirm-code-page",
]


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _create_google_social_app():
    """Create a Google SocialApp associated with site 1 and return it."""
    site, _ = Site.objects.get_or_create(id=1, defaults={"domain": "example.com", "name": "Example"})
    app = SocialApp.objects.create(provider="google", name="Google", client_id="test-id", secret="test-secret")
    app.sites.add(site)
    return app


def _create_test_user(django_user_model):
    """Create a basic user for authenticated flows."""
    return django_user_model.objects.create_user(username="testuser", email="test@example.com", password="testpass123")


# ---------------------------------------------------------------------------
# Screenshot tests
# ---------------------------------------------------------------------------


@pytest.mark.django_db(transaction=True)
@pytest.mark.parametrize("slug", PERMUTATIONS)
@pytest.mark.parametrize("tier,width,height", VIEWPORTS)
def test_login_screenshot(page, live_server, settings, django_user_model, slug, tier, width, height):
    """
    Capture a full-viewport screenshot of the login page for each combination
    of viewport size and settings permutation.

    Saves to: docs/_static/{tier}/{slug}.png
    Asserts: the file was created and is non-zero bytes.
    """
    # --- configure Django settings for this permutation ---
    if slug == "login-page-social-disabled":
        settings.SOCIALACCOUNT_ENABLED = False
        settings.ACCOUNT_LOGIN_BY_CODE_ENABLED = True
        target_path = reverse("account_login")

    elif slug == "login-page-social-enabled":
        settings.SOCIALACCOUNT_ENABLED = True
        settings.SOCIALACCOUNT_ONLY = False
        settings.ACCOUNT_LOGIN_BY_CODE_ENABLED = True
        _create_google_social_app()
        target_path = reverse("account_login")

    elif slug == "login-page-social-only":
        settings.SOCIALACCOUNT_ENABLED = True
        settings.SOCIALACCOUNT_ONLY = True
        _create_google_social_app()
        target_path = reverse("account_login")

    elif slug == "login-page-login-by-code":
        settings.SOCIALACCOUNT_ENABLED = False
        settings.ACCOUNT_LOGIN_BY_CODE_ENABLED = True
        settings.MFA_PASSKEY_LOGIN_ENABLED = False
        target_path = reverse("account_login")

    elif slug == "login-page-passkey-enabled":
        settings.SOCIALACCOUNT_ENABLED = False
        settings.ACCOUNT_LOGIN_BY_CODE_ENABLED = True
        settings.MFA_PASSKEY_LOGIN_ENABLED = True
        target_path = reverse("account_login")

    elif slug == "login-request-code-page":
        settings.ACCOUNT_LOGIN_BY_CODE_ENABLED = True
        target_path = reverse("account_request_login_code")

    elif slug == "login-confirm-code-page":
        settings.ACCOUNT_LOGIN_BY_CODE_ENABLED = True
        # The confirm code page is a login stage — reach it by posting to request_login_code
        user = _create_test_user(django_user_model)
        page.goto(live_server.url + reverse("account_request_login_code"))
        page.wait_for_load_state("networkidle")
        page.set_viewport_size({"width": width, "height": height})
        page.fill("input[type=email]", user.email)
        page.click("button[type=submit]")
        page.wait_for_load_state("networkidle")
        # At this point we should be on confirm_login_code — capture and return early
        output_dir = SCREENSHOT_ROOT / tier
        output_dir.mkdir(parents=True, exist_ok=True)
        screenshot_path = output_dir / f"{slug}.png"
        page.screenshot(path=str(screenshot_path), full_page=True)
        assert screenshot_path.exists(), f"Screenshot was not written to {screenshot_path}"
        assert screenshot_path.stat().st_size > 0, f"Screenshot at {screenshot_path} is empty"
        return

    # --- set viewport ---
    page.set_viewport_size({"width": width, "height": height})

    # --- navigate ---
    page.goto(live_server.url + target_path)
    page.wait_for_load_state("networkidle")

    # --- capture screenshot ---
    output_dir = SCREENSHOT_ROOT / tier
    output_dir.mkdir(parents=True, exist_ok=True)
    screenshot_path = output_dir / f"{slug}.png"
    page.screenshot(path=str(screenshot_path), full_page=True)

    # --- assert file is present and non-empty ---
    assert screenshot_path.exists(), f"Screenshot was not written to {screenshot_path}"
    assert screenshot_path.stat().st_size > 0, f"Screenshot at {screenshot_path} is empty"
