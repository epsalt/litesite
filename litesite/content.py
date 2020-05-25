import os

from dateutil.parser import parse


class Section:
    def __init__(self, rel, parent):
        self.name = os.path.basename(rel)
        self.kind = "section"
        self.parent = parent
        self.rel = rel

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
    def __init__(self, name, group):
        self.name = name
        self.group = group
        self.kind = "category"

        self.pages = []
        self.items = []

        self.url = os.path.join(group, "index.html")
        self.templates = [self.group, self.kind]


class CategoryItem:
    def __init__(self, category, value):
        self.value = value
        self.kind = "item"
        self.category = category

        self.url = os.path.join(category.group, value)
        self.templates = [self.value, self.kind, self.category.name]

    @property
    def pages(self):
        for page in self.category.pages:
            if self.value in page.metadata.get(self.category.group):
                yield page


class Page:
    def __init__(self, _file, section, reader, renderer, settings):
        self.name = os.path.basename(os.path.splitext(_file)[0])
        self.content, self.metadata = reader.read(_file)
        self.kind = "page"
        self.section = section
        self.is_index = _file == "index.md"

        if self.metadata.get("date"):
            self.metadata["date"] = parse(self.metadata["date"])

        self.url = self.urlify(section, settings, renderer)
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

    def urlify(self, section, settings, renderer):
        if section.name in settings["url_format"].keys():
            string = settings["url_format"][section.name]
        else:
            string = settings["url_format"]["_default"]

        args = {self.kind: self}
        return renderer.render_from_string(string, args)
