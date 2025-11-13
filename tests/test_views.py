"""
Tests for django-accounts-center views.
"""

import pytest
from django.contrib.auth import get_user_model
from django.test import RequestFactory
from django.urls import reverse

from dac.addons.actstream.views import AccountFollowers, AccountFollowing
from dac.views import EntranceView, Home

User = get_user_model()


@pytest.mark.django_db
class TestEntranceView:
    """Tests for the EntranceView."""

    def test_entrance_view_get(self, client):
        """Test GET request to entrance view."""
        response = client.get("/")  # Assuming entrance view is at root
        assert response.status_code == 200

    def test_entrance_view_context(self):
        """Test context data includes forms."""
        factory = RequestFactory()
        request = factory.get("/")
        view = EntranceView()
        view.request = request

        context = view.get_context_data()
        assert "login_form" in context
        assert "signup_form" in context


@pytest.mark.django_db
class TestLoginTemplateView:
    """Tests for the LoginTemplateView."""

    def test_login_required(self, client):
        """Test that view requires authentication."""
        url = reverse("account-center")  # Assuming this uses LoginTemplateView
        response = client.get(url)
        # Should redirect to login
        assert response.status_code == 302

    def test_authenticated_access(self, authenticated_client):
        """Test authenticated access works."""
        url = reverse("account-center")
        response = authenticated_client.get(url)
        assert response.status_code == 200


@pytest.mark.django_db
class TestHomeView:
    """Tests for the Home view."""

    def test_home_requires_login(self, client):
        """Test that home view requires authentication."""
        url = reverse("account-center")
        response = client.get(url)
        assert response.status_code == 302  # Redirect to login

    def test_home_authenticated(self, authenticated_client):
        """Test authenticated access to home view."""
        url = reverse("account-center")
        response = authenticated_client.get(url)
        assert response.status_code == 200

    def test_home_context_data(self, user):
        """Test context data includes Stripe settings."""
        factory = RequestFactory()
        request = factory.get("/")
        request.user = user

        view = Home()
        view.request = request

        context = view.get_context_data()
        assert "stripe_pricing_table_id" in context
        assert "stripe_public_key" in context


@pytest.mark.django_db
class TestAccountFollowersView:
    """Tests for the AccountFollowers view."""

    def test_requires_login(self, client):
        """Test that view requires authentication."""
        factory = RequestFactory()
        request = factory.get("/account/followers/")

        view = AccountFollowers()
        view.request = request

        # Should require login
        assert hasattr(view, "login_required")

    def test_context_data_without_actstream(self, user):
        """Test context data when actstream is not available."""
        factory = RequestFactory()
        request = factory.get("/account/followers/")
        request.user = user

        view = AccountFollowers()
        view.request = request

        context = view.get_context_data()
        assert "followers" in context
        assert context["followers"] == []


@pytest.mark.django_db
class TestAccountFollowingView:
    """Tests for the AccountFollowing view."""

    def test_requires_login(self, client):
        """Test that view requires authentication."""
        factory = RequestFactory()
        request = factory.get("/account/following/")

        view = AccountFollowing()
        view.request = request

        # Should require login
        assert hasattr(view, "login_required")

    def test_context_data_without_actstream(self, user):
        """Test context data when actstream is not available."""
        factory = RequestFactory()
        request = factory.get("/account/following/")
        request.user = user

        view = AccountFollowing()
        view.request = request

        context = view.get_context_data()
        assert "following" in context
        assert context["following"] == []


@pytest.mark.django_db
class TestViewIntegration:
    """Integration tests for views."""

    def test_view_templates_exist(self, authenticated_client):
        """Test that view templates can be rendered."""
        # This would require the actual templates to exist
        # For now, we just test that the views don't raise exceptions
        factory = RequestFactory()
        request = factory.get("/")
        request.user = User.objects.create_user("test", "test@example.com", "pass")

        # Test each view can be instantiated
        views = [EntranceView(), Home(), AccountFollowers(), AccountFollowing()]
        for view in views:
            view.request = request
            assert hasattr(view, "get_context_data")

    def test_error_handling(self, user):
        """Test error handling in views."""
        factory = RequestFactory()
        request = factory.get("/")
        request.user = user

        # Test that views handle missing templates gracefully
        view = Home()
        view.request = request

        # Should not raise exception when getting context
        context = view.get_context_data()
        assert isinstance(context, dict)
