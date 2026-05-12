"""
Django Account Center Views

This module provides views for managing user accounts, including authentication,
profile management, and account settings.
"""

from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.translation import gettext_lazy as _
from mvp.views import MVPTemplateView


class AccountCenter(LoginRequiredMixin, MVPTemplateView):
    """Main account center home page."""

    page_title = _("Account Center")
    template_name = "dac/account_center.html"
