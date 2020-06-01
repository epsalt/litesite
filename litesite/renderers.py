import itertools
import os

from jinja2 import Environment, FileSystemLoader

from litesite.filters import filters


class Renderer:
    def __init__(self, settings):

        self.env = Environment()
        self.env.filters.update(filters)

        loader = FileSystemLoader(settings["templates"])
        self.env.loader = loader

    def render(self, out, templates, args):
        template = self.lookup(templates)
        text = template.render(**args)

        os.makedirs(os.path.dirname(out), exist_ok=True)
        with open(out, "w") as _file:
            _file.write(text)

        return text

    def lookup(self, files):
        exts = [".html", ".xml"]

        templates = []
        for f, ext in itertools.product(files, exts):
            if f is not None:
                templates.append(str(f) + ext)

        return self.env.select_template(templates)

    @staticmethod
    def render_from_string(string, args=None):
        env = Environment()
        env.filters.update(filters)

        template = env.from_string(string)
        text = template.render(**args) if args else template.render()

        return text
