"""
Test URL configuration for integration tests.

Provides allauth account URLs without debug_toolbar or other
development-only dependencies.
"""

from django.contrib import admin
from django.shortcuts import render
from django.urls import include, path

from example.views import EmailChangeTestView, MultiEmailTestView, _verified_email_required_view


def _user_menu_no_avatar_view(request):
    return render(request, "test_user_menu_no_avatar.html")


def _user_menu_photo_view(request):
    return render(request, "test_user_menu_photo.html")


def _user_menu_custom_view(request):
    return render(request, "test_user_menu_custom.html")


class _MockAlternative:
    url = "/accounts/mock-mfa/"
    description = "Use authenticator code"


def _reauthenticate_with_alternatives_view(request):
    from allauth.account.forms import ReauthenticateForm

    form = ReauthenticateForm(user=request.user) if request.user.is_authenticated else None
    return render(
        request,
        "account/reauthenticate.html",
        {
            "form": form,
            "reauthentication_alternatives": [_MockAlternative()],
        },
    )


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
        "test/email-multi/",
        MultiEmailTestView.as_view(),
        name="account_email_multi_test",
    ),
    path(
        "test/verified-email-required/",
        _verified_email_required_view,
        name="account_verified_email_required",
    ),
    path(
        "test/reauthenticate-alternatives/",
        _reauthenticate_with_alternatives_view,
        name="test_reauthenticate_alternatives",
    ),
    # User menu screenshot test URLs
    path("test/user-menu/no-avatar/", _user_menu_no_avatar_view, name="test_user_menu_no_avatar"),
    path("test/user-menu/photo/", _user_menu_photo_view, name="test_user_menu_photo"),
    path("test/user-menu/custom/", _user_menu_custom_view, name="test_user_menu_custom"),
]
