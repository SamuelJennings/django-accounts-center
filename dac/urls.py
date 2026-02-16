from django.conf import settings
from django.urls import include, path

from . import views

urlpatterns = [
    path("", views.Home.as_view(), name="account-center"),
    path("account/", include("allauth.urls")),
]

if "dac.addons.allauth" in settings.INSTALLED_APPS:
    # urlpatterns.append(path("account/", include("dac.addons.allauth.urls")))
    urlpatterns.append(path("", include("allauth.urls")))
if "dac.addons.stripe" in settings.INSTALLED_APPS:
    urlpatterns.append(path("", include("dac.addons.stripe.urls")))

if "dac.addons.actstream" in settings.INSTALLED_APPS:
    urlpatterns.append(path("", include("dac.addons.actstream.urls")))
