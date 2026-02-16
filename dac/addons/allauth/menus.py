from django.utils.translation import gettext_lazy as _
from flex_menu import MenuItem
from flex_menu.checks import user_is_authenticated
from mvp.menus import MenuGroup
from mvp.utils import app_is_installed

from dac.menus import AccountCenterMenu, AuthenticatedUserMenu

MFA = app_is_installed("allauth.mfa")
USERSESSIONS = app_is_installed("allauth.usersessions")
ALLAUTH_ACCOUNT = app_is_installed("allauth.account")
ALLAUTH_SOCIALACCOUNT = app_is_installed("allauth.socialaccount")


def user_has_social_accounts(request, **kwargs):
    """Check if user has social account connections available."""
    return request.user.is_authenticated and hasattr(request.user, "socialaccount_set")


# AllAuth account management menu group
AllAuthMenuGroup = MenuGroup(
    name=_("Account"),
    extra_context={
        "icon": "account_circle",
        "description": _("Manage account settings and security"),
    },
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
            name=_("Password"),
            view_name="account_change_password",
            extra_context={
                "icon": "password",
                "description": _("Change your password"),
            },
        ),
    ],
)

if ALLAUTH_SOCIALACCOUNT:
    AllAuthMenuGroup.append(
        MenuItem(
            name=_("Social Accounts"),
            view_name="socialaccount_connections",
            extra_context={
                "icon": "link",
            },
        )
    )

if USERSESSIONS:
    AllAuthMenuGroup.append(
        MenuItem(
            name=_("Sessions"),
            view_name="usersessions_list",
            extra_context={
                "icon": "sessions",
            },
        )
    )

if MFA:
    AllAuthMenuGroup.append(
        MenuItem(
            name=_("MFA"),
            view_name="mfa_index",
            extra_context={
                "icon": "mfa",
            },
        )
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
