from django.utils.translation import gettext_lazy as _

from dac.menus import AuthenticatedUserDropdown, DropdownMenuItem, MainMenu, MainMenuGroup, MainMenuItem

AllAuthMenu = MainMenuGroup(
    _("Account"),
    extra_context={"label": _("Account")},
    children=[
        MainMenuItem(_("Email"), view_name="account_email", extra_context={"icon": "email"}),
        MainMenuItem(_("Connected Accounts"), view_name="socialaccount_connections", extra_context={"icon": "link"}),
        MainMenuItem(_("Sessions"), view_name="usersessions_list", extra_context={"icon": "sessions"}),
        MainMenuItem(_("Password"), view_name="account_change_password", extra_context={"icon": "password"}),
        MainMenuItem(_("MFA"), view_name="mfa_index", extra_context={"icon": "mfa"}),
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
