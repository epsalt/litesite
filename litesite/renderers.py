import itertools
import os

from bs4 import BeautifulSoup
from jinja2 import Environment, FileSystemLoader, Template


class Renderer:
    def __init__(self, site):
        self.site = site

        backends = {"jinja": Jinja}
        try:
            self.backend = site.config["content"]["renderer"]
        except LookupError as err:
            raise LookupError("Renderer backend not set in config") from err

        self.renderer = backends.get(self.backend)

        if self.renderer is None:
            raise KeyError("Backend not implemented {}".format(self.backend))

    def render(self, obj, out, names, pretty=True):
        directory = self.site.config["content"]["templates"]
        templates = self.lookup(names)

        if not os.path.exists(os.path.dirname(out)):
            os.makedirs(os.path.dirname(out))

        args = {obj.kind: obj, "site": self.site}
        text = self.renderer.render_template(directory, templates, args)

        if pretty:
            text = BeautifulSoup(text, "html.parser").prettify(formatter="html5")

        with open(out, "w") as _file:
            _file.write(text)

    def render_string(self, template, args):
        return self.renderer.render_string(template, args)

    @staticmethod
    def lookup(files):
        exts = [".html", ".html.jinja", ".xml", ".xml.jinja"]
        templates = [
            str(f) + ext for f, ext in itertools.product(files, exts) if f is not None
        ]

        return templates


class Jinja:
    @staticmethod
    def render_template(directory, templates, args):
        loader = FileSystemLoader(directory)
        env = Environment(loader=loader, auto_reload=True)

        template = env.select_template(templates)
        text = template.render(**args)

        return text

    @staticmethod
    def render_string(template, args):
        return Template(template).render(args)
