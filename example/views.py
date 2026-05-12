from allauth.account.views import EmailView
from django.shortcuts import render


class EmailChangeTestView(EmailView):
    """EmailView subclass that forces account/email_change.html template.

    EmailView.template_name is a class-level attribute evaluated at import time,
    so per-test settings overrides cannot change which template allauth serves.
    This subclass hard-codes the email_change.html template for test isolation.
    """

    template_name = "account/email_change.html"


def _verified_email_required_view(request):
    """Render the verified_email_required gate page directly.

    In allauth 65.x this template is rendered inline by the
    @verified_email_required decorator; there is no registered URL for it.
    This test-only view registers a URL so tests can drive it via the client.
    """
    return render(request, "account/verified_email_required.html")
