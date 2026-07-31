from django.urls import path

from . import views

urlpatterns = [
    # The 'gated' entry's own page, plus a sub-page beneath it. Both stay
    # reachable for a person the entry is hidden from — hiding is presentation
    # only — which is what the breadcrumb test needs to exercise.
    path("gated/", views.SettingsView.as_view(), name="testapp_gated"),
    path("gated/sub/", views.SettingsView.as_view(), name="testapp_gated_sub"),
    path("settings/", views.SettingsView.as_view(), name="testapp_settings"),
    # Sub-page of the 'sectioned' entry — its name starts with the entry's
    # declared url_names prefix, so breadcrumb resolution matches it.
    path("settings/sub/", views.SettingsView.as_view(), name="testapp_settings_sub"),
]
