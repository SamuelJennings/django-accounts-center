"""
Django Account Center App Configuration
"""

from django.apps import AppConfig


class AccountsCenterConfig(AppConfig):
    """Configuration for the Django Account Center application."""

    name = "dac"
    verbose_name = "Django Account Center"
    default_auto_field = "django.db.models.BigAutoField"
