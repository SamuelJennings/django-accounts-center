"""Views for django-accounts-center.

``AccountCenterView`` is the overview/landing page of the Account Center.
Integration sub-apps contribute cards to it through two optional attributes
on their ``AppConfig``:

- ``dac_overview_template`` — template included inside the overview grid
- ``dac_overview_context(request)`` — extra context for those cards

See :class:`dac.allauth.apps.DacAllauthConfig` for a working example.
"""

from django.apps import apps as django_apps
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.translation import gettext_lazy as _
from mvp.views import MVPTemplateView


class AccountCenterView(LoginRequiredMixin, MVPTemplateView):
    """Account Center overview page."""

    page_title = _("Account Center")
    template_name = "dac/account_center.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        overview_templates = []
        for appconfig in django_apps.get_app_configs():
            template_name = getattr(appconfig, "dac_overview_template", None)
            if not template_name:
                continue
            get_extra_context = getattr(appconfig, "dac_overview_context", None)
            if get_extra_context:
                context.update(get_extra_context(self.request))
            overview_templates.append(template_name)
        context["dac_overview_templates"] = overview_templates
        return context


# Backwards-compatible alias (pre-0.7 name).
AccountCenter = AccountCenterView
