"""Site level config reading and publishing"""
import os

import yaml

from content import Site
import renderers


def publish(config):
    with open(config, "r") as stream:
        settings = yaml.safe_load(stream)

    site = Site(settings)
    render(site, settings)


def render(site, settings):
    os.makedirs(settings["site"], exist_ok=True)
    renderer = renderers.Renderer(site, settings)

    for page in site.pages:
        print(f"name: {page.name}, section: {page.section.name}")
        renderer.render(page, page.url, page.templates)

    for category in site.categories:
        print(f"name: {category.name}")
        renderer.render(category, category.url, category.templates)

        for item in category.items:
            print(f"name: {item.value}")
            renderer.render(item, item.url, item.templates)
