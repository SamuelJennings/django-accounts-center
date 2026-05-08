"""
Test URL configuration for integration tests.

Provides allauth account URLs without debug_toolbar or other
development-only dependencies.
"""

from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("allauth.urls")),
    path("account-center/", include("dac.urls")),
]
