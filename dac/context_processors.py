from django.utils.translation import gettext_lazy as _

layout = {}

sections = {
    # holds the account center menu
    "sidebar_primary": {
        "is": "dac.sidebar",
        "breakpoint": "md",
        "class": "w-25 border-end",
        "header": {
            "title": _("Account Center"),
        },
    },
    # adds padding to the right on larger screens
    "sidebar_secondary": {
        "is": "sections.sidebar.empty",
        "breakpoint": "md",
        "width": "200px",
    },
}

# This is a mapping of url paths to titles and icons for the account management section.
titles = {
    "email/": {
        "title": _("Email"),
    },
    "password/change/": {
        "title": _("Change Password"),
    },
    "3rdparty/": {
        "title": _("Third Party Accounts"),
    },
    "sessions/": {
        "title": _("Sessions"),
    },
    "2fa/": {
        "title": _("Multi-Factor Authentication"),
    },
}


def account_context(request):
    if not request.path.startswith("/account/"):
        return {}
    # if not request.user.is_authenticated:
    # raise LoginRe
    # get page title from the path
    path = request.path.split("account/")[-1]  # Skip the first two parts ("account" and the empty string)
    if path in titles:
        page_title = titles[path]["title"]
    else:
        page_title = None
    return {
        "sections": sections,
        "layout": layout,
        "page_title": page_title,
    }
