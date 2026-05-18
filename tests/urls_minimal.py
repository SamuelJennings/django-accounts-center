"""
Minimal URL configuration for tests that verify graceful URL degradation.

Used by TestDacUserMenu tests that assert components render nothing when
account-center or account_logout URLs are not registered in the host app.
"""

from django.contrib import admin
from django.urls import path

urlpatterns = [
    path("admin/", admin.site.urls),
]
