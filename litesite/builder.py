"""Site creation, loading, and batch rendering.

This module publishes the site in two steps, build and render. Build
is the loading of data from the content directory into internal data
structures. Render is template lookup and writing content to html.

"""

import os

from litesite.content import Category, CategoryItem, Page, Section, Site
from litesite.readers import Reader
from litesite.renderers import Renderer


def build_site(settings):
    """Initialize site and load content into data structures."""

    site = Site(settings)
    site.top = load_content(settings)
    site.categories = load_categories(site)

    return site


def render_site(site):
    """Renders every content object in the site."""

    renderer = Renderer(site.settings)
    dest = site.settings["site"]
    os.makedirs(dest, exist_ok=True)

    for page in site.pages:
        print(page.name)
        out = os.path.join(dest, page.url)
        args = {"page": page, "site": site, "settings": site.settings}
        renderer.render(out, page.templates, args)

    for category in site.categories:
        print(category.name)
        out = os.path.join(dest, category.url)
        args = {
            "category": category,
            "site": site,
            "settings": site.settings,
        }
        renderer.render(out, category.templates, args)

        for item in category.items:
            print(item.value)
            out = os.path.join(dest, item.url)
            args = {"item": item, "site": site, "settings": site.settings}
            renderer.render(out, item.templates, args)


def load_content(settings):
    """Load section and page data from the content directory.

    os.walk is used to traverse the content directory and populate
    section data.

    """

    reader = Reader()
    queue = []

    for path, dirs, files in os.walk(settings["content"]):
        parent = queue.pop() if queue else None
        section = build_section(path, parent, files, settings, reader)
        queue += [section for _ in dirs]

        if parent:
            parent.subsections.append(section)
        else:
            top = section

    return top


def build_section(path, parent, files, settings, reader):
    """Load a section and child pages."""

    rel = os.path.relpath(path, settings["content"])

    ## Special name for site root section
    if os.path.basename(rel) == ".":
        name = "_top"
    else:
        name = os.path.basename(rel)

    ## Get section page URL overrides from settings
    if settings.get("url"):
        override = settings["url"].get(name)
    else:
        override = None

    section = Section(name, rel, parent, override)

    for _file in files:
        name = os.path.basename(os.path.splitext(_file)[0])
        with open(os.path.join(path, _file), "r") as f:
            text, metadata = reader.read(f.read())

        page = Page(name, text, metadata, section)

        if page.is_index:
            section.index = page
        else:
            section.pages.append(page)

    return section


def load_categories(site):
    """Populate categories from config definition"""

    cats = site.settings["categories"]
    pages = site.pages
    categories = []

    if not cats:
        return categories

    for name, item_name in cats.items():
        category = Category(name, item_name)
        for page in pages:
            if page.metadata.get(name):
                category.pages.append(page)

        vals = set()
        for page in category.pages:
            for val in page.metadata.get(name):
                vals.add(val)

        category.items = [CategoryItem(category, val) for val in vals]
        categories.append(category)

    return categories
