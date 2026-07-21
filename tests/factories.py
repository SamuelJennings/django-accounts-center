"""
Factory Boy factories for django-accounts-center testing.

This module provides factory classes for creating test data objects
used throughout the test suite.
"""

import factory
from allauth.account.models import EmailAddress
from allauth.socialaccount.models import SocialAccount, SocialApp
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


class EmailAddressFactory(factory.django.DjangoModelFactory):
    """Factory for creating EmailAddress instances."""

    class Meta:
        model = EmailAddress

    user = factory.SubFactory(UserFactory)
    email = factory.LazyAttribute(lambda obj: obj.user.email)
    verified = True
    primary = True


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


class SocialAccountFactory(factory.django.DjangoModelFactory):
    """Factory for creating SocialAccount instances."""

    class Meta:
        model = SocialAccount

    user = factory.SubFactory(UserFactory)
    provider = "google"
    uid = factory.Faker("uuid4")
    extra_data = factory.LazyFunction(dict)
