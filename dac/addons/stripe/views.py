from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_POST
from django.views.generic import TemplateView
from drf_stripe.models import StripeUser
from drf_stripe.stripe_api.api import stripe

User = get_user_model()


class StripePricingView(LoginRequiredMixin, TemplateView):
    template_name = "dac/stripe/pricing.html"
    extra_context = {
        "stripe_pricing_table_id": getattr(settings, "STRIPE_PRICING_TABLE_ID", None),
        "stripe_public_key": getattr(settings, "STRIPE_PUBLIC_KEY", None),
    }


class DRFStripeView(LoginRequiredMixin, TemplateView):
    template_name = "dac/stripe/drf_stripe.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["stripe_user"] = StripeUser.objects.filter(user=self.request.user).first()
        context["stripe_pricing_table_id"] = getattr(settings, "STRIPE_PRICING_TABLE_ID", None)
        context["stripe_public_key"] = getattr(settings, "STRIPE_PUBLIC_KEY", None)
        return context


@login_required
@require_POST
def stripe_portal_redirect(request):
    """
    Redirect to Stripe customer portal
    """
    stripe_user = get_object_or_404(StripeUser, user=request.user)
    session = stripe.billing_portal.Session.create(
        customer=stripe_user.customer_id, return_url=request.META["HTTP_REFERER"]
    )

    return redirect(session.url)
