import datetime
import os

import content
import readers
import renderers


class Site:
    def __init__(self, settings):

        self.reader = readers.Reader(self, settings)
        self.renderer = renderers.Renderer(self, settings)
        self.settings = settings
        self.build_time = datetime.datetime.now(datetime.timezone.utc)

        self.top = self._walk_content()
        self.sections = self.top.subsections

        self.categories = list(self._build_categories())

    def _walk_content(self):
        walker = os.walk(self.settings["content"])
        queue = []
        parent = None

        for path, dirs, files in walker:
            if queue:
                parent = queue.pop()

            section = self._build_section(path, files, parent)

            for _dir in dirs:
                queue.append(section)

            if parent:
                parent.subsections.append(section)
            else:
                top = section

        return top

    def _build_section(self, path, files, parent):
        rel = os.path.relpath(path, self.settings["content"])
        section = content.Section(rel, parent)

        for _file in files:
            fname = os.path.join(path, _file)
            page = content.Page(
                fname, section, self.reader, self.renderer, self.settings
            )

            if page.is_index:
                section.index = page
            else:
                section.pages.append(page)

        return section

    def _build_categories(self):
        for group, name in self.settings["categories"].items():
            category = content.Category(name, group)
            for page in self.pages:
                if page.metadata.get(group):
                    category.pages.append(page)

            vals = set()
            for page in category.pages:
                for val in page.metadata.get(group):
                    vals.add(val)

            category.items = [content.CategoryItem(category, val) for val in vals]

            yield category

    @property
    def pages(self):
        sections = [self.top]
        while sections:
            section = sections.pop()
            sections += section.subsections
            yield from section.all_pages
