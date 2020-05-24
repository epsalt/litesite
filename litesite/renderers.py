import itertools
import os

from dateutil.parser import parse
from jinja2 import Environment, FileSystemLoader
from urllib.parse import urljoin


class Renderer:
    def __init__(self, site, settings):
        self.site = site
        self.settings = settings

        loader = FileSystemLoader(settings.templates)
        self.env = Environment(loader=loader, trim_blocks=True, lstrip_blocks=True)
        self.env.filters["datetime"] = parse
        self.env.filters["isoformat"] = lambda dt: dt.isoformat()
        self.env.filters["permalink"] = lambda s: urljoin(self.settings.base, s)

    def render(self, obj, out, files):
        template = self.lookup(files)
        args = {obj.kind: obj, "site": self.site, "settings": self.settings}
        text = template.render(**args)

        out = os.path.join(self.settings.site, out)
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
