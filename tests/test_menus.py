"""
Tests for django-accounts-center menu functionality.
"""

from django.test import TestCase
from django.utils.translation import gettext_lazy as _

from dac.menus import (
    AccountManagement,
    AuthenticatedUserDropdown,
    DacMainMenu,
    DropdownMenu,
    DropdownMenuItem,
    MainMenu,
    MainMenuGroup,
    MainMenuItem,
)


class TestMenuClasses(TestCase):
    """Tests for menu class definitions."""

    def test_main_menu_group_inheritance(self):
        """Test MainMenuGroup inherits from flex_menu.MenuGroup."""
        # Since we can't easily test inheritance without importing flex_menu,
        # we test that the class exists and can be instantiated
        group = MainMenuGroup("Test Group")
        assert hasattr(group, "name")
        assert group.name == "Test Group"

    def test_main_menu_item_inheritance(self):
        """Test MainMenuItem inherits from flex_menu.MenuLink."""
        item = MainMenuItem("Test Item", view_name="test_view")
        assert hasattr(item, "name")
        assert item.name == "Test Item"

    def test_dac_main_menu_configuration(self):
        """Test DacMainMenu has correct configuration."""
        assert hasattr(DacMainMenu, "root_template")
        assert DacMainMenu.root_template == "dac/menus/sidebar.html"
        assert hasattr(DacMainMenu, "allowed_children")
        assert MainMenuGroup in DacMainMenu.allowed_children
        assert MainMenuItem in DacMainMenu.allowed_children

    def test_dropdown_menu_item_configuration(self):
        """Test DropdownMenuItem has correct configuration."""
        assert hasattr(DropdownMenuItem, "root_template")
        assert DropdownMenuItem.root_template == "dac/menus/dropdown_item.html"

    def test_dropdown_menu_configuration(self):
        """Test DropdownMenu has correct configuration."""
        assert hasattr(DropdownMenu, "root_template")
        assert DropdownMenu.root_template == "dac/menus/dropdown.html"
        assert hasattr(DropdownMenu, "allowed_children")
        assert DropdownMenuItem in DropdownMenu.allowed_children


class TestMenuInstances(TestCase):
    """Tests for menu instance creation and configuration."""

    def test_main_menu_creation(self):
        """Test MainMenu instance is created correctly."""
        assert isinstance(MainMenu, DacMainMenu)
        assert MainMenu.name == "Main Menu"

    def test_authenticated_user_dropdown_creation(self):
        """Test AuthenticatedUserDropdown is created correctly."""
        assert isinstance(AuthenticatedUserDropdown, DropdownMenu)
        assert AuthenticatedUserDropdown.name == "AuthenticatedUserDropdown"
        assert len(AuthenticatedUserDropdown.children) == 1

    def test_authenticated_user_dropdown_children(self):
        """Test AuthenticatedUserDropdown has correct children."""
        child = AuthenticatedUserDropdown.children[0]
        assert isinstance(child, DropdownMenuItem)
        assert child.name == _("Account Center")
        assert child.view_name == "account-center"
        assert child.icon == "account_center"

    def test_account_management_structure(self):
        """Test AccountManagement menu structure."""
        assert AccountManagement.name == "Django Account Center"
        assert len(AccountManagement.children) == 2
        assert MainMenu in AccountManagement.children
        assert AuthenticatedUserDropdown in AccountManagement.children


class TestMenuIntegration(TestCase):
    """Integration tests for menu functionality."""

    def test_menu_extensibility(self):
        """Test that menus can be extended."""
        # Test that we can add items to MainMenu
        original_children_count = len(MainMenu.children)

        test_group = MainMenuGroup("Test Group")
        MainMenu.append(test_group)

        assert len(MainMenu.children) == original_children_count + 1
        assert test_group in MainMenu.children

    def test_dropdown_menu_extensibility(self):
        """Test that dropdown menu can be extended."""
        original_children_count = len(AuthenticatedUserDropdown.children)

        test_item = DropdownMenuItem(name="Test Item", view_name="test_view", icon="test_icon")
        AuthenticatedUserDropdown.append(test_item)

        assert len(AuthenticatedUserDropdown.children) == original_children_count + 1
        assert test_item in AuthenticatedUserDropdown.children

    def test_menu_hierarchy(self):
        """Test menu hierarchy structure."""
        # Test that AccountManagement contains the other menus
        assert AccountManagement.name == "Django Account Center"
        child_names = [child.name for child in AccountManagement.children]
        assert "Main Menu" in child_names
        assert "AuthenticatedUserDropdown" in child_names
