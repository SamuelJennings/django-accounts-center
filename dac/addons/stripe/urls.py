from django.urls import include, path

from .views import DRFStripeView, StripePricingView, stripe_portal_redirect

urlpatterns = [
    path("pricing/", StripePricingView.as_view(), name="stripe_pricing"),
    path("subscription/manage/", DRFStripeView.as_view(), name="drf_stripe"),
    path("stripe-portal-redirect/", stripe_portal_redirect, name="stripe_portal_redirect"),
    path("stripe/", include("drf_stripe.urls")),
]
