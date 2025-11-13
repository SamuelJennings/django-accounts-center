from django.utils.translation import gettext_lazy as _
from flex_menu import MenuItem
from flex_menu.checks import user_is_authenticated

from dac.menus import AccountCenterMenu, AuthenticatedUserMenu


def user_has_social_accounts(request, **kwargs):
    """Check if user has social account connections available."""
    return request.user.is_authenticated and hasattr(request.user, "socialaccount_set")


# AllAuth account management menu group
AllAuthMenuGroup = MenuItem(
    name=_("Account"),
    extra_context={
        "icon": "account_circle",
        "description": _("Manage account settings and security"),
    },
    check=user_is_authenticated,
    children=[
        MenuItem(
            name=_("Email"),
            view_name="account_email",
            extra_context={
                "icon": "email",
                "description": _("Manage email addresses"),
            },
        ),
        MenuItem(
            name=_("Connected Accounts"),
            view_name="socialaccount_connections",
            extra_context={
                "icon": "link",
                "description": _("Manage social media connections"),
            },
            check=user_has_social_accounts,
        ),
        MenuItem(
            name=_("Sessions"),
            view_name="usersessions_list",
            extra_context={
                "icon": "sessions",
                "description": _("View active login sessions"),
            },
        ),
        MenuItem(
            name=_("Password"),
            view_name="account_change_password",
            extra_context={
                "icon": "password",
                "description": _("Change your password"),
            },
        ),
        MenuItem(
            name=_("MFA"),
            view_name="mfa_index",
            extra_context={
                "icon": "mfa",
                "description": _("Multi-factor authentication settings"),
            },
        ),
    ],
)

# Add AllAuth menu group to main menu
AccountCenterMenu.append(AllAuthMenuGroup)

# Add logout item to user dropdown
AuthenticatedUserMenu.append(
    MenuItem(
        name=_("Logout"),
        view_name="account_logout",
        extra_context={
            "icon": "logout",
            "description": _("Sign out of your account"),
            "css_class": "text-danger",
        },
        check=user_is_authenticated,
    ),
)
