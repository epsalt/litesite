import os

from litesite.content import Category, CategoryItem, Page, Section, Site
from litesite.readers import Reader


def build_site(settings):
    site = Site(settings)
    reader = Reader(settings)

    site.top = build_sections(site.settings, reader)
    site.categories = build_categories(site.pages, settings)

    return site


def build_sections(settings, reader):
    walker = os.walk(settings["content"])
    queue = []
    parent = None

    ## Build sections
    for path, dirs, files in walker:
        if queue:
            parent = queue.pop()

        rel = os.path.relpath(path, settings["content"])
        name = os.path.basename(rel)
        override = settings["url"].get(name) if settings.get("url") else None
        section = Section(name, rel, parent, override)

        ## Build pages
        for _file in files:
            name = os.path.basename(os.path.splitext(_file)[0])
            text, metadata = reader.read(os.path.join(path, _file))
            page = Page(name, text, metadata, section)

            if page.is_index:
                section.index = page
            else:
                section.pages.append(page)

        queue += [section for _ in dirs]

        if parent:
            parent.subsections.append(section)
        else:
            top = section

    return top


def build_categories(pages, settings):
    for group, name in settings["categories"].items():
        category = Category(name, group)
        for page in pages:
            if page.metadata.get(group):
                category.pages.append(page)

        vals = set()
        for page in category.pages:
            for val in page.metadata.get(group):
                vals.add(val)

        category.items = [CategoryItem(category, val) for val in vals]
        yield category
