from allauth.account.views import email, password_change
from allauth.mfa.base.views import index
from allauth.socialaccount.views import connections
from allauth.usersessions.views import list_usersessions
from django.urls import path

urlpatterns = [
    path("email/", email, name="account_email"),
    path("password/change/", password_change, name="account_change_password"),
    path("connected-accounts/", connections, name="socialaccount_connections"),
    path("sessions/", list_usersessions, name="usersessions_list"),
    path("mfa/", index, name="mfa_index"),
]
