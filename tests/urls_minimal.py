"""
Minimal URL configuration for tests that verify graceful URL degradation.

Used by TestDacUserMenu tests that assert components render nothing when
account-center or account_logout URLs are not registered in the host app,
and by the integration-contract tests that open the test integration's own
page with no dac URL — allauth's or dac's own — registered at all.
"""

from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    # The test integration's own URLs only — nothing from dac.urls, so this
    # stands in for a host project where dac.allauth (or dac itself) was
    # never mounted.
    path("test/testapp/", include("tests.testapp.urls")),
]
