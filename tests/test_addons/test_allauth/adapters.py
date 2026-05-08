"""
Shared test adapters for allauth E2E and screenshot tests.

These must be importable via dotted path so that the Django live server thread
(which runs in the same process) can resolve them when tests override
settings.ACCOUNT_ADAPTER.
"""

from allauth.account.adapter import DefaultAccountAdapter


class ClosedSignupAdapter(DefaultAccountAdapter):
    """Adapter that unconditionally disables new signups (for testing US4)."""

    def is_open_for_signup(self, request):
        return False
