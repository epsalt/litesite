import os

import yaml

from litesite.content import Category, CategoryItem, Page, Section, Site
from litesite.readers import Reader
from litesite.renderers import Renderer


def publish(config):
    with open(config, "r") as stream:
        settings = yaml.safe_load(stream)

    site = Site(settings)
    builder = SiteBuilder(site)

    builder.build_site()
    builder.render_site()

    return site


class SiteBuilder:
    def __init__(self, site):
        self.site = site

    def build_site(self):
        content = self.site.settings["content"]
        overrides = self.site.settings.get("url")
        cats = self.site.settings.get("categories")

        self.site.top = self._build_sections(content, overrides)
        self.site.categories = self._build_categories(cats, self.site.pages)

    def render_site(self):
        renderer = Renderer(self.site.settings)
        dest = self.site.settings["site"]
        os.makedirs(dest, exist_ok=True)

        for page in self.site.pages:
            print(page.name)
            out = os.path.join(dest, page.url)
            args = {"page": page, "site": self.site, "settings": self.site.settings}
            renderer.render(out, page.templates, args)

        for category in self.site.categories:
            print(category.name)
            out = os.path.join(dest, category.url)
            args = {
                "category": category,
                "site": self.site,
                "settings": self.site.settings,
            }
            renderer.render(out, category.templates, args)

            for item in category.items:
                print(item.value)
                out = os.path.join(dest, item.url)
                args = {"item": item, "site": self.site, "settings": self.site.settings}
                renderer.render(out, item.templates, args)

    @staticmethod
    def _build_sections(content, overrides):
        reader = Reader()
        walker = os.walk(content)
        queue = []
        parent = None

        for path, dirs, files in walker:
            if queue:
                parent = queue.pop()

            ## Build sections
            rel = os.path.relpath(path, content)
            name = "_top" if os.path.basename(rel) == "." else os.path.basename(rel)
            override = overrides.get(name) if overrides else None
            section = Section(name, rel, parent, override)

            ## Build pages
            for _file in files:
                with open(os.path.join(path, _file), "r") as f:
                    text = Renderer.render_from_string(f.read())

                text, metadata = reader.read(text)
                name = os.path.basename(os.path.splitext(_file)[0])
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

    @staticmethod
    def _build_categories(cats, pages):
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
