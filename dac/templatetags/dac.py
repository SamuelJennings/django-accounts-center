from crispy_forms.helper import FormHelper
from crispy_forms.templatetags.crispy_forms_tags import CrispyFormNode
from django import template
from django.conf import settings

register = template.Library()


@register.simple_tag(takes_context=True)
def render_form(context, form, **kwargs):
    """
    Prepares a form for rendering by setting the method and action attributes.
    This is useful for forms that need to be submitted via POST or GET.
    """
    # method = kwargs.get("method", "post")
    # action = kwargs.get("action", "")

    # form.method = method
    # form.action = action
    if not hasattr(form, "helper") or form.helper is None:
        form.helper = FormHelper()

    if not form.helper.form_id:
        form.helper.form_id = form.__class__.__name__.lower()

    form.helper.attrs = kwargs

    # for key, value in kwargs.items():
    # if hasattr(form.helper, key):
    # setattr(form.helper, key, value)

    context["form"] = form
    context["helper"] = form.helper

    node = CrispyFormNode("form", "helper")
    return node.render(context)


@register.simple_tag
def get_setting(name):
    """
    Returns the value of a setting. If the setting is not found, returns None.
    """
    try:
        return getattr(settings, name)
    except AttributeError:
        return None
