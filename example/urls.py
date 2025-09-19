from debug_toolbar.toolbar import debug_toolbar_urls
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.urls import include, path, reverse_lazy
from django.views.generic.base import RedirectView
from django.views.generic.edit import UpdateView

urlpatterns = [
    path("", RedirectView.as_view(url=reverse_lazy("account_login")), name="example-home"),
    path("account-center/", include("dac.urls")),
    path(
        "profile/<pk>/",
        UpdateView.as_view(model=get_user_model(), fields=["username", "first_name", "last_name"]),
        name="profile-edit",
    ),
    path("admin/", admin.site.urls),
    *debug_toolbar_urls(),
]
