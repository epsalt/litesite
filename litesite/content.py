import datetime
import os
import urllib.parse

from dateutil.parser import parse
import yaml

import metadata
import readers
import renderers


class Site:
    def __init__(self, config):
        with open(config, "r") as stream:
            self.config = yaml.safe_load(stream)

        self.content = self.config["content"]["root"]
        self.site = self.config["content"]["destination"]
        self.templates = self.config["content"]["templates"]
        self.base = self.config["site"]["base_url"]

        self.build_time = datetime.datetime.now(datetime.timezone.utc)

        self.reader = readers.Reader(self)
        self.renderer = renderers.Renderer(self)

        self.top = self.walk()
        self.sections = self.top.subsections

        self.categories = []
        for group, name in self.config["categories"].items():
            category = Category(name, group, self)
            self.categories.append(category)

    def walk(self):
        walker = os.walk(self.content)
        queue = []
        parent = None

        for path, dirs, files in walker:
            if queue:
                parent = queue.pop()

            section = Section(path, files, parent, self)

            for _dir in dirs:
                queue.append(section)

            if parent:
                parent.subsections.append(section)
            else:
                top = section

        return top

    @property
    def pages(self):
        sections = [self.top]
        while sections:
            section = sections.pop()
            sections += section.subsections
            yield from section.all_pages


class Section:
    def __init__(self, path, files, parent, site):
        self.path = path
        self.site = site
        self.name = os.path.basename(path)
        self.subsections = []
        self.parent = parent

        self.index = None
        self.kind = "section"
        self.pages = []

        for _file in files:
            page = Page(os.path.join(path, _file), self, site)

            if _file == "_index.md":
                self.index = page
                self.index.is_index = True
            else:
                self.pages.append(page)

    @property
    def pagesby_default(self):
        default_keys = ("date", "title")
        sorted_pages = sorted(
            self.pages, key=lambda page: tuple(getattr(page, k) for k in default_keys)
        )

        return sorted_pages

    @property
    def pagesby_date(self):
        sorted_pages = sorted(self.pages, key=lambda page: page.date)

        return sorted_pages

    @property
    def rel(self):
        return os.path.relpath(self.path, self.site.content)

    @property
    def all_pages(self):
        if self.index:
            return self.pages + [self.index]

        return self.pages


class Category:
    def __init__(self, name, group, site):
        self.name = name
        self.group = group
        self.site = site
        self.kind = "category"

        vals = set()
        for page in self.pages:
            for val in page.metadata.get(self.group):
                vals.add(val)

        self.items = [CategoryItem(self, val, site) for val in vals]

    def render(self):
        """Render tag index page"""
        out = os.path.join(self.site.site, self.group, "index.html")
        templates = [self.group, self.kind]

        self.site.renderer.render(self, out, templates)

    @property
    def rel(self):
        return os.path.join(self.group, self.name)

    @property
    def pages(self):
        """All pages with category present in metadata"""
        for page in self.site.pages:
            if page.metadata.get(self.group):
                yield page


class CategoryItem:
    def __init__(self, category, value, site):
        self.category = category
        self.value = value
        self.site = site
        self.kind = "item"

    def render(self):
        out = os.path.join(self.site.site, self.rel)
        templates = [self.value, self.kind, self.category.name]

        self.site.renderer.render(self, out, templates)

    @property
    def pages(self):
        for page in self.category.pages:
            if self.value in page.metadata.get(self.category.group):
                yield page

    @property
    def rel(self):
        return os.path.join(self.category.group, self.value)

    @property
    def url(self):
        return urllib.parse.urljoin(self.category.group, self.value)

    @property
    def permalink(self):
        return urllib.parse.urljoin(self.site.base, self.url)


class Page:
    def __init__(self, _file, section, site):
        read = site.reader.read(_file)
        self.content = read.content
        self.metadata = metadata.parse(read.meta)
        self.kind = "page"

        self.section = section
        self.site = site
        path, self.ext = os.path.splitext(_file)
        self.name = os.path.basename(path)

        self.is_index = False

    def render(self):
        out = os.path.join(self.site.site, self.url)
        templates = [self.metadata.get("template"), self.kind]
        self.site.renderer.render(self, out, templates)

    @property
    def nextin_section(self):
        sorted_pages = self.section.pagesby_default

        try:
            loc = sorted_pages.index(self)
            return sorted_pages[loc + 1]

        except IndexError:
            return None

    @property
    def previn_section(self):
        sorted_pages = self.section.pagesby_default

        loc = sorted_pages.index(self)
        prev = sorted_pages[loc - 1] if loc else None

        return prev

    @property
    def url(self):
        if self.section.name in self.site.config["url_format"].keys():
            template = self.site.config["url_format"][self.section.name]
        else:
            template = self.site.config["url_format"]["_default"]

        args = {self.kind: self}
        return self.site.renderer.render_string(template, args)

    @property
    def rel(self):
        return os.path.join(self.section.rel, self.name)

    @property
    def permalink(self):
        return urllib.parse.urljoin(self.site.base, self.url)

    @property
    def title(self):
        return self.metadata.get("title")

    @property
    def slug(self):
        return self.metadata.get("slug")

    @property
    def date(self):
        date_string = self.metadata["date"]

        if not date_string:
            return None

        return parse(date_string)
