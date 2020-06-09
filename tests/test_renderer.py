import os

import pytest

from litesite.renderers import Renderer


class TestStringRender:
    def test_render_from_string(self, page):
        string = "{{ page.name }}"
        text = Renderer.render_from_string(string, args={"page": page})

        assert text == "top_level_page"


class TestTemplateRenderer:
    def test_template_selection(self, page, renderer):
        template = renderer.lookup(page.templates)

        assert template.name == "page.html"

    def test_none_in_lookup(self, page, renderer):
        templates = [None, "page"]
        template = renderer.lookup(templates)

        assert template.name == "page.html"

    def test_number_in_lookup(self, page, renderer):
        templates = [404, None]
        template = renderer.lookup(templates)

        assert template.name == "404.html"

    def test_template_render_text(self, page, renderer):
        template = renderer.lookup(page.templates)
        args = {"page": page}
        text = renderer.render(page.url, page.templates, args)

        assert text == "<p>This is a top level page.</p>"

    def test_template_render_file(self, settings, page, renderer):
        dest = os.path.join(settings["site"], page.url)
        renderer.render(dest, page.templates, {"page": page})

        with open(dest) as _file:
            text = _file.read()

        assert text == "<p>This is a top level page.</p>"

    def test_preprocessing(self, site):
        for pg in site.pages:
            if pg.name == "preprocessing":
                test_page = pg

        assert test_page.content == "<p>preprocessing okay</p>"


class TestFilters:
    def test_datetime(self):
        string = "{{ '2010/01/01'|datetime }}"
        text = Renderer.render_from_string(string)

        assert text == "2010-01-01 00:00:00"

    def test_isoformat(self):
        string = "{{ '2010/01/01'|datetime|isoformat }}"
        text = Renderer.render_from_string(string)

        assert text == "2010-01-01T00:00:00"

    def test_slug(self, page):
        string = "{{ page|slug }}"
        text = Renderer.render_from_string(string, {"page": page})

        assert text == "top"

    def test_date(self, page):
        string = "{{ page|date('%Y--%m--%d') }}"
        text = Renderer.render_from_string(string, {"page": page})

        assert text == "2013--04--15"

    def test_permalink(self):
        string = "{{ 'test/location'|permalink }}"
        text = Renderer.render_from_string(
            string, {"settings": {"base": "https://www.test.com"}}
        )

        assert text == "https://www.test.com/test/location"
