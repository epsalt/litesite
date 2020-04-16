"""Site level config reading and publishing"""
import datetime
import logging
import os

import dirsync
import sass
import yaml

import content
import readers
import renderers


class Site:
    def __init__(self, config):
        with open(config, "r") as stream:
            self.config = yaml.safe_load(stream)

        self.content = self.config["content"]["root"]
        self.site = self.config["content"]["destination"]
        self.static = self.config["content"]["static"]
        self.templates = self.config["content"]["templates"]
        self.base = self.config["site"]["base_url"]

        self.build_time = datetime.datetime.now(datetime.timezone.utc)

        self.reader = readers.Reader(self)
        self.renderer = renderers.Renderer(self)

        self.top = self.walk()
        self.sections = self.top.subsections

        self.categories = []
        for group, name in self.config["categories"].items():
            category = content.Category(name, group, self)
            self.categories.append(category)

    def walk(self):
        walker = os.walk(self.content)
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

    def compile_style(
        self, out_dir="css", css_file="styles.min.css", map_file="styles.map"
    ):
        style = self.config["content"].get("style")

        if style:
            css_string, map_string = sass.compile(
                filename=style,
                output_style="compressed",
                source_map_filename=map_file,
                source_map_contents=True,
                source_map_embed=True,
            )
            out = os.path.join(self.site, out_dir)

            if not os.path.exists(os.path.dirname(out)):
                os.makedirs(os.path.dirname(out))

            with open(os.path.join(out, css_file), "w") as f:
                f.write(css_string)

            with open(os.path.join(out, map_file), "w") as f:
                f.write(map_string)

    def sync_static(self):
        logging.getLogger("dirsync").addHandler(logging.NullHandler())
        dirsync.sync(self.static, self.site, "sync")
        self.compile_style()

    def render(self):
        for page in self.pages:
            print(f"name: {page.name}, section: {page.section.name}, rel: {page.rel}")
            page.render()

        for category in self.categories:
            print(f"name: {category.name}, rel: {category.rel}")
            category.render()

            for item in category.items:
                print(f"name: {item.value}, rel: {item.rel}")
                item.render()

    def publish(self):
        if not os.path.exists(self.site):
            os.makedirs(self.site)

        self.sync_static()
        self.compile_style()
        self.render()

    @property
    def pages(self):
        sections = [self.top]
        while sections:
            section = sections.pop()
            sections += section.subsections
            yield from section.all_pages
