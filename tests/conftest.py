"""
Pytest configuration and fixtures for django-accounts-center tests.
"""

import pytest
from allauth.account.models import EmailAddress
from allauth.socialaccount.models import SocialAccount, SocialApp
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.contrib.sites.models import Site
from django.test import Client

User = get_user_model()


@pytest.fixture
def user():
    """Create a test user."""
    return User.objects.create_user(username="testuser", email="test@example.com", password="testpass123")


@pytest.fixture
def authenticated_user(user):
    """Create an authenticated test user."""
    return user


@pytest.fixture
def client():
    """Create a test client."""
    return Client()


@pytest.fixture
def authenticated_client(client, user):
    """Create an authenticated test client."""
    client.force_login(user)
    return client


@pytest.fixture
def anonymous_user():
    """Create an anonymous user."""
    return AnonymousUser()


@pytest.fixture
def superuser():
    """Create a superuser."""
    return User.objects.create_superuser(username="admin", email="admin@example.com", password="adminpass123")


@pytest.fixture
def user_with_verified_email(user):
    """Create a user with verified email address."""
    EmailAddress.objects.create(user=user, email=user.email, verified=True, primary=True)
    return user


@pytest.fixture
def user_with_unverified_email():
    """Create a user with unverified email address."""
    user = User.objects.create_user(username="unverified", email="unverified@example.com", password="testpass123")
    EmailAddress.objects.create(user=user, email=user.email, verified=False, primary=True)
    return user


@pytest.fixture
def social_app():
    """Create a social app for testing."""
    site = Site.objects.get_or_create(id=1, defaults={"domain": "example.com", "name": "example.com"})[0]

    app = SocialApp.objects.create(provider="google", name="Google", client_id="test_client_id", secret="test_secret")
    app.sites.add(site)
    return app


@pytest.fixture
def user_with_social_account(user, social_app):
    """Create a user with social account."""
    SocialAccount.objects.create(
        user=user, provider="google", uid="12345", extra_data={"email": user.email, "name": "Test User"}
    )
    return user


@pytest.fixture
def valid_login_data():
    """Valid login form data."""
    return {"login": "test@example.com", "password": "testpass123"}


@pytest.fixture
def invalid_login_data():
    """Invalid login form data."""
    return {"login": "invalid@email.com", "password": "wrongpassword"}


@pytest.fixture
def valid_signup_data():
    """Valid signup form data."""
    return {"email": "newuser@example.com", "password1": "newpassword123", "password2": "newpassword123"}


@pytest.fixture
def invalid_signup_data():
    """Invalid signup form data."""
    return {"email": "invalid-email", "password1": "short", "password2": "different"}


@pytest.fixture
def entrance_layout_test_data():
    """Test data for entrance layout components."""
    return {"title": "Test Title", "subtitle": "Test Subtitle", "type": "login"}


@pytest.fixture
def standard_layout_test_data():
    """Test data for standard layout components."""
    return {"title": "Account Management"}
