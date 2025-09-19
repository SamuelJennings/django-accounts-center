"""
Django Account Center Template Tags

Custom template tags for the django-accounts-center package.
"""

from crispy_forms.helper import FormHelper
from crispy_forms.templatetags.crispy_forms_tags import CrispyFormNode
from django import template
from django.conf import settings

register = template.Library()


@register.simple_tag(takes_context=True)
def render_form(context, form, **kwargs):
    """
    Prepares a form for rendering by setting the method and action attributes.

    This tag is useful for forms that need to be submitted via POST or GET.
    It automatically sets up a FormHelper if one doesn't exist and configures
    the form ID and attributes.

    Args:
        context: Template context
        form: Django form instance
        **kwargs: Additional attributes to set on the form helper

    Returns:
        Rendered form HTML
    """
    # Ensure form has a helper
    if not hasattr(form, "helper") or form.helper is None:
        form.helper = FormHelper()

    # Set form ID if not already set
    if not form.helper.form_id:
        form.helper.form_id = form.__class__.__name__.lower()

    form.helper.form_tag = False

    # Apply additional attributes
    form.helper.attrs = kwargs

    # Update context
    context["form"] = form
    context["helper"] = form.helper

    # Render using crispy forms
    node = CrispyFormNode("form", "helper")
    return node.render(context)


@register.simple_tag
def get_setting(name, default=None):
    """
    Returns the value of a Django setting.

    Args:
        name (str): Name of the setting to retrieve
        default: Default value to return if setting is not found

    Returns:
        Setting value or default if not found
    """
    return getattr(settings, name, default)
