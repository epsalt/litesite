import datetime
import os
import urllib.parse

from dateutil.parser import parse
from jinja2 import Template

import readers
import renderers


class Site:
    def __init__(self, settings):

        self.reader = readers.Reader(self, settings)
        self.renderer = renderers.Renderer(self, settings)
        self.build_time = datetime.datetime.now(datetime.timezone.utc)

        self.top = self._walk(settings, self.reader)
        self.sections = self.top.subsections

        self.categories = []
        for group, name in settings.categories.items():
            category = Category(name, group)
            for page in self.pages:
                if page.metadata.get(group):
                    category.pages.append(page)

            vals = set()
            for page in category.pages:
                for val in page.metadata.get(group):
                    vals.add(val)

            category.items = [CategoryItem(category, val) for val in vals]

            self.categories.append(category)

    @staticmethod
    def _walk(settings, reader):
        walker = os.walk(settings.content)
        queue = []
        parent = None

        for path, dirs, files in walker:
            if queue:
                parent = queue.pop()

            rel = os.path.relpath(path, settings.content)
            section = Section(rel, parent)

            for _file in files:
                page = Page(os.path.join(path, _file), section, reader, settings)

                if _file == "_index.md":
                    section.index = page
                    page.is_index = True
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
    def __init__(self, rel, parent):
        self.rel = rel
        self.name = os.path.basename(rel)
        self.subsections = []
        self.parent = parent

        self.index = None
        self.kind = "section"
        self.pages = []

    @property
    def sorted(self):
        default_keys = ("date", "title")
        sorted_pages = sorted(
            self.pages, key=lambda page: tuple(getattr(page, k) for k in default_keys)
        )

        return sorted_pages

    @property
    def all_pages(self):
        if self.index:
            return self.pages + [self.index]

        return self.pages


class Category:
    def __init__(self, name, group):
        self.name = name
        self.group = group
        self.kind = "category"

        self.out = os.path.join(group, "index.html")
        self.templates = [self.group, self.kind]

        self.pages = []
        self.items = []


class CategoryItem:
    def __init__(self, category, value):
        self.category = category
        self.value = value
        self.kind = "item"

        self.out = os.path.join(category.group, value)
        self.templates = [self.value, self.kind, self.category.name]

    @property
    def pages(self):
        for page in self.category.pages:
            if self.value in page.metadata.get(self.category.group):
                yield page


class Page:
    def __init__(self, _file, section, reader, settings):
        self.content, self.metadata = reader.read(_file)
        self.is_index = False
        self.kind = "page"
        self.settings = settings

        self.section = section
        path, _ = os.path.splitext(_file)
        self.name = os.path.basename(path)

        self.templates = [self.metadata.get("template"), self.kind]

    @property
    def nextin_section(self):
        try:
            loc = self.section.sorted.index(self)
            return self.section.sorted[loc + 1]

        except IndexError:
            return None

    @property
    def previn_section(self):
        loc = self.section.sorted.index(self)
        prev = self.section.sorted[loc - 1] if loc else None

        return prev

    @property
    def out(self):
        if self.section.name in self.settings.url_format.keys():
            template = self.settings.url_format[self.section.name]
        else:
            template = self.settings.url_format["_default"]

        args = {self.kind: self}
        return Template(template).render(args)

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
