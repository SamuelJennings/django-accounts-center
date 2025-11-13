"""Custom menu renderers for Django Accounts Center."""

from flex_menu.renderers import BaseRenderer


class SidebarRenderer(BaseRenderer):
    """Renderer for the account center sidebar menu.

    Used for the main navigation sidebar in account management pages.
    """

    templates = {
        0: {"default": "dac/menus/sidebar.html"},
        1: {
            "parent": "cotton/dac/menu/group.html",
            "leaf": "cotton/dac/menu/item.html",
        },
        "default": {
            "parent": "cotton/dac/menu/group.html",
            "leaf": "cotton/dac/menu/item.html",
        },
    }


class DropdownRenderer(BaseRenderer):
    """Renderer for dropdown menus in the account center.

    Used for user dropdown menus in the navbar.
    """

    templates = {
        0: {"default": "cotton/dac/dropdown/index.html"},
        "default": {
            "leaf": "cotton/dac/dropdown/item.html",
        },
    }
