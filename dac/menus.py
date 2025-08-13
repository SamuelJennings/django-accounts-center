import flex_menu
from django.utils.translation import gettext_lazy as _


class DacMainMenu(flex_menu.Menu):
    """
    This is the main menu for django-account-management which is displayed as a sidebar when editing user related
    information.
    """

    root_template = "dac/menus/sidebar.html"
    allowed_children = ("MainMenuGroup", "MainMenuItem")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for child in self.children:
            if child.__class__.__name__ not in self.allowed_children:
                raise ValueError(f"Child {child.__class__.__name__} is not allowed in {self.__class__.__name__}")


class MainMenuGroup(flex_menu.Menu):
    pass


class MainMenuItem(flex_menu.MenuItem):
    pass

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class DropdownMenu(flex_menu.Menu):
    """
    A menu that can be used in a dropdown.
    """

    root_template = "dac/menus/dropdown.html"
    allowed_children = ("DropdownMenuItem",)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for child in self.children:
            if child.__class__.__name__ not in self.allowed_children:
                raise ValueError(f"Child {child.__class__.__name__} is not allowed in {self.__class__.__name__}")


class DropdownMenuItem(flex_menu.MenuItem):
    """
    A menu item that can be used in a dropdown menu.
    """

    root_template = "dac/menus/dropdown_item.html"


# This is the main menu for django-account-management which is displayed as a sidebar when editing user related
# information.
MainMenu = DacMainMenu("Main Menu")

# This is the floating offcanvas menu which can be made available on any page
AuthenticatedUserDropdown = DropdownMenu(
    "AuthenticatedUserDropdown",
    children=[
        DropdownMenuItem(name=_("Account Center"), view_name="account-center", icon="account_center"),
    ],
)


# Groups all django-account-management menus under a single menu
AccountManagement = flex_menu.Menu(
    "Django Account Center",
    children=[MainMenu, AuthenticatedUserDropdown],
)
