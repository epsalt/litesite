from dateutil.parser import parse


class Section:
    def __init__(self, name, rel, parent):
        self.name = name
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

        self.url = f"{self.group}/{self.name}"
        self.templates = [self.group, self.kind]


class CategoryItem:
    def __init__(self, category, value):
        self.value = value
        self.kind = "item"
        self.category = category

        self.url = f"{self.category.name}/{self.value}"
        self.templates = [self.value, self.kind, self.category.name]

    @property
    def pages(self):
        for page in self.category.pages:
            if self.value in page.metadata.get(self.category.group):
                yield page


class Page:
    def __init__(self, name, content, metadata, section):
        self.name = name
        self.content = content
        self.metadata = metadata
        self.kind = "page"
        self.section = section
        self.is_index = name == "_index"

        self.url = f"{self.section.rel}/{self.metadata['slug']}"
        self.templates = [self.metadata.get("template"), self.kind]

        if self.metadata.get("date"):
            metadata["date"] = parse(metadata["date"])

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
