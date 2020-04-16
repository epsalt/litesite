import datetime
import email
import itertools
import os

from bs4 import BeautifulSoup
from dateutil.parser import parse
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
        directory = self.site.templates
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
    @classmethod
    def render_template(cls, directory, templates, args):
        loader = FileSystemLoader(directory)
        env = Environment(loader=loader, auto_reload=True)
        env.filters["pubdate"] = cls.pubdate
        env.filters["rfc3339"] = cls.rfc3339

        template = env.select_template(templates)
        text = template.render(**args)

        return text

    @staticmethod
    def render_string(template, args):
        return Template(template).render(args)

    @staticmethod
    def pubdate(dt):
        return email.utils.formatdate(dt.timestamp(), usegmt=True)

    @staticmethod
    def rfc3339(dt):
        if not isinstance(dt, datetime.datetime):
            dt = parse(dt)

        return dt.isoformat()
