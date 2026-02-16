"""
E2E Test Configuration and Fixtures

This module provides Playwright fixtures and configuration for end-to-end testing.
"""

import os
import re
from pathlib import Path

import pytest
from allauth.account.models import EmailAddress
from django.contrib.auth import get_user_model
from django.core import mail
from django.urls import reverse
from playwright.sync_api import Page, expect

User = get_user_model()

# Set environment variable to allow Django async-unsafe operations
# This is needed because Playwright creates an async event loop
# but Django's ORM operations (like database setup) are synchronous
os.environ.setdefault("DJANGO_ALLOW_ASYNC_UNSAFE", "true")


@pytest.fixture
def page_desktop(page: Page):
    """Fixture for desktop viewport (1920x1080)."""
    page.set_viewport_size({"width": 1920, "height": 1080})
    return page


@pytest.fixture
def page_tablet(page: Page):
    """Fixture for tablet viewport (768x1024)."""
    page.set_viewport_size({"width": 768, "height": 1024})
    return page


@pytest.fixture
def page_mobile(page: Page):
    """Fixture for mobile viewport (375x667)."""
    page.set_viewport_size({"width": 375, "height": 667})
    return page


@pytest.fixture(
    params=[
        {"width": 1920, "height": 1080},  # Desktop
        {"width": 768, "height": 1024},  # Tablet
        {"width": 375, "height": 667},  # Mobile
    ]
)
def page_all_viewports(page: Page, request):
    """Fixture that parametrizes tests across all viewport sizes."""
    page.set_viewport_size(request.param)
    return page


@pytest.fixture(scope="function")
def e2e_user(django_db_blocker):
    """Create a test user for E2E tests."""
    with django_db_blocker.unblock():
        # Clean up any existing user with this email
        User.objects.filter(email="e2e@example.com").delete()

        user = User.objects.create_user(
            username="e2e_testuser",
            email="e2e@example.com",
            password="TestPass123!",
            first_name="E2E",
            last_name="Tester",
        )
        # Create verified email
        EmailAddress.objects.create(user=user, email=user.email, verified=True, primary=True)
        yield user

        # Cleanup after test
        user.delete()


@pytest.fixture(scope="function")
def e2e_unverified_user(django_db_blocker):
    """Create a test user with unverified email for E2E tests."""
    with django_db_blocker.unblock():
        # Clean up any existing user with this email
        User.objects.filter(email="unverified@example.com").delete()

        user = User.objects.create_user(
            username="e2e_unverified",
            email="unverified@example.com",
            password="TestPass123!",
            first_name="Unverified",
            last_name="User",
        )
        # Create unverified email
        EmailAddress.objects.create(user=user, email=user.email, verified=False, primary=True)
        yield user

        # Cleanup after test
        user.delete()


@pytest.fixture
def screenshots_dir():
    """Create and return screenshots directory."""
    screenshots_path = Path(__file__).parent.parent.parent / "docs" / "_static" / "screenshots" / "e2e"
    screenshots_path.mkdir(parents=True, exist_ok=True)
    return screenshots_path


def login_user(page: Page, live_server_url: str, email: str, password: str):
    """
    Helper function to log in a user via the UI.

    Args:
        page: Playwright page object
        live_server_url: Base URL of the live server
        email: User email
        password: User password
    """
    page.goto(live_server_url + reverse("account_login"))
    page.fill('input[name="login"]', email)
    page.fill('input[name="password"]', password)
    # Click the main "Sign In" button, not the passkey button
    page.get_by_role("button", name="Sign In", exact=True).click()
    # Wait for redirect to complete (Playwright auto-waits)
    page.wait_for_url(live_server_url + reverse("account-center"))


def logout_user(page: Page, live_server_url: str):
    """
    Helper function to log out a user via the UI.

    Args:
        page: Playwright page object
        live_server_url: Base URL of the live server
    """
    logout_url_path = reverse("account_logout")
    # Click logout in user dropdown (desktop) or sidebar (mobile)
    # Try desktop dropdown first
    if page.locator(f'a[href="{logout_url_path}"]').first.is_visible():
        page.locator(f'a[href="{logout_url_path}"]').first.click()
    else:
        # Open mobile menu if needed
        if page.locator('button[data-bs-toggle="offcanvas"]').is_visible():
            page.locator('button[data-bs-toggle="offcanvas"]').click()
        page.locator(f'a[href="{logout_url_path}"]').first.click()

    # Confirm logout
    page.wait_for_url("**/account/logout/**")
    page.get_by_role("button", name="Sign Out", exact=True).click()
    page.wait_for_url("**/account/login/**")


def check_entrance_layout(page: Page):
    """
    Verify that the entrance layout is being used.

    Args:
        page: Playwright page object
    """
    expect(page.locator("#dac-entrance-layout")).to_be_visible()
    expect(page.locator(".min-vh-100.d-flex.align-items-center")).to_be_visible()


def check_standard_layout(page: Page):
    """
    Verify that the standard layout is being used.

    Args:
        page: Playwright page object
    """
    expect(page.locator("#sidebar")).to_be_attached()


def get_email_verification_url(email_index: int = -1) -> str | None:
    """
    Extract verification URL from sent emails.

    Args:
        email_index: Index of email to parse (default: -1 for latest)

    Returns:
        Verification URL if found, None otherwise
    """
    if not mail.outbox:
        return None

    email_body = mail.outbox[email_index].body
    # Extract URL from email body
    # Pattern matches /account-center/account/confirm-email/XXX:XXX/
    match = re.search(r"/account(-center)?/account/confirm-email/[^/\s]+/", email_body)
    if match:
        return match.group(0)
    return None


def get_password_reset_url(email_index: int = -1) -> str | None:
    """
    Extract password reset URL from sent emails.

    Args:
        email_index: Index of email to parse (default: -1 for latest)

    Returns:
        Password reset URL if found, None otherwise
    """
    if not mail.outbox:
        return None

    email_body = mail.outbox[email_index].body
    # Pattern matches /account-center/account/password/reset/key/XXX-XXX/
    match = re.search(r"/account(-center)?/account/password/reset/key/[^/\s]+/", email_body)
    if match:
        return match.group(0)
    return None


def verify_alert_message(page: Page, message_type: str, message_text: str | None = None):
    """
    Verify that an alert message is displayed.

    Args:
        page: Playwright page object
        message_type: Type of alert (success, warning, danger, info)
        message_text: Optional text to check in the message
    """
    alert = page.locator(f".alert.alert-{message_type}")
    expect(alert).to_be_visible()
    if message_text:
        expect(alert).to_contain_text(message_text, ignore_case=True)


def take_screenshot(
    page: Page,
    screenshots_dir: Path,
    name: str,
    full_page: bool = True,
    image_format: str = "png",
):
    """
    Take a screenshot and save it with organized subdirectories.

    Args:
        page: Playwright page object
        screenshots_dir: Base directory to save screenshots
        name: Screenshot filename in format "category/filename" or "filename"
              e.g., "login/filled_desktop" or "dashboard_view"
        full_page: Whether to capture full page or just viewport
        image_format: Image format - "png" or "jpeg" (default: png, best for UI screenshots)

    Returns:
        Path to the saved screenshot
    """
    # Parse the name to support subdirectories
    name_parts = name.split("/")
    if len(name_parts) > 1:
        # Create subdirectory if path contains /
        subdir = screenshots_dir / "/".join(name_parts[:-1])
        subdir.mkdir(parents=True, exist_ok=True)
        screenshot_path = subdir / f"{name_parts[-1]}.{image_format}"
    else:
        screenshot_path = screenshots_dir / f"{name}.{image_format}"

    # Take screenshot
    screenshot_type = "png" if image_format == "png" else "jpeg"
    page.screenshot(path=str(screenshot_path), full_page=full_page, type=screenshot_type)
    return screenshot_path


@pytest.fixture
def authenticated_page(page: Page, live_server, e2e_user):
    """
    Fixture that provides a page with an authenticated user session.

    Args:
        page: Playwright page object
        live_server: Django live server fixture
        e2e_user: E2E test user fixture

    Returns:
        Authenticated Playwright page
    """
    login_user(page, live_server.url, e2e_user.email, "TestPass123!")
    return page
