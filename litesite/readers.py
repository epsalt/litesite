"""Markdown file reader"""
import markdown


class Reader:
    def __init__(self):
        extensions = [
            "markdown.extensions.extra",
            "markdown.extensions.smarty",
            "markdown.extensions.codehilite",
            "full_yaml_metadata",
        ]

        self.md = markdown.Markdown(extensions=extensions)

    def read(self, text):
        content = self.md.convert(text)
        meta = self.md.Meta

        return content, meta
