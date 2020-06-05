import os

import pytest

from litesite.builder import SiteBuilder
from litesite.content import Site


@pytest.fixture
def settings(shared_datadir):
    return {
        "content": os.path.join(shared_datadir, "content"),
        "site": os.path.join(shared_datadir, "site"),
        "categories": {"tags": "tag"},
        "url": {"override": "overridden/{{ page|slug }}"},
    }


@pytest.fixture
def site(settings):
    test_site = Site(settings)
    SiteBuilder(test_site).build_site()

    return test_site


@pytest.fixture
def category(site):
    for cat in site.categories:
        if cat.name == "tags":
            test_category = cat

    return test_category


@pytest.fixture
def page(site):
    for pg in site.pages:
        if pg.name == "top_level_page":
            return pg

    raise NameError("top_level_page not found")
