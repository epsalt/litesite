"""Markdown file reader"""
from jinja2 import Environment, Template
import markdown

from litesite.renderers import ContentRenderer


class Reader:
    def __init__(self, settings):
        extensions = [
            "markdown.extensions.extra",
            "markdown.extensions.smarty",
            "markdown.extensions.codehilite",
            "full_yaml_metadata",
        ]

        self.md = markdown.Markdown(extensions=extensions)
        self.renderer = ContentRenderer(settings)

    def preprocess(self, _file):
        with open(_file, "r") as f:
            string = f.read()

        text = self.renderer.render_from_string(string)
        return text

    def read(self, _file):
        text = self.preprocess(_file)
        content = self.md.convert(text)
        meta = self.md.Meta

        return content, meta
