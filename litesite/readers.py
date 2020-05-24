"""Markdown file reader"""
from jinja2 import Template
import markdown


class Reader:
    def __init__(self, site):
        extensions = [
            "markdown.extensions.extra",
            "markdown.extensions.smarty",
            "markdown.extensions.codehilite",
            "full_yaml_metadata",
        ]

        self.site = site
        self.md = markdown.Markdown(extensions=extensions)

    def preprocess(self, _file):
        args = {"site": self.site}
        with open(_file, "r") as f:
            text = Template(f.read()).render(args)

        return text

    def read(self, _file):
        text = self.preprocess(_file)
        content = self.md.convert(text)
        meta = self.md.Meta

        return content, meta
