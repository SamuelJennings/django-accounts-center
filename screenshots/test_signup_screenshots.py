"""
Playwright viewport screenshot tests for the allauth signup page.

Covers FR-011 / Principle XIII: Multi-Viewport Screenshot Coverage.

Captures screenshots at three canonical viewport sizes for each of the six
visually distinct settings permutations, saving them to docs/_static/{tier}/.

Viewports:
  - desktop  : 1440×900
  - tablet   : 768×1024
  - mobile   : 390×844

Permutations:
  - signup-page-social-disabled  : SOCIALACCOUNT_ENABLED=False (email/password form only)
  - signup-page-social-enabled   : Google SocialApp + SOCIALACCOUNT_ENABLED=True (buttons + form)
  - signup-page-social-only      : Google SocialApp + SOCIALACCOUNT_ONLY=True (buttons only)
  - signup-page-signup-closed    : ClosedSignupAdapter → signup_closed.html
  - signup-page-passkey-enabled  : MFA_PASSKEY_SIGNUP_ENABLED=True (signup page with passkey option)
  - signup-by-passkey-page       : Same passkey settings at /signup/passkey/ URL

Agent visual verification (Principle XIII, NON-NEGOTIABLE):
  After TVAL-5 runs this test suite, the implementing agent MUST open and inspect
  every generated docs/_static/{desktop,tablet,mobile}/signup-page-*.png file
  and signup-by-passkey-page-*.png before marking TVAL-5 complete.
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
    "signup-page-social-disabled",
    "signup-page-social-enabled",
    "signup-page-social-only",
    "signup-page-signup-closed",
    "signup-page-passkey-enabled",
    "signup-by-passkey-page",
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


# ---------------------------------------------------------------------------
# Screenshot tests
# ---------------------------------------------------------------------------


@pytest.mark.django_db(transaction=True)
@pytest.mark.parametrize("slug", PERMUTATIONS)
@pytest.mark.parametrize("tier,width,height", VIEWPORTS)
def test_signup_screenshot(page, live_server, settings, slug, tier, width, height):
    """
    Capture a full-viewport screenshot of the signup page for each combination
    of viewport size and settings permutation.

    Saves to: docs/_static/{tier}/{slug}.png
    Asserts: the file was created and is non-zero bytes.
    """
    # --- configure Django settings for this permutation ---
    if slug == "signup-page-social-disabled":
        settings.SOCIALACCOUNT_ENABLED = False

    elif slug == "signup-page-social-enabled":
        settings.SOCIALACCOUNT_ENABLED = True
        settings.SOCIALACCOUNT_ONLY = False
        _create_google_social_app()

    elif slug == "signup-page-social-only":
        settings.SOCIALACCOUNT_ENABLED = True
        settings.SOCIALACCOUNT_ONLY = True
        _create_google_social_app()

    elif slug == "signup-page-signup-closed":
        settings.ACCOUNT_ADAPTER = "tests.test_addons.test_allauth.adapters.ClosedSignupAdapter"

    elif slug in ("signup-page-passkey-enabled", "signup-by-passkey-page"):
        settings.MFA_PASSKEY_SIGNUP_ENABLED = True
        settings.SOCIALACCOUNT_ENABLED = False

    # --- set viewport ---
    page.set_viewport_size({"width": width, "height": height})

    # --- navigate to the appropriate URL ---
    if slug == "signup-by-passkey-page":
        target_path = reverse("account_signup_by_passkey")
    else:
        target_path = reverse("account_signup")
    page.goto(live_server.url + target_path)
    page.wait_for_load_state("networkidle")

    # --- capture screenshot ---
    output_dir = SCREENSHOT_ROOT / tier
    output_dir.mkdir(parents=True, exist_ok=True)
    screenshot_path = output_dir / f"{slug}.png"
    page.screenshot(path=str(screenshot_path))

    # --- assert file is present and non-empty ---
    assert screenshot_path.exists(), f"Screenshot was not written to {screenshot_path}"
    assert screenshot_path.stat().st_size > 0, f"Screenshot at {screenshot_path} is empty"
