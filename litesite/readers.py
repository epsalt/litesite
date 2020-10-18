"""Content file readers.

Currently only markdown is supported.

"""

import markdown


class Reader:
    """Initialize a markdown file reader and extensions."""

    def __init__(self, user_extensions=None):
        extensions = [
            "markdown.extensions.extra",
            "markdown.extensions.smarty",
            "markdown.extensions.codehilite",
            "full_yaml_metadata",
        ]

        if user_extensions:
            extensions += user_extensions

        self.md = markdown.Markdown(extensions=extensions)

    def read(self, text):
        """Read a markdown file and YAML metadata."""

        content = self.md.convert(text)
        meta = self.md.Meta

        return content, meta
