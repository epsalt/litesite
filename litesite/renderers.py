"""Template renderers.

Currently only jinja2 is supported. Custom filters available to the
renderer are loaded from `filters.py`. Template directory is defined
in the site config file. Nested template directories are not
supported.

"""

import itertools
import os

from jinja2 import Environment, FileSystemLoader

from litesite.filters import filters


class Renderer:
    """Class for jinja2 template lookup and rendering."""

    def __init__(self, settings):
        self.env = Environment()
        self.env.filters.update(filters)

        loader = FileSystemLoader(settings["templates"])
        self.env.loader = loader

    def render(self, out, templates, args):
        """Select the first available template and render to `out`."""

        template = self.lookup(templates)
        text = template.render(**args)

        os.makedirs(os.path.dirname(out), exist_ok=True)
        with open(out, "w") as _file:
            _file.write(text)

        return text

    def lookup(self, templates):
        """Lookup a template from the template directory.

        Templates are selected based on `templates` list
        order. Available templates extensions are `html` and
        `xml. `html` files take template selection precendence over
        `xml` files.

        """

        exts = [".html", ".xml"]

        template_files = []
        for f, ext in itertools.product(templates, exts):
            if f is not None:
                template_files.append(str(f) + ext)

        return self.env.select_template(template_files)

    @staticmethod
    def render_from_string(string, args=None):
        """Render a string template with access to custom filters."""

        env = Environment()
        env.filters.update(filters)

        template = env.from_string(string)
        text = template.render(**args) if args else template.render()

        return text
