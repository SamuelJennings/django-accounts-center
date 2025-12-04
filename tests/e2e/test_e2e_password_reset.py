"""
E2E tests for password reset flow.

This module tests the complete password reset workflow including:
- Requesting password reset
- Email confirmation
- Password reset form
- Successful login with new password
"""

import pytest
from django.core import mail
from django.urls import reverse
from playwright.sync_api import Page, expect

from tests.e2e.conftest import (
    get_password_reset_url,
    take_screenshot,
)

# Mark all tests in this module for e2e and Django DB with transactional mode
pytestmark = [pytest.mark.e2e, pytest.mark.django_db(transaction=True)]


@pytest.mark.django_db
class TestPasswordResetFlow:
    """Test password reset workflow."""

    def test_password_reset_request_sends_email(self, page_desktop: Page, live_server, e2e_user, screenshots_dir):
        """Test that requesting password reset sends email."""
        # Clear mail outbox
        mail.outbox = []

        page_desktop.goto(live_server.url + reverse("account_reset_password"))

        # Fill in email
        page_desktop.fill('input[name="email"]', e2e_user.email)

        # Take screenshot before submit
        take_screenshot(page_desktop, screenshots_dir, "password_reset_form_filled_desktop")

        # Submit form
        page_desktop.click('button[type="submit"]')

        # Should redirect to confirmation page
        password_reset_done_url = reverse("account_reset_password_done")
        page_desktop.wait_for_url(f"**{password_reset_done_url}")

        # Verify confirmation message
        expect(page_desktop.locator("h1")).to_contain_text("Password Reset")

        # Take screenshot of confirmation
        take_screenshot(page_desktop, screenshots_dir, "password_reset_email_sent_desktop")

        # Verify email was sent
        assert len(mail.outbox) == 1
        assert e2e_user.email in mail.outbox[0].to

    def test_complete_password_reset_flow(self, page_desktop: Page, live_server, e2e_user, screenshots_dir):
        """Test complete password reset flow from start to finish."""
        # Clear mail outbox
        mail.outbox = []

        # Step 1: Request password reset
        page_desktop.goto(live_server.url + reverse("account_reset_password"))
        page_desktop.fill('input[name="email"]', e2e_user.email)
        page_desktop.click('button[type="submit"]')

        # Wait for email confirmation page
        password_reset_done_url = reverse("account_reset_password_done")
        page_desktop.wait_for_url(f"**{password_reset_done_url}")

        # Step 2: Get reset URL from email
        reset_url = get_password_reset_url()
        assert reset_url is not None, "Password reset URL not found in email"

        # Step 3: Navigate to reset URL
        page_desktop.goto(f"{live_server.url}{reset_url}")

        # Should show password reset form
        expect(page_desktop.locator('input[name="password1"]')).to_be_visible()
        expect(page_desktop.locator('input[name="password2"]')).to_be_visible()

        # Take screenshot of reset form
        take_screenshot(page_desktop, screenshots_dir, "password_reset_form_desktop")

        # Step 4: Enter new password
        new_password = "NewTestPass456!"
        page_desktop.fill('input[name="password1"]', new_password)
        page_desktop.fill('input[name="password2"]', new_password)

        # Take screenshot with filled form
        take_screenshot(page_desktop, screenshots_dir, "password_reset_new_password_desktop")

        # Submit new password
        page_desktop.click('button[type="submit"]')

        # Take screenshot of success page
        take_screenshot(page_desktop, screenshots_dir, "password_reset_success_desktop")

        # Step 5: Verify can login with new password
        page_desktop.goto(live_server.url + reverse("account_login"))
        page_desktop.fill('input[name="login"]', e2e_user.email)
        page_desktop.fill('input[name="password"]', new_password)
        page_desktop.click('button[type="submit"]')

        # Should redirect to dashboard
        page_desktop.wait_for_url(live_server.url + reverse("account-center"))
        expect(page_desktop).to_have_url(live_server.url + reverse("account-center"))

        # Take screenshot of successful login with new password
        take_screenshot(page_desktop, screenshots_dir, "login_with_new_password_desktop")

    def test_password_reset_with_invalid_email(self, page_desktop: Page, live_server, screenshots_dir):
        """Test password reset with email that doesn't exist."""
        # Clear mail outbox
        mail.outbox = []

        page_desktop.goto(live_server.url + reverse("account_reset_password"))

        # Fill in non-existent email
        page_desktop.fill('input[name="email"]', "nonexistent@example.com")
        page_desktop.click('button[type="submit"]')

        # Should still redirect to confirmation page (security best practice)
        password_reset_done_url = reverse("account_reset_password_done")
        page_desktop.wait_for_url(f"**{password_reset_done_url}")

        # But no email should be sent
        assert len(mail.outbox) == 0

        # Take screenshot
        take_screenshot(page_desktop, screenshots_dir, "password_reset_invalid_email_desktop")


@pytest.mark.django_db
class TestPasswordResetMobile:
    """Test password reset on mobile viewport."""

    def test_complete_password_reset_mobile(self, page_mobile: Page, live_server, e2e_user, screenshots_dir):
        """Test complete password reset flow on mobile."""
        # Clear mail outbox
        mail.outbox = []

        # Request password reset
        page_mobile.goto(live_server.url + reverse("account_reset_password"))
        page_mobile.fill('input[name="email"]', e2e_user.email)
        page_mobile.click('button[type="submit"]')

        # Wait for confirmation
        password_reset_done_url = reverse("account_reset_password_done")
        page_mobile.wait_for_url(f"**{password_reset_done_url}")

        # Get reset URL
        reset_url = get_password_reset_url()
        assert reset_url is not None

        # Navigate to reset form
        page_mobile.goto(f"{live_server.url}{reset_url}")

        # Fill new password
        new_password = "MobileNewPass789!"
        page_mobile.fill('input[name="password1"]', new_password)
        page_mobile.fill('input[name="password2"]', new_password)

        # Take screenshot
        take_screenshot(page_mobile, screenshots_dir, "password_reset_form_mobile")

        # Submit
        page_mobile.click('button[type="submit"]')

        # Wait for success
        page_mobile.wait_for_timeout(2000)

        # Login with new password
        page_mobile.goto(live_server.url + reverse("account_login"))
        page_mobile.fill('input[name="login"]', e2e_user.email)
        page_mobile.fill('input[name="password"]', new_password)
        page_mobile.click('button[type="submit"]')

        # Should reach dashboard
        page_mobile.wait_for_url(live_server.url + reverse("account-center"))
        expect(page_mobile).to_have_url(live_server.url + reverse("account-center"))


@pytest.mark.django_db
class TestPasswordResetValidation:
    """Test password reset form validation."""

    def test_password_reset_mismatched_passwords(self, page_desktop: Page, live_server, e2e_user, screenshots_dir):
        """Test password reset with mismatched passwords."""
        # Clear mail outbox
        mail.outbox = []

        # Request reset
        page_desktop.goto(live_server.url + reverse("account_reset_password"))
        page_desktop.fill('input[name="email"]', e2e_user.email)
        page_desktop.click('button[type="submit"]')

        # Wait for email
        password_reset_done_url = reverse("account_reset_password_done")
        page_desktop.wait_for_url(f"**{password_reset_done_url}")

        # Get reset URL
        reset_url = get_password_reset_url()
        assert reset_url is not None

        # Navigate to reset form
        page_desktop.goto(f"{live_server.url}{reset_url}")

        # Enter mismatched passwords
        page_desktop.fill('input[name="password1"]', "NewPass123!")
        page_desktop.fill('input[name="password2"]', "DifferentPass456!")

        # Submit
        page_desktop.click('button[type="submit"]')

        # Should show error (expect auto-waits)
        error_message = page_desktop.locator(".alert-danger, .errorlist")
        expect(error_message.first).to_be_visible()

        # Take screenshot
        take_screenshot(page_desktop, screenshots_dir, "password_reset_mismatch_desktop")

    def test_password_reset_weak_password(self, page_desktop: Page, live_server, e2e_user, screenshots_dir):
        """Test password reset with weak password."""
        # Clear mail outbox
        mail.outbox = []

        # Request reset
        page_desktop.goto(live_server.url + reverse("account_reset_password"))
        page_desktop.fill('input[name="email"]', e2e_user.email)
        page_desktop.click('button[type="submit"]')

        # Wait for email
        password_reset_done_url = reverse("account_reset_password_done")
        page_desktop.wait_for_url(f"**{password_reset_done_url}")

        # Get reset URL
        reset_url = get_password_reset_url()
        assert reset_url is not None

        # Navigate to reset form
        page_desktop.goto(f"{live_server.url}{reset_url}")

        # Enter weak password
        weak_password = "123"
        page_desktop.fill('input[name="password1"]', weak_password)
        page_desktop.fill('input[name="password2"]', weak_password)

        # Submit
        page_desktop.click('button[type="submit"]')

        # Error should be visible (expect auto-waits)
        error = page_desktop.locator(".alert-danger, .errorlist")
        expect(error.first).to_be_visible()

        # Take screenshot
        take_screenshot(page_desktop, screenshots_dir, "password_reset_weak_password_desktop")


@pytest.mark.django_db
class TestPasswordResetSecurity:
    """Test password reset security features."""

    def test_old_password_doesnt_work_after_reset(self, page_desktop: Page, live_server, e2e_user):
        """Test that old password no longer works after reset."""
        old_password = "TestPass123!"
        new_password = "BrandNewPass999!"

        # Clear mail outbox
        mail.outbox = []

        # Request password reset
        page_desktop.goto(live_server.url + reverse("account_reset_password"))
        page_desktop.fill('input[name="email"]', e2e_user.email)
        page_desktop.click('button[type="submit"]')

        # Wait and get reset URL
        password_reset_done_url = reverse("account_reset_password_done")
        page_desktop.wait_for_url(f"**{password_reset_done_url}")
        reset_url = get_password_reset_url()
        assert reset_url is not None

        # Complete password reset
        page_desktop.goto(f"{live_server.url}{reset_url}")
        page_desktop.fill('input[name="password1"]', new_password)
        page_desktop.fill('input[name="password2"]', new_password)
        page_desktop.click('button[type="submit"]')

        # Try to login with old password
        page_desktop.goto(live_server.url + reverse("account_login"))
        page_desktop.fill('input[name="login"]', e2e_user.email)
        page_desktop.fill('input[name="password"]', old_password)
        page_desktop.click('button[type="submit"]')

        # Should fail (stay on login page)
        login_url = reverse("account_login")
        assert login_url in page_desktop.url

        # Try with new password
        page_desktop.fill('input[name="login"]', e2e_user.email)
        page_desktop.fill('input[name="password"]', new_password)
        page_desktop.click('button[type="submit"]')

        # Should succeed
        page_desktop.wait_for_url(live_server.url + reverse("account-center"))
        expect(page_desktop).to_have_url(live_server.url + reverse("account-center"))
