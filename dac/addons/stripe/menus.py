from django.utils.translation import gettext_lazy as _

from dac.menus import MainMenu, MainMenuGroup, MainMenuItem

SubscriptionMenu = MainMenuGroup(
    _("Subscription"),
    children=[
        # MainMenuItem(_("Pricing"), view_name="stripe_pricing", icon="password_change"),
        MainMenuItem(_("Manage"), view_name="drf_stripe", icon="email"),
    ],
)

MainMenu.append(SubscriptionMenu)
