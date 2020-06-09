import os

import pytest

from litesite.builder import build_site
from litesite.renderers import Renderer


@pytest.fixture
def settings(shared_datadir):
    return {
        "content": os.path.join(shared_datadir, "content"),
        "site": os.path.join(shared_datadir, "site"),
        "categories": {"tags": "tag"},
        "url": {"override": "overridden/{{ page|slug }}"},
        "preprocess_test": "preprocessing okay",
    }


@pytest.fixture
def renderer(shared_datadir):
    settings = {"templates": f"{shared_datadir}/templates"}

    return Renderer(settings)


@pytest.fixture
def site(settings):
    return build_site(settings)


@pytest.fixture
def category(site):
    for cat in site.categories:
        if cat.name == "tags":
            test_category = cat

    return test_category


@pytest.fixture
def section(site):
    for section in site.sections:
        if section.name == "dogs":
            return section

    raise NameError


@pytest.fixture
def page(site):
    for pg in site.pages:
        if pg.name == "top_level_page":
            return pg

    raise NameError("top_level_page not found")
