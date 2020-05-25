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
        name = os.path.basename(rel)
        section = content.Section(name, rel, parent)

        for _file in files:
            page = self._build_page(path, _file, section)

            if page.is_index:
                section.index = page
            else:
                section.pages.append(page)

        return section

    def _build_page(self, path, _file, section):
        fname = os.path.join(path, _file)
        name = os.path.basename(os.path.splitext(_file)[0])
        text, metadata = self.reader.read(fname)

        page = content.Page(name, text, metadata, section)

        ## Set custom URLs
        if section.name in self.settings["url_format"].keys():
            page.url = self._urlify(page, section)

        return page

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

    def _urlify(self, page, section):
        template = self.settings["url_format"][section.name]
        args = {page.kind: page}

        url = self.renderer.render_from_string(template, args)

        return url

    @property
    def pages(self):
        sections = [self.top]
        while sections:
            section = sections.pop()
            sections += section.subsections
            yield from section.all_pages
