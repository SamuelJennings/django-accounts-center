"""
Factory Boy factories for django-accounts-center testing.

This module provides factory classes for creating test data objects
used throughout the test suite.
"""

import factory
from allauth.account.models import EmailAddress, EmailConfirmation
from allauth.mfa.models import Authenticator
from allauth.socialaccount.models import SocialAccount, SocialApp, SocialToken
from allauth.usersessions.models import UserSession
from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site

User = get_user_model()


class UserFactory(factory.django.DjangoModelFactory):
    """Factory for creating User instances."""

    class Meta:
        model = User

    username = factory.Sequence(lambda n: f"user{n}")
    email = factory.LazyAttribute(lambda obj: f"{obj.username}@example.com")
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    is_active = True
    is_staff = False
    is_superuser = False

    @factory.post_generation
    def password(self, create, extracted, **kwargs):
        """Set password for the user."""
        if extracted:
            self.set_password(extracted)
        else:
            self.set_password("defaultpass123")
        if create:
            self.save()


class SuperUserFactory(UserFactory):
    """Factory for creating superuser instances."""

    username = factory.Sequence(lambda n: f"admin{n}")
    email = factory.LazyAttribute(lambda obj: f"{obj.username}@example.com")
    is_staff = True
    is_superuser = True


class StaffUserFactory(UserFactory):
    """Factory for creating staff user instances."""

    username = factory.Sequence(lambda n: f"staff{n}")
    email = factory.LazyAttribute(lambda obj: f"{obj.username}@example.com")
    is_staff = True


class EmailAddressFactory(factory.django.DjangoModelFactory):
    """Factory for creating EmailAddress instances."""

    class Meta:
        model = EmailAddress

    user = factory.SubFactory(UserFactory)
    email = factory.LazyAttribute(lambda obj: obj.user.email)
    verified = True
    primary = True


class UnverifiedEmailAddressFactory(EmailAddressFactory):
    """Factory for creating unverified EmailAddress instances."""

    verified = False
    primary = False


class EmailConfirmationFactory(factory.django.DjangoModelFactory):
    """Factory for creating EmailConfirmation instances."""

    class Meta:
        model = EmailConfirmation

    email_address = factory.SubFactory(UnverifiedEmailAddressFactory)
    key = factory.Faker("uuid4")


class SiteFactory(factory.django.DjangoModelFactory):
    """Factory for creating Site instances."""

    class Meta:
        model = Site

    domain = factory.Faker("domain_name")
    name = factory.Faker("company")


class SocialAppFactory(factory.django.DjangoModelFactory):
    """Factory for creating SocialApp instances."""

    class Meta:
        model = SocialApp

    provider = "google"
    name = factory.Faker("company")
    client_id = factory.Faker("uuid4")
    secret = factory.Faker("password")

    @factory.post_generation
    def sites(self, create, extracted, **kwargs):
        """Add sites to the social app."""
        if not create:
            return

        if extracted:
            for site in extracted:
                self.sites.add(site)
        else:
            # Add default site
            default_site, _ = Site.objects.get_or_create(
                id=1, defaults={"domain": "example.com", "name": "example.com"}
            )
            self.sites.add(default_site)


class GoogleSocialAppFactory(SocialAppFactory):
    """Factory for creating Google SocialApp instances."""

    provider = "google"
    name = "Google"


class GitHubSocialAppFactory(SocialAppFactory):
    """Factory for creating GitHub SocialApp instances."""

    provider = "github"
    name = "GitHub"


class SocialAccountFactory(factory.django.DjangoModelFactory):
    """Factory for creating SocialAccount instances."""

    class Meta:
        model = SocialAccount

    user = factory.SubFactory(UserFactory)
    provider = "google"
    uid = factory.Faker("uuid4")
    extra_data = factory.LazyFunction(dict)


class GoogleSocialAccountFactory(SocialAccountFactory):
    """Factory for creating Google SocialAccount instances."""

    provider = "google"
    extra_data = factory.LazyFunction(
        lambda: {"email": "user@gmail.com", "name": "Test User", "picture": "https://example.com/avatar.jpg"}
    )


class GitHubSocialAccountFactory(SocialAccountFactory):
    """Factory for creating GitHub SocialAccount instances."""

    provider = "github"
    extra_data = factory.LazyFunction(
        lambda: {
            "login": "testuser",
            "email": "user@example.com",
            "name": "Test User",
            "avatar_url": "https://example.com/avatar.jpg",
        }
    )


class SocialTokenFactory(factory.django.DjangoModelFactory):
    """Factory for creating SocialToken instances."""

    class Meta:
        model = SocialToken

    app = factory.SubFactory(SocialAppFactory)
    account = factory.SubFactory(SocialAccountFactory)
    token = factory.Faker("uuid4")
    token_secret = factory.Faker("password")


class AuthenticatorFactory(factory.django.DjangoModelFactory):
    """Factory for creating MFA Authenticator instances."""

    class Meta:
        model = Authenticator

    user = factory.SubFactory(UserFactory)
    type = Authenticator.Type.TOTP
    data = factory.LazyFunction(dict)


class TOTPAuthenticatorFactory(AuthenticatorFactory):
    """Factory for creating TOTP Authenticator instances."""

    type = Authenticator.Type.TOTP
    data = factory.LazyFunction(lambda: {"secret": "JBSWY3DPEHPK3PXP"})


class WebAuthnAuthenticatorFactory(AuthenticatorFactory):
    """Factory for creating WebAuthn Authenticator instances."""

    type = Authenticator.Type.WEBAUTHN
    data = factory.LazyFunction(lambda: {"credential_id": "test_credential_id", "public_key": "test_public_key"})


class UserSessionFactory(factory.django.DjangoModelFactory):
    """Factory for creating UserSession instances."""

    class Meta:
        model = UserSession

    user = factory.SubFactory(UserFactory)
    ip = factory.Faker("ipv4")
    user_agent = factory.Faker("user_agent")


# Template testing specific factories


class UserWithEmailFactory(UserFactory):
    """Factory for user with verified email address."""

    @factory.post_generation
    def create_email(self, create, extracted, **kwargs):
        """Create verified email address for user."""
        if create:
            EmailAddressFactory(user=self, email=self.email, verified=True, primary=True)


class UserWithUnverifiedEmailFactory(UserFactory):
    """Factory for user with unverified email address."""

    @factory.post_generation
    def create_email(self, create, extracted, **kwargs):
        """Create unverified email address for user."""
        if create:
            UnverifiedEmailAddressFactory(user=self, email=self.email)


class UserWithSocialAccountFactory(UserFactory):
    """Factory for user with social account."""

    @factory.post_generation
    def create_social_account(self, create, extracted, **kwargs):
        """Create social account for user."""
        if create:
            provider = extracted or "google"
            if provider == "google":
                GoogleSocialAccountFactory(user=self)
            elif provider == "github":
                GitHubSocialAccountFactory(user=self)
            else:
                SocialAccountFactory(user=self, provider=provider)


class UserWithMFAFactory(UserFactory):
    """Factory for user with MFA enabled."""

    @factory.post_generation
    def create_mfa(self, create, extracted, **kwargs):
        """Create MFA authenticator for user."""
        if create:
            mfa_type = extracted or Authenticator.Type.TOTP
            if mfa_type == Authenticator.Type.TOTP:
                TOTPAuthenticatorFactory(user=self)
            elif mfa_type == Authenticator.Type.WEBAUTHN:
                WebAuthnAuthenticatorFactory(user=self)
            else:
                AuthenticatorFactory(user=self, type=mfa_type)


class CompleteUserFactory(UserFactory):
    """Factory for user with all features enabled."""

    @factory.post_generation
    def setup_complete_user(self, create, extracted, **kwargs):
        """Set up user with email, social account, and MFA."""
        if create:
            # Create verified email
            EmailAddressFactory(user=self, email=self.email, verified=True, primary=True)

            # Create social account
            GoogleSocialAccountFactory(user=self)

            # Create MFA
            TOTPAuthenticatorFactory(user=self)

            # Create user session
            UserSessionFactory(user=self)


# Test scenario factories


class LoginScenarioFactory:
    """Factory for creating login test scenarios."""

    @staticmethod
    def create_socialaccount_only_scenario():
        """Create scenario for SOCIALACCOUNT_ONLY testing."""
        # Create social apps
        google_app = GoogleSocialAppFactory()
        github_app = GitHubSocialAppFactory()

        # Create users with social accounts
        google_user = UserWithSocialAccountFactory(create_social_account="google")
        github_user = UserWithSocialAccountFactory(create_social_account="github")

        return {"apps": [google_app, github_app], "users": [google_user, github_user]}

    @staticmethod
    def create_mfa_scenario():
        """Create scenario for MFA testing."""
        # Create users with different MFA setups
        totp_user = UserWithMFAFactory(create_mfa=Authenticator.Type.TOTP)
        webauthn_user = UserWithMFAFactory(create_mfa=Authenticator.Type.WEBAUTHN)
        no_mfa_user = UserFactory()

        return {"totp_user": totp_user, "webauthn_user": webauthn_user, "no_mfa_user": no_mfa_user}

    @staticmethod
    def create_email_verification_scenario():
        """Create scenario for email verification testing."""
        # Create users with different email states
        verified_user = UserWithEmailFactory()
        unverified_user = UserWithUnverifiedEmailFactory()

        # Create email confirmation for unverified user
        email_address = unverified_user.emailaddress_set.first()
        if email_address:
            confirmation = EmailConfirmationFactory(email_address=email_address)
        else:
            confirmation = None

        return {"verified_user": verified_user, "unverified_user": unverified_user, "confirmation": confirmation}


class TemplateTestDataFactory:
    """Factory for creating template-specific test data."""

    @staticmethod
    def create_form_test_data():
        """Create data for form testing."""
        return {
            "valid_login_data": {"login": "test@example.com", "password": "validpass123"},
            "invalid_login_data": {"login": "invalid@email.com", "password": "wrongpass"},
            "valid_signup_data": {"email": "newuser@example.com", "password1": "newpass123", "password2": "newpass123"},
            "invalid_signup_data": {"email": "invalid-email", "password1": "short", "password2": "different"},
        }

    @staticmethod
    def create_component_test_data():
        """Create data for component testing."""
        return {
            "entrance_layout_props": {"title": "Test Title", "subtitle": "Test Subtitle", "type": "login"},
            "standard_layout_props": {"title": "Account Management"},
            "alert_props": {"variant": "success", "message": "Test message", "dismissable": True},
            "button_props": {"text": "Test Button", "type": "submit", "variant": "primary"},
        }
