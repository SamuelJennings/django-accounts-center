"""
Test URL configuration for integration tests.

Provides allauth account URLs without debug_toolbar or other
development-only dependencies.
"""

from django.contrib import admin
from django.shortcuts import render
from django.urls import include, path

from allauth.account.views import EmailView


class EmailChangeTestView(EmailView):
    """EmailView subclass that forces account/email_change.html template.

    EmailView.template_name is a class-level attribute evaluated at import time,
    so per-test settings overrides cannot change which template allauth serves.
    This subclass hard-codes the email_change.html template for test isolation.
    """

    template_name = "account/email_change.html"


def _verified_email_required_view(request):
    """Render the verified_email_required gate page directly.

    In allauth 65.x this template is rendered inline by the
    @verified_email_required decorator; there is no registered URL for it.
    This test-only view registers a URL so tests can drive it via the client.
    """
    return render(request, "account/verified_email_required.html")


urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("allauth.urls")),
    path("account-center/", include("dac.urls")),
    # Test-only URLs — not part of the production URL configuration
    path(
        "test/email-change/",
        EmailChangeTestView.as_view(),
        name="account_email_change_test",
    ),
    path(
        "test/verified-email-required/",
        _verified_email_required_view,
        name="account_verified_email_required",
    ),
]
