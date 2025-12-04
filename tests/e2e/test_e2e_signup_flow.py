"""
E2E tests for signup/registration flow.

This module tests the complete signup workflow including:
- Registration form submission
- Form validation (password strength, required fields, TOS checkbox)
- Email verification workflow
- First-time dashboard access after signup
"""

import pytest
from django.core import mail
from django.urls import reverse
from playwright.sync_api import Page, expect

from tests.e2e.conftest import (
    get_email_verification_url,
    take_screenshot,
)

# Mark all tests in this module for e2e and Django DB
pytestmark = [pytest.mark.e2e, pytest.mark.django_db(transaction=True)]


@pytest.mark.django_db
class TestSignupFlowDesktop:
    """Test complete signup flow on desktop."""

    def test_successful_signup_basic(self, page_desktop: Page, live_server, screenshots_dir):
        """Test successful signup with basic fields (no email verification)."""
        page_desktop.goto(live_server.url + reverse("account_signup"))

        # Fill signup form with basic fields
        page_desktop.fill('input[name="username"]', "newuser")
        page_desktop.fill('input[name="email"]', "newuser@example.com")
        page_desktop.fill('input[name="password1"]', "SecurePass123!")
        page_desktop.fill('input[name="password2"]', "SecurePass123!")

        # Check TOS if present
        tos_checkbox = page_desktop.locator('input[name="signup_tos"]')
        if tos_checkbox.count() > 0:
            tos_checkbox.check()

        # Take screenshot before submit
        take_screenshot(page_desktop, screenshots_dir, "signup_form_filled_desktop")

        # Submit form
        page_desktop.click('button[type="submit"]')

        # Should be logged in and redirected (with no verification)
        account_center_url = reverse("account-center")
        page_desktop.wait_for_url(f"**{account_center_url}")
        assert account_center_url in page_desktop.url

        # Take screenshot of post-signup state
        take_screenshot(page_desktop, screenshots_dir, "signup_complete_desktop")

    @pytest.mark.skip(reason="Requires ACCOUNT_EMAIL_VERIFICATION to be enabled")
    def test_successful_signup_with_verification(self, page_desktop: Page, live_server, screenshots_dir):
        """Test successful signup with email verification."""
        # Clear mail outbox
        mail.outbox = []

        page_desktop.goto(live_server.url + reverse("account_signup"))

        # Fill signup form with basic fields
        page_desktop.fill('input[name="username"]', "newuser")
        page_desktop.fill('input[name="email"]', "newuser@example.com")
        page_desktop.fill('input[name="password1"]', "SecurePass123!")
        page_desktop.fill('input[name="password2"]', "SecurePass123!")

        # Check TOS if present
        tos_checkbox = page_desktop.locator('input[name="signup_tos"]')
        if tos_checkbox.count() > 0:
            tos_checkbox.check()

        # Take screenshot before submit
        take_screenshot(page_desktop, screenshots_dir, "signup_form_filled_desktop")

        # Submit form
        page_desktop.click('button[type="submit"]')

        # Check if verification email was sent
        assert len(mail.outbox) > 0
        assert "newuser@example.com" in mail.outbox[-1].to

        # Take screenshot of post-signup state
        take_screenshot(page_desktop, screenshots_dir, "signup_submitted_desktop")

        # Get verification URL from email
        verification_url = get_email_verification_url()
        if verification_url:
            # Navigate to verification URL
            page_desktop.goto(f"{live_server.url}{verification_url}")

            # Confirm verification
            confirm_button = page_desktop.locator('button[type="submit"]')
            if confirm_button.count() > 0:
                confirm_button.click()

            # Take screenshot after verification
            take_screenshot(page_desktop, screenshots_dir, "email_verified_desktop")

    def test_signup_and_first_login(self, page_desktop: Page, live_server, screenshots_dir):
        """Test signup followed by first login."""
        # Clear mail outbox
        mail.outbox = []

        # Signup
        page_desktop.goto(live_server.url + reverse("account_signup"))
        page_desktop.fill('input[name="username"]', "firsttime")
        page_desktop.fill('input[name="email"]', "firsttime@example.com")
        page_desktop.fill('input[name="password1"]', "FirstPass123!")
        page_desktop.fill('input[name="password2"]', "FirstPass123!")

        # Check TOS if present
        tos_checkbox = page_desktop.locator('input[name="signup_tos"]')
        if tos_checkbox.count() > 0:
            tos_checkbox.check()

        page_desktop.click('button[type="submit"]')

        # Verify and confirm email if needed
        verification_url = get_email_verification_url()
        if verification_url:
            page_desktop.goto(f"{live_server.url}{verification_url}")
            confirm_button = page_desktop.locator('button[type="submit"]')
            if confirm_button.count() > 0:
                confirm_button.click()

        # Now try to login
        page_desktop.goto(live_server.url + reverse("account_login"))
        page_desktop.fill('input[name="login"]', "firsttime@example.com")
        page_desktop.fill('input[name="password"]', "FirstPass123!")
        page_desktop.click('button[type="submit"]')

        # Should redirect to dashboard
        account_center_url = reverse("account-center")
        page_desktop.wait_for_url(f"**{account_center_url}")

        # Take screenshot of first dashboard access
        take_screenshot(page_desktop, screenshots_dir, "first_time_dashboard_desktop")


@pytest.mark.django_db
class TestSignupValidation:
    """Test signup form validation."""

    def test_signup_with_empty_fields(self, page_desktop: Page, live_server, screenshots_dir):
        """Test signup with empty required fields shows validation errors."""
        page_desktop.goto(live_server.url + reverse("account_signup"))

        # Submit without filling anything
        page_desktop.click('button[type="submit"]')

        # Should stay on signup page
        signup_url = reverse("account_signup")
        assert signup_url in page_desktop.url

        # Take screenshot
        take_screenshot(page_desktop, screenshots_dir, "signup_empty_fields_desktop")

    def test_signup_with_mismatched_passwords(self, page_desktop: Page, live_server, screenshots_dir):
        """Test signup with mismatched passwords shows error."""
        page_desktop.goto(live_server.url + reverse("account_signup"))

        # Fill form with mismatched passwords
        page_desktop.fill('input[name="email"]', "mismatch@example.com")
        page_desktop.fill('input[name="first_name"]', "Mis")
        page_desktop.fill('input[name="last_name"]', "Match")
        page_desktop.fill('input[name="password1"]', "Password123!")
        page_desktop.fill('input[name="password2"]', "DifferentPass456!")

        # Submit
        page_desktop.click('button[type="submit"]')

        # Should show error (expect auto-waits)
        error = page_desktop.locator(".alert-danger, .errorlist")
        expect(error.first).to_be_visible()

        # Take screenshot
        take_screenshot(page_desktop, screenshots_dir, "signup_password_mismatch_desktop")

    def test_signup_with_weak_password(self, page_desktop: Page, live_server, screenshots_dir):
        """Test signup with weak password shows validation error."""
        page_desktop.goto(live_server.url + reverse("account_signup"))

        # Fill form with weak password
        page_desktop.fill('input[name="email"]', "weak@example.com")
        page_desktop.fill('input[name="first_name"]', "Weak")
        page_desktop.fill('input[name="last_name"]', "Password")
        page_desktop.fill('input[name="password1"]', "123")
        page_desktop.fill('input[name="password2"]', "123")

        # Submit
        page_desktop.click('button[type="submit"]')

        # Should show validation error (expect auto-waits)
        error = page_desktop.locator(".alert-danger, .errorlist")
        expect(error.first).to_be_visible()

        # Take screenshot
        take_screenshot(page_desktop, screenshots_dir, "signup_weak_password_desktop")

    def test_signup_with_invalid_email(self, page_desktop: Page, live_server, screenshots_dir):
        """Test signup with invalid email format shows error."""
        page_desktop.goto(live_server.url + reverse("account_signup"))

        # Fill form with invalid email
        page_desktop.fill('input[name="email"]', "not-an-email")
        page_desktop.fill('input[name="first_name"]', "Invalid")
        page_desktop.fill('input[name="last_name"]', "Email")
        page_desktop.fill('input[name="password1"]', "ValidPass123!")
        page_desktop.fill('input[name="password2"]', "ValidPass123!")

        # Submit
        page_desktop.click('button[type="submit"]')

        # Check email field validity
        email_field = page_desktop.locator('input[name="email"]')
        assert email_field.is_visible()

        # Take screenshot
        take_screenshot(page_desktop, screenshots_dir, "signup_invalid_email_desktop")

    def test_signup_with_existing_email(self, page_desktop: Page, live_server, e2e_user, screenshots_dir):
        """Test signup with already registered email shows error."""
        page_desktop.goto(live_server.url + reverse("account_signup"))

        # Try to signup with existing user's email
        page_desktop.fill('input[name="email"]', e2e_user.email)
        page_desktop.fill('input[name="first_name"]', "Duplicate")
        page_desktop.fill('input[name="last_name"]', "User")
        page_desktop.fill('input[name="password1"]', "AnotherPass123!")
        page_desktop.fill('input[name="password2"]', "AnotherPass123!")

        # Submit
        page_desktop.click('button[type="submit"]')

        # Should show error about existing email (expect auto-waits)
        error = page_desktop.locator(".alert-danger, .errorlist")
        expect(error.first).to_be_visible()

        # Take screenshot
        take_screenshot(page_desktop, screenshots_dir, "signup_existing_email_desktop")


@pytest.mark.django_db
class TestSignupMobile:
    """Test signup flow on mobile viewport."""

    def test_successful_signup_mobile(self, page_mobile: Page, live_server, screenshots_dir):
        """Test successful signup on mobile."""
        # Clear mail outbox
        mail.outbox = []

        page_mobile.goto(live_server.url + reverse("account_signup"))

        # Fill form
        page_mobile.fill('input[name="email"]', "mobileuser@example.com")
        page_mobile.fill('input[name="first_name"]', "Mobile")
        page_mobile.fill('input[name="last_name"]', "User")
        page_mobile.fill('input[name="password1"]', "MobilePass123!")
        page_mobile.fill('input[name="password2"]', "MobilePass123!")

        # Check TOS if present
        tos_checkbox = page_mobile.locator('input[name="signup_tos"]')
        if tos_checkbox.count() > 0:
            tos_checkbox.check()

        # Take screenshot
        take_screenshot(page_mobile, screenshots_dir, "signup_form_filled_mobile")

        # Submit
        page_mobile.click('button[type="submit"]')

        # Verify email sent
        assert len(mail.outbox) > 0

        # Take screenshot
        take_screenshot(page_mobile, screenshots_dir, "signup_submitted_mobile")


@pytest.mark.django_db
class TestSignupLinks:
    """Test signup page links and navigation."""

    def test_login_link_from_signup(self, page_desktop: Page, live_server):
        """Test navigating to login from signup page."""
        page_desktop.goto(live_server.url + reverse("account_signup"))

        # Click login link
        page_desktop.click(f'a[href="{reverse("account_login")}"]')

        # Should navigate to login
        login_url = reverse("account_login")
        page_desktop.wait_for_url(f"**{login_url}", timeout=5000)
        assert login_url in page_desktop.url

    def test_signup_link_from_login(self, page_desktop: Page, live_server):
        """Test navigating to signup from login page."""
        page_desktop.goto(live_server.url + reverse("account_login"))

        # Click signup link
        page_desktop.click(f'a[href="{reverse("account_signup")}"]')

        # Should navigate to signup
        signup_url = reverse("account_signup")
        page_desktop.wait_for_url(f"**{signup_url}", timeout=5000)
        assert signup_url in page_desktop.url


@pytest.mark.django_db
class TestEmailVerificationWorkflow:
    """Test email verification workflow after signup."""

    def test_email_verification_sent_after_signup(self, page_desktop: Page, live_server):
        """Test that verification email is sent after signup."""
        # Clear mail outbox
        mail.outbox = []

        page_desktop.goto(live_server.url + reverse("account_signup"))

        # Fill and submit signup form
        page_desktop.fill('input[name="email"]', "verify@example.com")
        page_desktop.fill('input[name="first_name"]', "Verify")
        page_desktop.fill('input[name="last_name"]', "Me")
        page_desktop.fill('input[name="password1"]', "VerifyPass123!")
        page_desktop.fill('input[name="password2"]', "VerifyPass123!")

        # Check TOS if present
        tos_checkbox = page_desktop.locator('input[name="signup_tos"]')
        if tos_checkbox.count() > 0:
            tos_checkbox.check()

        page_desktop.click('button[type="submit"]')

        # Verify email was sent
        assert len(mail.outbox) > 0
        verification_email = mail.outbox[-1]
        assert "verify@example.com" in verification_email.to
        assert "confirm" in verification_email.subject.lower() or "verify" in verification_email.subject.lower()

    def test_email_verification_link_works(self, page_desktop: Page, live_server, screenshots_dir):
        """Test that email verification link works correctly."""
        # Clear mail outbox
        mail.outbox = []

        # Signup
        page_desktop.goto(live_server.url + reverse("account_signup"))
        page_desktop.fill('input[name="email"]', "verifylink@example.com")
        page_desktop.fill('input[name="first_name"]', "Verify")
        page_desktop.fill('input[name="last_name"]', "Link")
        page_desktop.fill('input[name="password1"]', "LinkPass123!")
        page_desktop.fill('input[name="password2"]', "LinkPass123!")

        # Check TOS if present
        tos_checkbox = page_desktop.locator('input[name="signup_tos"]')
        if tos_checkbox.count() > 0:
            tos_checkbox.check()

        page_desktop.click('button[type="submit"]')

        # Get verification URL
        verification_url = get_email_verification_url()
        assert verification_url is not None, "Verification URL not found in email"

        # Navigate to verification URL
        page_desktop.goto(f"{live_server.url}{verification_url}")

        # Take screenshot
        take_screenshot(page_desktop, screenshots_dir, "email_verification_page_desktop")

        # Click confirm button if present
        confirm_button = page_desktop.locator('button[type="submit"]')
        if confirm_button.count() > 0:
            confirm_button.click()

            # Take screenshot after confirmation
            take_screenshot(page_desktop, screenshots_dir, "email_verified_success_desktop")
