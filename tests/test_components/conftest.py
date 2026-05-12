"""
Conftest for test_components: override cotton_render_string_soup to attach request.site.

Templates in the dac/base.html rendering chain (mvp/base.html, app.header,
app.sidebar.header) access {{ request.site.name }}.  The upstream fixture's
RequestFactory request has no .site attribute because it bypasses
CurrentSiteMiddleware.  This override attaches a minimal Site-like object so
the attribute lookup resolves without error or a database hit.
"""

from types import SimpleNamespace

import pytest
from bs4 import BeautifulSoup
from django.template import Context, Template
from django.test import RequestFactory
from django_cotton.compiler_regex import CottonCompiler  # type: ignore[import-untyped]

_compiler = CottonCompiler()
_factory = RequestFactory()

_MOCK_SITE = SimpleNamespace(name="Test Site", domain="example.com", id=1)


@pytest.fixture
def cotton_render_string_soup():
    """
    Drop-in replacement for the upstream cotton_render_string_soup fixture.

    Identical behaviour except that request.site is populated with a
    SimpleNamespace so that templates referencing {{ request.site.name }}
    (e.g. mvp/base.html, app.header.html, app.sidebar.header.html) render
    correctly without requiring the Django sites framework or a database.
    """

    def _render(template_string, context=None):
        if context is None:
            context = {}
        request = _factory.get("/")
        request.site = _MOCK_SITE
        context["request"] = request

        compiled = _compiler.process(template_string)
        html = Template(compiled).render(Context(context))
        return BeautifulSoup(html, "html.parser")

    return _render
