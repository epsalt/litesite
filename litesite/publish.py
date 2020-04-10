"""Site level config reading and publishing"""
import datetime
import logging
import os
import yaml

from dirsync import sync

import content
import readers
import renderers


class Site:
    def __init__(self, config):
        with open(config, "r") as stream:
            self.config = yaml.safe_load(stream)

        self.content_root = self.config["content"]["root"]
        self.site_dest = self.config["site"]["destination"]
        self.base_url = self.config["site"]["base_url"]
        self.build_time = datetime.datetime.now()

        self.reader = readers.Reader(self)
        self.renderer = renderers.Renderer(self)
        self.static = self.config["content"]["static"]

        self.top = self.walk()
        self.sections = self.top.subsections

        self.categories = []
        for group, name in self.config["categories"].items():
            category = content.Category(name, group, self)
            self.categories.append(category)

    def walk(self):
        walker = os.walk(self.content_root)
        queue = []
        parent = None

        for path, dirs, files in walker:
            if queue:
                parent = queue.pop()

            section = content.Section(path, files, parent, self)

            for _dir in dirs:
                queue.append(section)

            if parent:
                parent.subsections.append(section)
            else:
                top = section

        return top

    def publish(self):
        if not os.path.exists(self.site):
            os.makedirs(self.site)

        logging.getLogger("dirsync").addHandler(logging.NullHandler())
        sync(self.static, self.site, "sync")

        for page in self.pages:
            print(f"name: {page.name}, section: {page.section.name}, rel: {page.rel}")
            page.render()

        for category in self.categories:
            print(f"name: {category.name}, rel: {category.rel}")
            category.render()

            for item in category.items:
                print(f"name: {item.value}, rel: {item.rel}")
                item.render()

    @property
    def pages(self):
        sections = [self.top]
        while sections:
            section = sections.pop()
            sections += section.subsections
            yield from section.all_pages
