import pytest


class TestBuild:
    def test_build_succeeds(self, site):
        assert site


class TestSections:
    def test_top_level_page(self, site):
        assert "top_level_page" in [page.name for page in site.pages]

    def test_parents(self, site):
        parents = [section.parent for section in site.sections]
        parentless = [parent is None for parent in parents]

        assert sum(parentless) == 1

    def test_nested_sections(self, site):
        assert [section.name == "dogs" for section in site.sections]

    def test_nested_page(self, site):
        assert [page.name == "borzoi" for page in site.pages]

    def test_section_with_no_pages(self, site):
        assert any(not section.pages for section in site.sections)


class TestCategories:
    def test_categories(self, site):
        assert "tags" in [category.name for category in site.categories]

    def test_category_pages(self, category):
        for pname in ["a_page", "b_page"]:
            assert pname in [page.name for page in category.pages]

    def test_category_values(self, category):
        for val in ["a", "b", "c", "d"]:
            assert val in [item.value for item in category.items]

    def test_duplicate_values(self, category):
        vals = [item.value for item in category.items]
        assert len(set(vals)) == len(vals)
