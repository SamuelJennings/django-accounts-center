"""
Tests for django-accounts-center menu functionality.
"""

import pytest
from django.utils.translation import gettext_lazy as _
from flex_menu import Menu, MenuItem

from dac.menus import AccountCenterMenu, AccountManagement, AuthenticatedUserMenu


@pytest.mark.django_db
class TestMenuInstances:
    """Tests for menu instance creation and configuration."""

    def test_account_center_menu_exists(self):
        """Test AccountCenterMenu instance exists and is a Menu."""
        assert isinstance(AccountCenterMenu, Menu)
        assert AccountCenterMenu.name == "Account Center Menu"

    def test_authenticated_user_menu_exists(self):
        """Test AuthenticatedUserMenu is created correctly."""
        assert isinstance(AuthenticatedUserMenu, Menu)
        assert AuthenticatedUserMenu.name == "AuthenticatedUserMenu"
        # Should have at least the Account Center menu item
        assert len(AuthenticatedUserMenu.children) >= 1

    def test_authenticated_user_menu_children(self):
        """Test AuthenticatedUserMenu has correct Account Center child."""
        child = AuthenticatedUserMenu.children[0]
        assert isinstance(child, MenuItem)
        assert child.name == _("Account Center")
        assert child.view_name == "account-center"
        assert child.extra_context.get("icon") == "account_center"
        assert child.extra_context.get("description") == _("Manage your account")

    def test_account_management_structure(self):
        """Test AccountManagement menu structure."""
        assert isinstance(AccountManagement, Menu)
        assert AccountManagement.name == _("Django Account Center")
        assert len(AccountManagement.children) == 2
        assert AccountCenterMenu in AccountManagement.children
        assert AuthenticatedUserMenu in AccountManagement.children


@pytest.mark.django_db
class TestMenuExtensibility:
    """Integration tests for menu extensibility."""

    def test_account_center_menu_can_be_extended(self):
        """Test that AccountCenterMenu can have items added."""
        # Store original children count
        original_children_count = len(AccountCenterMenu.children)

        # Add a test item using append method
        test_item = MenuItem(name="Test Item", view_name="test_view")
        AccountCenterMenu.append(test_item)

        try:
            assert len(AccountCenterMenu.children) == original_children_count + 1
            assert test_item in AccountCenterMenu.children
        finally:
            # Clean up - detach the test item
            test_item.parent = None

    def test_authenticated_user_menu_can_be_extended(self):
        """Test that AuthenticatedUserMenu can have items added."""
        original_children_count = len(AuthenticatedUserMenu.children)

        test_item = MenuItem(name="Test Item", view_name="test_view", extra_context={"icon": "test_icon"})
        AuthenticatedUserMenu.append(test_item)

        try:
            assert len(AuthenticatedUserMenu.children) == original_children_count + 1
            assert test_item in AuthenticatedUserMenu.children
        finally:
            # Clean up - detach the test item
            test_item.parent = None


@pytest.mark.django_db
class TestMenuHierarchy:
    """Tests for menu hierarchy structure."""

    def test_menu_hierarchy(self):
        """Test menu hierarchy structure."""
        assert AccountManagement.name == _("Django Account Center")
        child_names = [child.name for child in AccountManagement.children]
        assert "Account Center Menu" in child_names
        assert "AuthenticatedUserMenu" in child_names

    def test_menus_are_independent(self):
        """Test that menu instances are properly separated."""
        # AccountCenterMenu and AuthenticatedUserMenu should be different objects
        assert AccountCenterMenu is not AuthenticatedUserMenu
        assert AccountCenterMenu.name != AuthenticatedUserMenu.name
