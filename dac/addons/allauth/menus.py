from django.utils.translation import gettext_lazy as _

from dac.menus import AuthenticatedUserDropdown, DropdownMenuItem, MainMenu, MainMenuGroup, MainMenuItem

AllAuthMenu = MainMenuGroup(
    _("Account"),
    children=[
        MainMenuItem(_("Email"), view_name="account_email", icon="email"),
        MainMenuItem(_("Connected Accounts"), view_name="socialaccount_connections", icon="link"),
        MainMenuItem(_("Sessions"), view_name="usersessions_list", icon="sessions"),
        MainMenuItem(_("Password"), view_name="account_change_password", icon="password_change"),
        MainMenuItem(_("MFA"), view_name="mfa_index", icon="mfa"),
    ],
)

MainMenu.append(AllAuthMenu)

AuthenticatedUserDropdown.append(
    DropdownMenuItem(
        root_template="dac/menus/allauth_logout.html",
        name=_("Logout"),
        view_name="account_logout",
        icon="delete",
        css_class="text-danger",
    ),
)
