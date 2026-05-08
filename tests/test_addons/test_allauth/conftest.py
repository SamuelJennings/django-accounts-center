"""
Conftest for test_allauth: override ROOT_URLCONF to the test URL configuration.
"""

import pytest


@pytest.fixture(autouse=True)
def use_test_urls(settings):
    """Use test URL config that doesn't require debug_toolbar."""
    settings.ROOT_URLCONF = "tests.urls"
