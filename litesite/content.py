import datetime

from cached_property import cached_property
from dateutil.parser import parse

from litesite.renderers import Renderer


class Site:
    def __init__(self, settings):
        self.settings = settings
        self.build_time = datetime.datetime.now(datetime.timezone.utc)

        self.top = None
        self.categories = []

    @property
    def sections(self):
        sections = [self.top]

        while sections:
            section = sections.pop()
            sections += section.subsections

            yield section

    @property
    def pages(self):
        for section in self.sections:
            yield from section.all_pages


class Section:
    def __init__(self, name, rel, parent, override):
        self.name = name
        self.parent = parent
        self.rel = rel
        self.override = override

        self.index = None
        self.subsections = []
        self.pages = []

    @property
    def sorted(self):
        default_keys = ("date", "title")
        key = lambda page: tuple(page.metadata[k] for k in default_keys)
        return sorted(self.pages, key=key)

    @property
    def all_pages(self):
        if self.index:
            return self.pages + [self.index]

        return self.pages


class Category:
    def __init__(self, name, item_name):
        self.name = name
        self.item_name = item_name

        self.pages = []
        self.items = []

        self.templates = [self.name, "category"]

    @cached_property
    def url(self):
        template = "{{ category.name }}/{{ category.item_name }}"
        args = {"category": self}
        return Renderer.render_from_string(template, args)


class CategoryItem:
    def __init__(self, category, value):
        self.value = value
        self.category = category

        self.templates = [self.value, "item", self.category.item_name]

    @cached_property
    def url(self):
        template = "{{ item.category.name }}/{{ item.value }}"
        args = {"item": self}
        return Renderer.render_from_string(template, args)

    @property
    def pages(self):
        for page in self.category.pages:
            if self.value in page.metadata.get(self.category.name):
                yield page


class Page:
    def __init__(self, name, content, metadata, section):
        self.name = name
        self.content = content
        self.metadata = metadata
        self.section = section
        self.is_index = name == "_index"

        self.templates = [self.metadata.get("template"), "page"]

        if self.metadata.get("date"):
            try:
                self.metadata["date"] = parse(self.metadata.get("date"))
            except TypeError:

                pass

    @cached_property
    def url(self):
        if self.section.override:
            template = self.section.override
        else:
            template = "{{ page.section.rel }}/{{ page|slug }}"

        args = {"page": self}
        return Renderer.render_from_string(template, args)

    @property
    def next(self):
        try:
            loc = self.section.sorted.index(self)
            return self.section.sorted[loc + 1]

        except IndexError:
            return None

    @property
    def prev(self):
        loc = self.section.sorted.index(self)
        prev = self.section.sorted[loc - 1] if loc else None

        return prev
