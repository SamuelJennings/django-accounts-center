"""
Django Account Center Views

This module provides views for managing user accounts, including authentication,
profile management, and account settings.
"""

import logging

from allauth.account import app_settings as allauth_settings
from allauth.account.forms import LoginForm, SignupForm
from allauth.utils import get_form_class
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

logger = logging.getLogger(__name__)
User = get_user_model()


class EntranceView(TemplateView):
    """View for user registration and login entrance page."""

    template_name = "dac/entrance.html"

    def get_context_data(self, **kwargs):
        """Add login and signup forms to context."""
        context = super().get_context_data(**kwargs)

        try:
            LoginFormClass = get_form_class(allauth_settings.FORMS, "login", LoginForm)
            SignupFormClass = get_form_class(allauth_settings.FORMS, "signup", SignupForm)

            context["login_form"] = LoginFormClass(self.request.POST or None, prefix="login")
            context["signup_form"] = SignupFormClass(self.request.POST or None, prefix="signup")
        except Exception:
            logger.exception("Error loading forms")
            # Fallback to default forms
            context["login_form"] = LoginForm(self.request.POST or None, prefix="login")
            context["signup_form"] = SignupForm(self.request.POST or None, prefix="signup")

        return context


class LoginTemplateView(LoginRequiredMixin, TemplateView):
    """View for rendering the login template after authentication."""

    template_name = "dac/login.html"


class Home(LoginRequiredMixin, TemplateView):
    """Main account center home page."""

    template_name = "dac/home.html"

    def get_context_data(self, **kwargs):
        """Add Stripe configuration to context if available."""
        context = super().get_context_data(**kwargs)
        # context["stripe_pricing_table_id"] = getattr(settings, "STRIPE_PRICING_TABLE_ID", None)
        # context["stripe_public_key"] = getattr(settings, "STRIPE_PUBLIC_KEY", None)
        return context
