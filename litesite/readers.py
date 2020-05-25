"""Markdown file reader"""
from jinja2 import Environment, Template
import markdown

from renderers import Renderer


class Reader:
    def __init__(self, site, settings):
        extensions = [
            "markdown.extensions.extra",
            "markdown.extensions.smarty",
            "markdown.extensions.codehilite",
            "full_yaml_metadata",
        ]

        self.site = site
        self.md = markdown.Markdown(extensions=extensions)
        self.renderer = Renderer(site, settings)

    def preprocess(self, _file):
        args = {"site": self.site}
        with open(_file, "r") as f:
            string = f.read()

        text = self.renderer.render_from_string(string, args)
        return text

    def read(self, _file):
        text = self.preprocess(_file)
        content = self.md.convert(text)
        meta = self.md.Meta

        return content, meta
