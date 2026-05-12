"""
Cotton rendering tests for dac/base.html.

Verifies the block contract, structural composition, and consistent UI
provided by the shared management-page base template.

All tests render a minimal child template that extends dac/base.html via
cotton_render_string_soup, then assert specific DOM properties.
The template itself is NOT modified by these tests — read-only verification only.
"""

import pathlib

import pytest

# Bare-minimum child template: extends base, loads i18n, no block overrides.
_BASE = '{% extends "dac/base.html" %}{% load i18n %}'


@pytest.fixture(autouse=True)
def use_test_urls(settings):
    """Set ROOT_URLCONF so {% url "account-center" %} resolves correctly."""
    settings.ROOT_URLCONF = "tests.urls"


# ---------------------------------------------------------------------------
# US1 — Developer Block Contract (P1, MVP)
# ---------------------------------------------------------------------------


class TestDacBaseBlockContract:
    """Verify every public block in dac/base.html per US1 acceptance scenarios."""

    def test_sidebar_injects_account_center_menu(self, cotton_render_string_soup):
        """Rendering a bare extend produces an <aside class="app-sidebar"> element.

        dac/base.html overrides the app.sidebar block with
        <c-app.sidebar menu="Account Center Menu" />.  The Cotton component
        renders an <aside class="app-sidebar"> regardless of whether the menu
        has items, confirming the block override is in effect.
        """
        soup = cotton_render_string_soup(_BASE)
        aside = soup.find("aside", class_="app-sidebar")
        assert aside is not None

    def test_breadcrumbs_root_item_present(self, cotton_render_string_soup):
        """The default page.breadcrumbs block renders an 'Account Center' link.

        FR-006: the default breadcrumb item must be labelled 'Account Center'
        and link to the account-center home URL.
        """
        soup = cotton_render_string_soup(_BASE)
        links = soup.find_all("a")
        account_center_links = [a for a in links if a.get_text(strip=True) == "Account Center"]
        assert len(account_center_links) >= 1
        assert account_center_links[0].get("href") not in (None, "")

    def test_title_block_empty_by_default(self, cotton_render_string_soup):
        """When the title block is not overridden, no heading is rendered.

        <c-mvp-toolbar> only emits an <h*> when its title slot is non-empty.
        An overridden (empty) title block produces a whitespace-only slot,
        which Cotton strips to an empty string, so {% if title %} is falsy
        and no heading element appears in the output.
        """
        soup = cotton_render_string_soup(_BASE)
        h1 = soup.find("h1")
        # Either no h1 is rendered, or it contains only whitespace
        assert h1 is None or not h1.get_text(strip=True)

    def test_title_block_override_renders(self, cotton_render_string_soup):
        """Overriding the title block produces an <h1> with the given text.

        <c-mvp-toolbar> renders its heading at level 1 (default) when the
        title slot is non-empty.
        """
        template = _BASE + "{% block title %}My Test Page{% endblock title %}"
        soup = cotton_render_string_soup(template)
        h1 = soup.find("h1")
        assert h1 is not None
        assert h1.get_text(strip=True) == "My Test Page"

    def test_page_content_placeholder_default(self, cotton_render_string_soup):
        """The default page.content block shows the 'Coming soon...' placeholder.

        FR-010: the default content must be a localised placeholder, not an empty block.
        """
        soup = cotton_render_string_soup(_BASE)
        assert "Coming soon" in soup.get_text()

    def test_page_content_block_override_renders(self, cotton_render_string_soup):
        """Overriding page.content renders the provided HTML inside the card stack.

        The element with id='my-content' must appear in the rendered output,
        confirming the override content reaches the final DOM.
        """
        template = _BASE + '{% block page.content %}<p id="my-content">Hello</p>{% endblock page.content %}'
        soup = cotton_render_string_soup(template)
        el = soup.find(id="my-content")
        assert el is not None
        assert el.get_text(strip=True) == "Hello"

    def test_breadcrumbs_block_override_extends_with_block_super(self, cotton_render_string_soup):
        """Using {{ block.super }} in page.breadcrumbs appends a second item.

        Both 'Account Center' (from the default) and 'Sub Page' (appended)
        must appear as breadcrumb-related text in the rendered HTML.
        """
        template = (
            _BASE
            + "{% block page.breadcrumbs %}"
            + "{{ block.super }}"
            + '<c-breadcrumbs.item text="Sub Page" />'
            + "{% endblock page.breadcrumbs %}"
        )
        soup = cotton_render_string_soup(template)
        text = soup.get_text()
        assert "Account Center" in text
        assert "Sub Page" in text


# ---------------------------------------------------------------------------
# US2 — Consistent Management UI (P2)
# ---------------------------------------------------------------------------


class TestDacBaseConsistency:
    """Verify structural consistency across multiple pages that extend dac/base.html."""

    def test_two_subpages_share_sidebar_and_breadcrumb(self, cotton_render_string_soup):
        """Both sub-pages carry the sidebar and root breadcrumb regardless of title.

        Renders two distinct child templates and asserts that both share the
        same structural anchors: <aside class="app-sidebar"> and an
        'Account Center' breadcrumb link.
        """
        template_a = _BASE + "{% block title %}Page A{% endblock %}"
        template_b = _BASE + "{% block title %}Page B{% endblock %}"

        soup_a = cotton_render_string_soup(template_a)
        soup_b = cotton_render_string_soup(template_b)

        for soup in (soup_a, soup_b):
            assert soup.find("aside", class_="app-sidebar") is not None
            links = soup.find_all("a")
            account_center_links = [a for a in links if a.get_text(strip=True) == "Account Center"]
            assert len(account_center_links) >= 1

    def test_real_account_center_page_renders_correctly(self, cotton_render_string_soup):
        """The actual dac/account_center.html sub-page renders with full base structure.

        SC-001: existing sub-pages that extend dac/base.html must render the
        same structural layout (sidebar, breadcrumb, placeholder content).
        account_center.html extends dac/base.html with zero block overrides.
        """
        template = '{% extends "dac/account_center.html" %}{% load i18n %}'
        soup = cotton_render_string_soup(template)

        assert soup.find("aside", class_="app-sidebar") is not None

        links = soup.find_all("a")
        account_center_links = [a for a in links if a.get_text(strip=True) == "Account Center"]
        assert len(account_center_links) >= 1

        assert "Coming soon" in soup.get_text()


# ---------------------------------------------------------------------------
# US3 — Template Structure Legibility (P3)
# ---------------------------------------------------------------------------


class TestDacBaseStructure:
    """Verify that dac/base.html contains required blocks in the expected positions."""

    def test_all_required_blocks_present(self):
        """The template source contains every required named block tag.

        US3 SC: a developer listing all {% block %} tags must find all seven
        documented blocks (app.sidebar, content, page.header, page.breadcrumbs,
        page.content-wrapper, title, page.content).
        """
        template_path = (
            pathlib.Path(__file__).resolve().parent.parent.parent / "dac" / "templates" / "dac" / "base.html"
        )
        source = template_path.read_text(encoding="utf-8")
        required_blocks = [
            "app.sidebar",
            "content",
            "page.header",
            "page.breadcrumbs",
            "page.content-wrapper",
            "title",
            "page.content",
        ]
        for block_name in required_blocks:
            assert f"{{% block {block_name} %}}" in source, f"Block '{block_name}' not found in dac/base.html"

    def test_page_breadcrumbs_default_has_one_item(self, cotton_render_string_soup):
        """Rendering without block overrides shows at least one 'Account Center' breadcrumb link.

        FR-006: the default page.breadcrumbs block must contain exactly one
        breadcrumb item linking to the Account Center home URL.
        """
        soup = cotton_render_string_soup(_BASE)
        links = soup.find_all("a")
        account_center_links = [a for a in links if a.get_text(strip=True) == "Account Center"]
        assert len(account_center_links) >= 1
        assert account_center_links[0].get("href") not in (None, "")

    def test_card_stack_wraps_page_content(self, cotton_render_string_soup):
        """The card.stack wrapper element is present in the rendered output.

        FR-009: <c-card.stack> renders as <div class="d-flex flex-column gap-3">.
        Its presence confirms the structural card-stack wrapper is injected by
        the base template, independently of the content inside it.
        """
        soup = cotton_render_string_soup(_BASE)
        card_stack = soup.find("div", class_="d-flex")
        assert card_stack is not None
