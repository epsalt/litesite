import itertools
import os
from urllib.parse import urljoin

from dateutil.parser import parse
from jinja2 import Environment, FileSystemLoader


class ContentRenderer:
    def __init__(self, settings):
        loader = FileSystemLoader(settings["templates"])
        self.env = Environment(loader=loader, trim_blocks=True, lstrip_blocks=True)
        self.env.filters["datetime"] = parse
        self.env.filters["isoformat"] = lambda dt: dt.isoformat()
        self.env.filters["permalink"] = lambda s: urljoin(settings["base"], s)

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

    def render_from_string(self, string, args=None):
        template = self.env.from_string(string)
        text = template.render(**args) if args else template.render()

        return text


class URLRenderer:
    def __init__(self, template, args):
        self.template = template
        self.args = args

        self.env = Environment()
        self.env.filters["slug"] = lambda page: page.metadata["slug"]
        self.env.filters["date"] = self._datetimeformat

    @property
    def url(self):
        template = self.env.from_string(self.template)
        text = template.render(self.args)

        return text

    @staticmethod
    def _slug(page):
        return page.metadata["slug"]

    @staticmethod
    def _datetimeformat(page, _format):
        return page.metadata["date"].strftime(_format)
