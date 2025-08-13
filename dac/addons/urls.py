from django.conf import settings
from django.urls import include, path

urlpatterns = []

if "dac.addons.allauth" in settings.INSTALLED_APPS:
    urlpatterns.append(path("", include("allauth.urls")))
