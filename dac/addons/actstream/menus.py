from cotton_bs5.menus import SidebarGroup, SidebarItem
from django.utils.translation import gettext_lazy as _

is_staff_user = lambda request: request.user.is_staff
ActivityStreamMenu = SidebarGroup(
    _("Activity"),
    children=[
        SidebarItem(_("Recent Activity"), view_name="home", icon="activity"),
        SidebarItem(_("Following"), view_name="account-following", icon="star-solid"),
        SidebarItem(_("Followed by"), view_name="account-followers", icon="identifier"),
    ],
)
