# from actstream import models
from allauth.account import app_settings as allauth_settings
from allauth.utils import get_form_class
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

User = get_user_model()


class EntranceView(TemplateView):
    template_name = "dac/entrance.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        LoginFormClass = get_form_class(allauth_settings.FORMS, "login")
        SignupFormClass = get_form_class(allauth_settings.FORMS, "signup")

        context["login_form"] = LoginFormClass(self.request.POST or None, prefix="login")
        context["signup_form"] = SignupFormClass(self.request.POST or None, prefix="signup")

        return context


class LoginTemplateView(LoginRequiredMixin, TemplateView):
    """
    This view is used to render the login template.
    """

    template_name = "dac/login.html"


class Home(LoginRequiredMixin, TemplateView):
    template_name = "dac/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["stripe_pricing_table_id"] = getattr(settings, "STRIPE_PRICING_TABLE_ID", None)
        context["stripe_public_key"] = getattr(settings, "STRIPE_PUBLIC_KEY", None)
        return context


class AccountFollowers(LoginRequiredMixin, TemplateView):
    template_name = "dac/followers.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["followers"] = models.followers(self.request.user, flag="")
        return context


class AccountFollowing(LoginRequiredMixin, TemplateView):
    template_name = "dac/following.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["following"] = models.following(self.request.user, flag="")
        return context
