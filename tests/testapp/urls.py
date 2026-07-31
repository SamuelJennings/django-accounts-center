from django.urls import path

from . import views

urlpatterns = [
    path("settings/", views.SettingsView.as_view(), name="testapp_settings"),
    # Sub-page of the 'sectioned' entry — its name starts with the entry's
    # declared url_names prefix, so breadcrumb resolution matches it.
    path("settings/sub/", views.SettingsView.as_view(), name="testapp_settings_sub"),
]
