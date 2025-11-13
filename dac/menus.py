"""
Django Account Center Menu Definitions

This module defines menu instances for the django-accounts-center package.
It integrates with django-flex-menus to provide structured navigation for account management.
"""

from django.utils.translation import gettext_lazy as _
from flex_menu import Menu, MenuItem
from flex_menu.checks import user_is_authenticated

# Main menu instance for django-account-center
AccountCenterMenu = Menu(
    name="Account Center Menu",
)

AuthenticatedUserMenu = Menu(
    name="AuthenticatedUserMenu",
    children=[
        MenuItem(
            name=_("Account Center"),
            view_name="account-center",
            extra_context={"icon": "account_center", "description": _("Manage your account")},
            check=user_is_authenticated,
        ),
    ],
)

# Groups all django-account-center menus under a single menu
AccountManagement = Menu(
    name=_("Django Account Center"),
    children=[AccountCenterMenu, AuthenticatedUserMenu],
)
