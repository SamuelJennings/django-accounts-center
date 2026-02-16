from django.urls import include, path
from mvp.utils import app_is_installed

ALLAUTH = app_is_installed("allauth")

urlpatterns = []
if ALLAUTH:
    urlpatterns.append(path("", include("allauth.urls")))
