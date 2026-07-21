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
def social_app():
    """Create a social app for testing."""
    from allauth.socialaccount.models import SocialApp
    from django.contrib.sites.models import Site

    site = Site.objects.get_or_create(id=1, defaults={"domain": "example.com", "name": "example.com"})[0]
    app = SocialApp.objects.create(provider="google", name="Google", client_id="test_client_id", secret="test_secret")
    app.sites.add(site)
    return app
