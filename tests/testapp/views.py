from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView


class SettingsView(LoginRequiredMixin, TemplateView):
    """The test integration's one management page.

    Renders through ``dac/base.html`` — the shared management page every
    integration's page is meant to reach (FR-008) — carrying nothing of its
    own but ``{% block content %}``.
    """

    template_name = "testapp/settings.html"
