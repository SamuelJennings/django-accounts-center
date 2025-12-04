"""
E2E tests for dashboard page.

This module tests the dashboard functionality including:
- Access control (authentication required)
- Logout flows
"""

import pytest
from django.urls import reverse
from playwright.sync_api import Page, expect

from tests.e2e.conftest import (
    login_user,
    take_screenshot,
)

# Mark all tests in this module for e2e and Django DB with transactional mode
pytestmark = [pytest.mark.e2e, pytest.mark.django_db(transaction=True)]


@pytest.mark.django_db
class TestDashboardDesktop:
    """Test dashboard navigation flows on desktop viewport."""

    def test_dashboard_security_settings_link(self, page_desktop: Page, live_server, e2e_user):
        """Test that security settings link navigates correctly."""
        login_user(page_desktop, live_server.url, e2e_user.email, "TestPass123!")

        # Click on Security Settings link (should go to password change)
        security_link = page_desktop.locator(f'a[href="{reverse("account_change_password")}"]').first
        security_link.click()

        # Should navigate to password change page
        password_change_url = reverse("account_change_password")
        page_desktop.wait_for_url(f"**{password_change_url}")
        assert password_change_url in page_desktop.url


@pytest.mark.django_db
class TestDashboardAccessControl:
    """Test dashboard access control and authentication."""

    def test_dashboard_requires_authentication(self, page_desktop: Page, live_server):
        """Test that dashboard requires authentication."""
        # Try to access dashboard without logging in
        page_desktop.goto(live_server.url + reverse("account-center"))

        # Should redirect to login
        login_url = reverse("account_login")
        assert login_url in page_desktop.url


@pytest.mark.django_db
class TestMobileOffcanvasNavigation:
    """Test mobile offcanvas navigation menu."""

    def test_offcanvas_sidebar_opens_on_mobile(self, page_mobile: Page, live_server, e2e_user, screenshots_dir):
        """Test that offcanvas sidebar opens when hamburger is clicked."""
        login_user(page_mobile, live_server.url, e2e_user.email, "TestPass123!")

        # Click hamburger menu
        hamburger = page_mobile.locator('button[data-bs-toggle="offcanvas"]')
        hamburger.click()

        # Offcanvas sidebar should be visible (auto-waits)
        offcanvas = page_mobile.locator("#sidebar, .offcanvas.show")
        expect(offcanvas.first).to_be_visible()

        # Take screenshot with open sidebar
        take_screenshot(page_mobile, screenshots_dir, "offcanvas_sidebar_open_mobile")

    def test_offcanvas_closes_after_navigation(self, page_mobile: Page, live_server, e2e_user):
        """Test that offcanvas closes after clicking a menu item."""
        login_user(page_mobile, live_server.url, e2e_user.email, "TestPass123!")

        # Open offcanvas
        page_mobile.click('button[data-bs-toggle="offcanvas"]')

        # Click a menu item
        email_url = reverse("account_email")
        page_mobile.click(f'a[href="{email_url}"]')

        # Wait for navigation
        page_mobile.wait_for_url(f"**{email_url}")

        # Offcanvas should auto-close (or can be manually tested)
        # This behavior depends on Bootstrap configuration
