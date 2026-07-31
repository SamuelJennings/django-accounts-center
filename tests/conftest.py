"""
Pytest configuration and fixtures for django-accounts-center tests.
"""

import pytest


@pytest.fixture
def user(django_user_model):
    """Create a test user."""
    return django_user_model.objects.create_user(username="testuser", email="test@example.com", password="testpass123")


@pytest.fixture
def authenticated_client(client, user):
    """Create an authenticated test client."""
    client.force_login(user)
    return client


@pytest.fixture
def gated_person(django_user_model):
    """A signed-in person the testapp's 'gated' menu entry applies to."""
    from django.contrib.auth.models import Group

    from tests.testapp.menus import GATED_GROUP_NAME

    person = django_user_model.objects.create_user(
        username="gated_person", email="gated_person@example.com", password="testpass123"
    )
    group, _ = Group.objects.get_or_create(name=GATED_GROUP_NAME)
    person.groups.add(group)
    return person


@pytest.fixture
def gated_client(gated_person):
    """An authenticated client for the person the 'gated' entry applies to.

    A fresh ``Client()`` rather than the shared ``client`` fixture: a test
    comparing two people's menus needs ``gated_client`` and ``ungated_client``
    signed in at once, and both would otherwise resolve to the same
    pytest-django ``client`` instance, so the second ``force_login`` call
    would silently sign out the first.
    """
    from django.test import Client

    test_client = Client()
    test_client.force_login(gated_person)
    return test_client


@pytest.fixture
def ungated_person(django_user_model):
    """A signed-in person the testapp's 'gated' menu entry does not apply to."""
    return django_user_model.objects.create_user(
        username="ungated_person", email="ungated_person@example.com", password="testpass123"
    )


@pytest.fixture
def ungated_client(ungated_person):
    """An authenticated client for the person the 'gated' entry does not apply to.

    A fresh ``Client()`` — see ``gated_client`` for why the shared ``client``
    fixture does not work when both are used in the same test.
    """
    from django.test import Client

    test_client = Client()
    test_client.force_login(ungated_person)
    return test_client


@pytest.fixture
def social_app():
    """Create a social app for testing."""
    from allauth.socialaccount.models import SocialApp
    from django.contrib.sites.models import Site

    site = Site.objects.get_or_create(id=1, defaults={"domain": "example.com", "name": "example.com"})[0]
    app = SocialApp.objects.create(provider="google", name="Google", client_id="test_client_id", secret="test_secret")
    app.sites.add(site)
    return app
