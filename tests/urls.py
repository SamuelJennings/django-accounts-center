"""
Test URL configuration for integration tests.

Provides allauth account URLs without debug_toolbar or other
development-only dependencies.
"""

from django.contrib import admin
from django.urls import include, path

from example.views import EmailChangeTestView, _verified_email_required_view

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
