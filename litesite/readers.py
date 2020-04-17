"""File readers"""
import markdown


class Reader:
    def __init__(self, site):
        self.site = site
        self.reader = Markdown

    def read(self, _file):
        args = {"site": self.site}

        with open(_file, "r") as f:
            text = self.site.renderer.render_string(f.read(), args)

        return self.reader(text)


class Markdown:
    def __init__(self, text):
        self.extensions = [
            "markdown.extensions.extra",
            "markdown.extensions.smarty",
            "markdown.extensions.codehilite",
            "full_yaml_metadata",
        ]

        md = markdown.Markdown(extensions=self.extensions)

        self.content = md.convert(text)
        self.meta = md.Meta
