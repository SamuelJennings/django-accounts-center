from django.urls import include, path
from mvp.utils import app_is_installed

from . import views

urlpatterns = [
    path("", views.AccountCenterView.as_view(), name="account-center"),
]

if app_is_installed("dac.allauth"):
    urlpatterns.append(path("", include("dac.allauth.urls")))
