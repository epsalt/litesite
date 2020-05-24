import datetime
import os
import urllib.parse

from dateutil.parser import parse
from jinja2 import Template

import readers
import renderers


class Site:
    def __init__(self, settings):

        self.reader = readers.Reader(self)
        self.renderer = renderers.Renderer(self, settings)
        self.build_time = datetime.datetime.now(datetime.timezone.utc)

        self.top = self._walk(settings, self.reader, self.renderer)
        self.sections = self.top.subsections

        self.categories = []
        for group, name in settings.categories.items():
            category = Category(name, group, settings)
            for page in self.pages:
                if page.metadata.get(group):
                    category.pages.append(page)

            vals = set()
            for page in category.pages:
                for val in page.metadata.get(group):
                    vals.add(val)

            category.items = [CategoryItem(category, val, settings) for val in vals]

            self.categories.append(category)

    @staticmethod
    def _walk(settings, reader, renderer):
        walker = os.walk(settings.content)
        queue = []
        parent = None

        for path, dirs, files in walker:
            if queue:
                parent = queue.pop()

            section = Section(path, parent, settings)

            for _file in files:
                page = Page(
                    os.path.join(path, _file), section, reader, renderer, settings,
                )

                if _file == "_index.md":
                    section.index = page
                    section.index.is_index = True
                else:
                    section.pages.append(page)

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
    def __init__(self, path, parent, settings):
        self.path = path
        self.name = os.path.basename(path)
        self.subsections = []
        self.parent = parent
        self.settings = settings

        self.index = None
        self.kind = "section"
        self.pages = []

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
        return os.path.relpath(self.path, self.settings.content)

    @property
    def all_pages(self):
        if self.index:
            return self.pages + [self.index]

        return self.pages


class Category:
    def __init__(self, name, group, settings):
        self.name = name
        self.group = group
        self.kind = "category"
        self.settings = settings

        self.pages = []
        self.items = []

    def render(self, site):
        """Render tag index page"""
        out = os.path.join(self.settings.site, self.group, "index.html")
        templates = [self.group, self.kind]

        site.renderer.render(self, out, templates)

    @property
    def rel(self):
        return os.path.join(self.group, self.name)


class CategoryItem:
    def __init__(self, category, value, settings):
        self.category = category
        self.value = value
        self.kind = "item"
        self.settings = settings

    def render(self, site):
        out = os.path.join(self.settings.site, self.rel)
        templates = [self.value, self.kind, self.category.name]

        site.renderer.render(self, out, templates)

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
        return urllib.parse.urljoin(self.settings.base, self.url)


class Page:
    def __init__(self, _file, section, reader, renderer, settings):
        self.content, self.metadata = reader.read(_file)
        self.kind = "page"
        self.settings = settings
        self.renderer = renderer

        self.section = section
        path, self.ext = os.path.splitext(_file)
        self.name = os.path.basename(path)

        self.is_index = False

    def render(self, site):
        out = os.path.join(self.settings.site, self.url)
        templates = [self.metadata.get("template"), self.kind]
        site.renderer.render(self, out, templates)

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
        if self.section.name in self.settings.url_format.keys():
            template = self.settings.url_format[self.section.name]
        else:
            template = self.settings.url_format["_default"]

        args = {self.kind: self}
        return Template(template).render(args)

    @property
    def rel(self):
        return os.path.join(self.section.rel, self.name)

    @property
    def permalink(self):
        return urllib.parse.urljoin(self.settings.base, self.url)

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
