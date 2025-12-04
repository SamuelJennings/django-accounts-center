"""
E2E tests for login flow using django-allauth.

This module tests the complete login workflow including:
- Standard email/password login
- Form validation and error handling
- Redirect behavior after successful login
- Responsive design across different viewport sizes
- Remember me functionality
"""

import pytest
from django.urls import reverse
from playwright.sync_api import Page, expect

from tests.e2e.conftest import take_screenshot

# Mark all tests in this module for e2e and Django DB with transactional mode
pytestmark = [pytest.mark.e2e, pytest.mark.django_db(transaction=True)]


@pytest.mark.django_db
class TestLoginFlowDesktop:
    """Test login flow on desktop viewport."""

    def test_successful_login_desktop(self, page_desktop: Page, live_server, e2e_user, screenshots_dir):
        """Test successful login flow on desktop."""
        page_desktop.goto(live_server.url + reverse("account_login"))

        # Fill in login form
        page_desktop.fill('input[name="login"]', e2e_user.email)
        page_desktop.fill('input[name="password"]', "TestPass123!")

        # Take screenshot before submit
        take_screenshot(page_desktop, screenshots_dir, "login/filled_desktop")

        # Submit form - click the main "Sign In" button, not the passkey button
        page_desktop.get_by_role("button", name="Sign In", exact=True).click()

        # Wait for redirect to dashboard (Playwright auto-waits up to 30s)
        page_desktop.wait_for_url(live_server.url + reverse("account-center"))

        # Verify we're on the dashboard
        expect(page_desktop).to_have_url(live_server.url + reverse("account-center"))

        # Verify success message or dashboard content
        expect(page_desktop.locator("h1")).to_contain_text("Account Center")

        # Take screenshot of dashboard after login
        take_screenshot(page_desktop, screenshots_dir, "dashboard/after_login_desktop")

    def test_login_with_invalid_credentials(self, page_desktop: Page, live_server, screenshots_dir):
        """Test login with invalid credentials shows error."""
        page_desktop.goto(live_server.url + reverse("account_login"))

        # Fill in invalid credentials
        page_desktop.fill('input[name="login"]', "invalid@example.com")
        page_desktop.fill('input[name="password"]', "WrongPassword123!")

        # Submit form
        page_desktop.get_by_role("button", name="Sign In", exact=True).click()

        # Should stay on login page
        expect(page_desktop).to_have_url(live_server.url + reverse("account_login"))

        # Verify error message is displayed (expect auto-waits for visibility)
        error_message = page_desktop.locator(".alert-danger, .invalid-feedback, .error, div.alert")
        expect(error_message.first).to_be_visible()

        # Take screenshot of error state
        take_screenshot(page_desktop, screenshots_dir, "login/error_desktop")


@pytest.mark.django_db
class TestLoginFlowMobile:
    """Test login flow on mobile viewport."""

    def test_successful_login_mobile(self, page_mobile: Page, live_server, e2e_user, screenshots_dir):
        """Test successful login on mobile viewport."""
        page_mobile.goto(live_server.url + reverse("account_login"))

        # Fill and submit
        page_mobile.fill('input[name="login"]', e2e_user.email)
        page_mobile.fill('input[name="password"]', "TestPass123!")
        page_mobile.get_by_role("button", name="Sign In", exact=True).click()

        # Wait for redirect (Playwright auto-waits)
        page_mobile.wait_for_url(live_server.url + reverse("account-center"))

        # Verify dashboard loads
        expect(page_mobile).to_have_url(live_server.url + reverse("account-center"))

        # Take screenshot
        take_screenshot(page_mobile, screenshots_dir, "dashboard/after_login_mobile")


@pytest.mark.django_db
class TestLoginFlowTablet:
    """Test login flow on tablet viewport."""

    def test_successful_login_tablet(self, page_tablet: Page, live_server, e2e_user, screenshots_dir):
        """Test successful login on tablet viewport."""
        page_tablet.goto(live_server.url + reverse("account_login"))

        # Fill and submit
        page_tablet.fill('input[name="login"]', e2e_user.email)
        page_tablet.fill('input[name="password"]', "TestPass123!")
        page_tablet.get_by_role("button", name="Sign In", exact=True).click()

        # Wait for redirect (Playwright auto-waits)
        page_tablet.wait_for_url(live_server.url + reverse("account-center"))

        # Verify dashboard
        expect(page_tablet).to_have_url(live_server.url + reverse("account-center"))

        # Take screenshot
        take_screenshot(page_tablet, screenshots_dir, "dashboard/after_login_tablet")


@pytest.mark.django_db
class TestLoginFormInteractions:
    """Test login form keyboard interactions."""

    def test_form_submission_with_enter_key(self, page_desktop: Page, live_server, e2e_user):
        """Test that form can be submitted with Enter key."""
        page_desktop.goto(live_server.url + reverse("account_login"))

        # Fill in credentials
        page_desktop.fill('input[name="login"]', e2e_user.email)
        page_desktop.fill('input[name="password"]', "TestPass123!")

        # Press Enter in password field
        page_desktop.locator('input[name="password"]').press("Enter")

        # Should redirect to dashboard (Playwright auto-waits)
        page_desktop.wait_for_url(live_server.url + reverse("account-center"))
        expect(page_desktop).to_have_url(live_server.url + reverse("account-center"))
