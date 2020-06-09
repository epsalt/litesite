from dateutil.parser import parse
import pytest


class TestSection:
    def test_sorted(self, section):
        slugs = [page.metadata["slug"] for page in section.sorted]
        expected_slugs = ["borzoi", "samoyed", "borzoi2"]
        assert slugs == expected_slugs

    def test_all_pages(self, section):
        slugs = [page.metadata["slug"] for page in section.all_pages]
        expected_slugs = ["borzoi", "samoyed", "borzoi2", "index"]

        assert set(slugs) == set(expected_slugs)


class TestPage:
    def test_next(self, section):
        page = section.sorted[0]
        expected = ["borzoi", "samoyed", "borzoi2"]

        for slug in expected:
            assert page.metadata["slug"] == slug
            page = page.next

        assert page is None

    def test_prev(self, section):
        page = section.sorted[-1]
        expected = ["borzoi2", "samoyed", "borzoi"]

        for slug in expected:
            assert page.metadata["slug"] == slug
            page = page.prev

        assert page is None

    def test_url_override(self, site):
        for section in site.sections:
            if section.name == "overridden":
                test_section = section
                page = test_section.pages[0]
                assert page.url == "overridden/" + page.metadata["slug"]
                return

        assert False

    def test_index(self, section):
        for page in section.all_pages:
            if page.name == "_index":
                assert page.is_index
                assert page is section.index
                return

        assert False

    def test_metadata_date(self, page):
        expected = parse("2013-04-15 00:00:00 -0000")
        assert page.metadata["date"] == expected

    def test_metadata(self, page):
        expected = {
            "title": "Top Level Page",
            "slug": "top",
            "arbitrary": ["a", "b", "c"],
        }

        for key, item in expected.items():
            assert page.metadata[key] == item
