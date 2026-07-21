from django.apps import AppConfig


class DacAllauthConfig(AppConfig):
    """django-allauth integration for the Account Center.

    Opt in by adding ``"dac.allauth"`` to ``INSTALLED_APPS`` **before**
    ``"allauth"`` (app template dirs are searched in INSTALLED_APPS order, so
    dac's allauth layout/element overrides must win).

    Contributes to the Account Center overview page via the ``dac_overview_*``
    hooks that :class:`dac.views.AccountCenterView` collects from every
    installed app.
    """

    name = "dac.allauth"
    label = "dac_allauth"
    verbose_name = "Account Center — allauth"

    dac_overview_template = "dac/allauth/overview_cards.html"

    def dac_overview_context(self, request):
        from allauth.account.models import EmailAddress
        from mvp.utils import app_is_installed

        user = request.user
        emailaddresses = EmailAddress.objects.filter(user=user).order_by(
            "-primary", "-verified", "email"
        )
        context = {
            "emailaddresses": emailaddresses,
            "unverified_email_count": sum(1 for e in emailaddresses if not e.verified),
            "has_usable_password": user.has_usable_password(),
            "socialaccount_enabled": app_is_installed("allauth.socialaccount"),
            "mfa_enabled": app_is_installed("allauth.mfa"),
            "usersessions_enabled": app_is_installed("allauth.usersessions"),
        }

        if context["socialaccount_enabled"]:
            context["socialaccounts"] = user.socialaccount_set.all()

        if context["mfa_enabled"]:
            from allauth.mfa.models import Authenticator

            authenticators = Authenticator.objects.filter(user=user)
            context["authenticators"] = authenticators
            context["mfa_active"] = any(
                a.type in (Authenticator.Type.TOTP, Authenticator.Type.WEBAUTHN)
                for a in authenticators
            )

        if context["usersessions_enabled"]:
            from allauth.usersessions.models import UserSession

            context["session_count"] = UserSession.objects.filter(user=user).count()

        return context
