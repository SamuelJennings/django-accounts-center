"""
Cotton rendering tests for the shared entrance page (dac/entrance.html) and
its <c-dac.entrance> component (cotton/dac/entrance.html).

The entrance page is the core package's extension point for anonymous-facing
pages: any integration reaches it with a bare {% extends %} and fills
{% block content %}, and gets the full-screen background, the centered card,
the site logo, the package stylesheet and the messages region for free —
without depending on, or referencing, any integration template.
"""

# Bare-minimum child template: extends the core entrance page, no block
# overrides. This belongs to no app, which is the point (SC-001).
_ENTRANCE = '{% extends "dac/entrance.html" %}{% load i18n %}'


class TestEntrancePageBlockContract:
    def test_full_screen_background_present(self, cotton_render_string_soup):
        """mvp's <c-entrance> background wraps the page (full-screen, centered)."""
        soup = cotton_render_string_soup(_ENTRANCE)
        background = soup.find("div", class_="min-h-screen")
        assert background is not None

    def test_one_centered_card_present(self, cotton_render_string_soup):
        """Exactly one card renders (mvp's <c-entrance> card) — no app supplies
        its own card markup."""
        soup = cotton_render_string_soup(_ENTRANCE)
        cards = soup.find_all("div", class_="card")
        assert len(cards) == 1

    def test_site_logo_present(self, cotton_render_string_soup):
        """The site logo renders above the content, inside the card."""
        soup = cotton_render_string_soup(_ENTRANCE)
        img = soup.find("img", alt="Site Logo")
        assert img is not None

    def test_content_block_override_renders(self, cotton_render_string_soup):
        """{% block content %} content reaches the DOM inside the card."""
        template = _ENTRANCE + '{% block content %}<p id="my-content">Hello</p>{% endblock content %}'
        soup = cotton_render_string_soup(template)
        el = soup.find(id="my-content")
        assert el is not None
        assert el.get_text(strip=True) == "Hello"

    def test_stylesheet_link_present(self, cotton_render_string_soup):
        """The entrance page itself carries the package stylesheet, so an
        extending page never has to know about it (FR-009)."""
        soup = cotton_render_string_soup(_ENTRANCE)
        links = soup.find_all("link", rel="stylesheet")
        assert any("dac.css" in (link.get("href") or "") for link in links)

    def test_messages_region_present(self, cotton_render_string_soup):
        """mvp's <c-messages> toast region renders even with no messages
        queued (FR-011)."""
        soup = cotton_render_string_soup(_ENTRANCE)
        toast = soup.find("div", class_="toast")
        assert toast is not None


class TestEntranceComponentConsistency:
    def test_two_distinct_pages_share_structure(self, cotton_render_string_soup):
        """Two unrelated pages extending the entrance page get identical chrome."""
        template_a = _ENTRANCE + "{% block content %}Page A{% endblock content %}"
        template_b = _ENTRANCE + "{% block content %}Page B{% endblock content %}"
        for template in (template_a, template_b):
            soup = cotton_render_string_soup(template)
            assert soup.find("div", class_="min-h-screen") is not None
            assert soup.find("img", alt="Site Logo") is not None


def _entrance_with_size(size):
    """A layout overriding {% block entrance %} to declare a card width,
    with {% block content %} already filled (so a caller does not also
    need to append its own, which would duplicate the block name)."""
    return (
        '{% extends "dac/entrance.html" %}{% load i18n %}'
        "{% block entrance %}"
        f'<c-dac.entrance size="{size}">'
        "{% block content %}Hi{% endblock content %}"
        "</c-dac.entrance>"
        "{% endblock entrance %}"
    )

# mvp's <c-entrance small> branch adds this class (see the `small` c-var in
# django-mvp's cotton/entrance/index.html); its absence is the "full" branch.
_SMALL_WIDTH_CLASS = "md:max-w-2xl"


class TestEntranceComponentWidth:
    def test_default_renders_todays_width(self, cotton_render_string_soup):
        """A layout that overrides nothing keeps today's (small) card width."""
        soup = cotton_render_string_soup(_ENTRANCE + "{% block content %}Hi{% endblock content %}")
        card = soup.find("div", class_="card")
        assert card is not None
        assert _SMALL_WIDTH_CLASS in card.get("class", [])

    def test_size_full_renders_wider_card(self, cotton_render_string_soup):
        """A layout overriding {% block entrance %} with size="full" drops
        mvp's small-width class, rendering a wider card than the default."""
        template = _entrance_with_size("full")
        soup = cotton_render_string_soup(template)
        card = soup.find("div", class_="card")
        assert card is not None
        assert _SMALL_WIDTH_CLASS not in card.get("class", [])

    def test_default_and_full_card_classes_differ(self, cotton_render_string_soup):
        """The default and size="full" branches render distinct card classes."""
        default_soup = cotton_render_string_soup(_ENTRANCE + "{% block content %}Hi{% endblock content %}")
        full_template = _entrance_with_size("full")
        full_soup = cotton_render_string_soup(full_template)

        default_card = default_soup.find("div", class_="card")
        full_card = full_soup.find("div", class_="card")
        assert default_card.get("class", []) != full_card.get("class", [])

    def test_unrecognised_size_falls_back_to_default_width(self, cotton_render_string_soup):
        """An unrecognised size value falls back to today's width rather than
        emitting broken markup."""
        template = _entrance_with_size("huge")
        soup = cotton_render_string_soup(template)
        card = soup.find("div", class_="card")
        assert card is not None
        assert _SMALL_WIDTH_CLASS in card.get("class", [])
