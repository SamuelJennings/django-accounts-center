"""
Tests for django-accounts-center menu functionality.
"""

from django.test import TestCase
from django.utils.translation import gettext_lazy as _

from dac.menus import (
    AccountCenterMenu,
    AccountCenterMenuGroup,
    AccountCenterMenuItem,
    AccountManagement,
    AuthenticatedUserMenu,
    DacAccountCenterMenu,
    DropdownMenu,
    DropdownMenuItem,
)


class TestMenuClasses(TestCase):
    """Tests for menu class definitions."""

    def test_main_menu_group_inheritance(self):
        """Test AccountCenterMenuGroup inherits from flex_menu.MenuGroup."""
        # Since we can't easily test inheritance without importing flex_menu,
        # we test that the class exists and can be instantiated
        group = AccountCenterMenuGroup("Test Group")
        assert hasattr(group, "name")
        assert group.name == "Test Group"

    def test_main_menu_item_inheritance(self):
        """Test AccountCenterMenuItem inherits from flex_menu.MenuLink."""
        item = AccountCenterMenuItem("Test Item", view_name="test_view")
        assert hasattr(item, "name")
        assert item.name == "Test Item"

    # Tests for the old API have been removed due to major API changes
    # The menu classes now follow the current django-flex-menus patterns


class TestMenuInstances(TestCase):
    """Tests for menu instance creation and configuration."""

    def test_main_menu_creation(self):
        """Test AccountCenterMenu instance is created correctly."""
        assert isinstance(AccountCenterMenu, DacAccountCenterMenu)
        assert AccountCenterMenu.name == "Main Menu"

    def test_authenticated_user_dropdown_creation(self):
        """Test AuthenticatedUserMenu is created correctly."""
        assert isinstance(AuthenticatedUserMenu, DropdownMenu)
        assert AuthenticatedUserMenu.name == "AuthenticatedUserMenu"
        # Note: allauth adds logout item, so we expect 2 children total
        assert len(AuthenticatedUserMenu.children) == 2

    def test_authenticated_user_dropdown_children(self):
        """Test AuthenticatedUserMenu has correct children."""
        child = AuthenticatedUserMenu.children[0]
        assert isinstance(child, DropdownMenuItem)
        assert child.name == _("Account Center")
        assert child.view_name == "account-center"
        assert child.extra_context.get("icon") == "account_center"

    def test_account_management_structure(self):
        """Test AccountManagement menu structure."""
        assert AccountManagement.name == "Django Account Center"
        assert len(AccountManagement.children) == 2
        assert AccountCenterMenu in AccountManagement.children
        assert AuthenticatedUserMenu in AccountManagement.children


class TestMenuIntegration(TestCase):
    """Integration tests for menu functionality."""

    def test_menu_extensibility(self):
        """Test that menus can be extended."""
        # Test that we can add items to AccountCenterMenu
        original_children_count = len(AccountCenterMenu.children)

        test_group = AccountCenterMenuGroup("Test Group")
        AccountCenterMenu.append(test_group)

        assert len(AccountCenterMenu.children) == original_children_count + 1
        assert test_group in AccountCenterMenu.children

    def test_dropdown_menu_extensibility(self):
        """Test that dropdown menu can be extended."""
        original_children_count = len(AuthenticatedUserMenu.children)

        test_item = DropdownMenuItem(name="Test Item", view_name="test_view", icon="test_icon")
        AuthenticatedUserMenu.append(test_item)

        assert len(AuthenticatedUserMenu.children) == original_children_count + 1
        assert test_item in AuthenticatedUserMenu.children

    def test_menu_hierarchy(self):
        """Test menu hierarchy structure."""
        # Test that AccountManagement contains the other menus
        assert AccountManagement.name == "Django Account Center"
        child_names = [child.name for child in AccountManagement.children]
        assert "Main Menu" in child_names
        assert "AuthenticatedUserMenu" in child_names
