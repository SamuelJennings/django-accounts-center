"""
Pytest configuration and fixtures for django-accounts-center tests.
"""

import pytest


def pytest_configure(config):
    """Apply performance overrides for the test session.

    ``tests/settings.py`` is shared with the dev server (manage.py runserver),
    so expensive settings that are fine for development but hurt test speed are
    overridden here rather than in the settings file itself.

    Runs after pytest-django has called django.setup(), so django.conf.settings
    is safe to modify at this point.
    """
    from django.conf import settings

    # libsass takes ~1.35 s per SCSS file per render; with DummyCache every
    # template render recompiles from scratch.  Tests don't check CSS output.
    settings.COMPRESS_PRECOMPILERS = ()

    # LocMemCache lets django-compressor (and other middleware) cache across
    # requests within the same process, eliminating repeated work per test.
    settings.CACHES = {
        "default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"},
    }


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
