"""Template tags for django-accounts-center."""

from django import template

register = template.Library()


@register.simple_tag(takes_context=True)
def account_section(context):
    """Resolve the active Account Center section for breadcrumb rendering.

    Usage: ``{% account_section as section %}`` — see
    :func:`dac.menus.get_active_section` for the return shape.
    """
    from dac.menus import get_active_section

    request = context.get("request")
    if request is None:
        return None
    return get_active_section(request)
