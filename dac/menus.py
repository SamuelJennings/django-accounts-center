"""
Django Account Center Menu Definitions

This module defines menu classes and instances for the django-accounts-center package.
It integrates with django-flex-menus to provide structured navigation for account management.
"""

import flex_menu
from django.utils.translation import gettext_lazy as _


class MainMenuItem(flex_menu.MenuLink):
    """Individual menu item for the main account center menu."""

    template_name = "cotton/dac/menu/item.html"


class MainMenuGroup(flex_menu.MenuGroup):
    """Menu group for organizing main menu items."""

    template_name = "cotton/dac/menu/group.html"
    allowed_children = [MainMenuItem]


class DacMainMenu(flex_menu.MenuGroup):
    """
    Main menu for django-account-center displayed as a sidebar
    when editing user-related information.
    """

    template_name = "dac/menus/sidebar.html"
    allowed_children = [MainMenuGroup]


class DropdownMenuItem(flex_menu.MenuLink):
    """Menu item that can be used in a dropdown menu."""

    template_name = "dac/menus/dropdown_item.html"


class DropdownMenu(flex_menu.MenuGroup):
    """Menu container for dropdown menu items."""

    template_name = "dac/menus/dropdown.html"
    allowed_children = [DropdownMenuItem]


# Main menu instance for django-account-center
# Displayed as a sidebar when editing user-related information
MainMenu = DacMainMenu("Main Menu")

# Floating offcanvas menu available on any page
AuthenticatedUserDropdown = DropdownMenu(
    "AuthenticatedUserDropdown",
    children=[
        DropdownMenuItem(name=_("Account Center"), view_name="account-center", icon="account_center"),
    ],
)

# Groups all django-account-center menus under a single menu
AccountManagement = flex_menu.MenuGroup(
    "Django Account Center",
    children=[MainMenu, AuthenticatedUserDropdown],
)
