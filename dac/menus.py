"""Menu definitions for django-accounts-center.

``AccountCenterMenu`` is the internal sub menu shown on every Account Center
page (rendered by ``dac/base.html``). The core package registers only the
Overview item; integration sub-apps (``dac.allauth``, future ``dac.stripe``,
…) append their own labelled ``MenuGroup`` from their ``menus.py``, so the
menu grows with the integrations the host project installs.

Group items may declare ``url_names`` in ``extra_context`` — a tuple of
URL-name prefixes identifying their sub-pages — which breadcrumbs use to
resolve the active section on pages below a section root.
"""

from django.urls import NoReverseMatch, reverse
from django.utils.translation import gettext_lazy as _
from flex_menu import Menu, MenuItem

AccountCenterMenu = Menu(
    name="AccountCenterMenu",
    children=[
        MenuItem(
            name="overview",
            view_name="account-center",
            extra_context={"label": _("Account Center"), "icon": "overview"},
        ),
    ],
)


def _iter_leaves(node):
    """Yield the leaf items of a menu tree (groups descend)."""
    children = list(node.children or [])
    if children:
        for child in children:
            yield from _iter_leaves(child)
    else:
        yield node


def get_active_section(request):
    """Return the AccountCenterMenu section for ``request`` as a dict.

    Returns ``{"label": …, "url": …, "is_current": bool}`` — ``is_current``
    means the request is the section page itself (render the crumb as plain
    text), otherwise the request is a sub-page of the section (render the
    crumb as a link). Returns ``None`` on the overview page or when no
    section matches.

    Resolved from ``AccountCenterMenu``'s *declared* children, matched on URL
    name, rather than the per-request processed tree: which section a URL
    belongs to has nothing to do with whether the current person can see its
    menu entry, so this must not depend on any entry's visibility check
    (FR-006a). See specs/013-account-center-menu/research.md R2.
    """
    resolver_match = getattr(request, "resolver_match", None)
    if resolver_match is None:
        return None

    leaves = [item for item in _iter_leaves(AccountCenterMenu) if item.view_name and item.name != "overview"]

    # Exact match first, across every leaf, before any prefix match is
    # considered: a section root's own name (e.g. "mfa_index") must never
    # lose to another entry's url_names prefix (e.g. "mfa_").
    for item in leaves:
        current_name = resolver_match.view_name if ":" in item.view_name else resolver_match.url_name
        if current_name == item.view_name:
            return {
                "label": item.extra_context.get("label", item.name),
                "url": None,
                "is_current": True,
            }

    url_name = resolver_match.url_name
    if url_name:
        for item in leaves:
            for prefix in item.extra_context.get("url_names", ()):
                if url_name.startswith(prefix):
                    try:
                        url = reverse(item.view_name)
                    except NoReverseMatch:
                        # An unreachable entry degrades to no breadcrumb
                        # rather than a 500.
                        return None
                    return {
                        "label": item.extra_context.get("label", item.name),
                        "url": url,
                        "is_current": False,
                    }
    return None
