import yaml


class Settings:
    def __init__(self, config):
        with open(config, "r") as stream:
            self.config = yaml.safe_load(stream)

        self.base = self.config["site"]["base_url"]
        self.title = self.config["site"]["title"]
        self.author = self.config["site"]["author"]
        self.email = self.config["site"]["email"]
        self.description = self.config["site"]["description"]

        self.content = self.config["content"]["root"]
        self.site = self.config["content"]["destination"]
        self.templates = self.config["content"]["templates"]

        self.url_format = self.config["url_format"]
        self.categories = self.config["categories"]
