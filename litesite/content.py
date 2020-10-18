"""Data structures for site content."""

import datetime

from cached_property import cached_property
from dateutil.parser import parse

from litesite.renderers import Renderer


class Site:
    """Top level data structure containing all content.

    The site is populated using the `build_site` function from
    `builder.py`.

    """

    def __init__(self, settings):
        self.settings = settings
        self.build_time = datetime.datetime.now(datetime.timezone.utc)

        self.top = None
        self.categories = []

    @property
    def sections(self):
        """Yields all sections defined in the site."""

        sections = [self.top]
        while sections:
            section = sections.pop()
            sections += section.subsections

            yield section

    @property
    def pages(self):
        """Yields all pages defined in the site."""

        for section in self.sections:
            yield from section.all_pages


class Section:
    """Hierarchical container for pages and other sections.

    Sections are defined based on the content directory tree. They can
    contain other sections (subsections) and pages.

    """

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
        """Return non-index pages sorted in date, title order."""

        default_keys = ("date", "title")
        key = lambda page: tuple(page.metadata[k] for k in default_keys)
        return sorted(self.pages, key=key)

    @property
    def all_pages(self):
        """Return all section pages and the index page if it exists."""

        if self.index:
            return self.pages + [self.index]

        return self.pages


class Category:
    """A key-value pair associated with some number of pages.

    Categories must be defined in the site configuration file to be
    found during site build. Defined categories (keys) and category
    items (values) can then be specified in page metadata.

    For example to define a "tags" category with "tag" category items
    name:

    ## config.yaml
    categories:
      tags: tag

    ## page.md metadata
    tags: a_tag
          b_tag

    """

    def __init__(self, name, item_name):
        self.name = name
        self.item_name = item_name

        self.pages = []
        self.items = []

        self.templates = [self.name, "category"]

    @cached_property
    def url(self):
        """Return the category URL."""

        template = "{{ category.name }}/{{ category.item_name }}"
        args = {"category": self}
        return Renderer.render_from_string(template, args)


class CategoryItem:
    """A value associated with a category key."""

    def __init__(self, category, value):
        self.value = value
        self.category = category

        self.templates = [self.value, "item", self.category.item_name]

    @cached_property
    def url(self):
        """Return the category item URL."""

        template = "{{ item.category.name }}/{{ item.value }}"
        args = {"item": self}
        return Renderer.render_from_string(template, args)

    @property
    def pages(self):
        """Yield all pages with this category item."""

        for page in self.category.pages:
            if self.value in page.metadata.get(self.category.name):
                yield page

    @property
    def sorted(self):
        """Return pages sorted in date, title order."""

        default_keys = ("date", "title")
        key = lambda page: tuple(page.metadata[k] for k in default_keys)
        return sorted(self.pages, key=key)


class Page:
    """An individual text document corresponding to a file in the content directory.

    Pages are read from files during the site build. Each page is a
    member of a section.

    """

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
        """Return the page URL.

        Page URLs can be overridden in the site config by specifying a
        URL override template for the section.

        """

        if self.section.override:
            template = self.section.override
        else:
            template = "{{ page.section.rel }}/{{ page|slug }}"

        args = {"page": self}
        return Renderer.render_from_string(template, args)

    @property
    def next(self):
        """Return the next page in the section in date, title order."""

        try:
            loc = self.section.sorted.index(self)
            return self.section.sorted[loc + 1]

        except IndexError:
            return None

    @property
    def prev(self):
        """Return the previous page in the section in date, title order."""

        loc = self.section.sorted.index(self)
        prev = self.section.sorted[loc - 1] if loc else None

        return prev
