"""
E2E tests for navigation and menu functionality.

This module tests:
- Sidebar menu navigation
- Mobile offcanvas behavior
- Logout flow via user dropdown
- Breadcrumbs
- Unauthorized access redirects
"""

import pytest
from django.urls import reverse
from playwright.sync_api import Page, expect

from tests.e2e.conftest import (
    login_user,
    logout_user,
    take_screenshot,
)

# Mark all tests in this module for e2e and Django DB with transactional mode
pytestmark = [pytest.mark.e2e, pytest.mark.django_db(transaction=True)]


@pytest.mark.django_db
class TestLogoutFlow:
    """Test logout functionality via user dropdown."""

    def test_complete_logout_flow_desktop(self, page_desktop: Page, live_server, e2e_user, screenshots_dir):
        """Test complete logout flow on desktop."""
        login_user(page_desktop, live_server.url, e2e_user.email, "TestPass123!")

        # Navigate to logout page
        page_desktop.goto(live_server.url + reverse("account_logout"))

        # Should show logout confirmation page
        expect(page_desktop.locator("h1")).to_contain_text("Sign Out")

        # Take screenshot of confirmation page
        take_screenshot(page_desktop, screenshots_dir, "logout_confirmation_desktop")

        # Confirm logout
        page_desktop.click('button[type="submit"]')

        # Should redirect to login page
        login_url = reverse("account_login")
        page_desktop.wait_for_url(f"**{login_url}")
        assert login_url in page_desktop.url

        # Take screenshot after logout
        take_screenshot(page_desktop, screenshots_dir, "after_logout_desktop")

    def test_cannot_access_dashboard_after_logout(self, page_desktop: Page, live_server, e2e_user):
        """Test that dashboard is not accessible after logout."""
        login_user(page_desktop, live_server.url, e2e_user.email, "TestPass123!")

        # Logout
        logout_user(page_desktop, live_server.url)

        # Try to access dashboard
        page_desktop.goto(live_server.url + reverse("account-center"))

        # Should redirect to login
        login_url = reverse("account_login")
        page_desktop.wait_for_url(f"**{login_url}")
        assert login_url in page_desktop.url

    def test_logout_flow_mobile(self, page_mobile: Page, live_server, e2e_user, screenshots_dir):
        """Test logout flow on mobile viewport."""
        login_user(page_mobile, live_server.url, e2e_user.email, "TestPass123!")

        # Navigate to logout
        page_mobile.goto(live_server.url + reverse("account_logout"))

        # Confirm logout
        page_mobile.click('button[type="submit"]')

        # Should redirect to login
        login_url = reverse("account_login")
        page_mobile.wait_for_url(f"**{login_url}")
        assert login_url in page_mobile.url

        # Take screenshot
        take_screenshot(page_mobile, screenshots_dir, "after_logout_mobile")
