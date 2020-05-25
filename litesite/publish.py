"""Site level config reading and publishing"""
import os

import yaml

from _site import Site
import renderers


def publish(config):
    with open(config, "r") as stream:
        settings = yaml.safe_load(stream)

    site = Site(settings)
    os.makedirs(settings["site"], exist_ok=True)
    render(site, settings)


def render(site, sets):
    renderer = renderers.Renderer(site, sets)

    for page in site.pages:
        print(f"name: {page.name}, section: {page.section.name}")
        renderer.render(page, page.url, page.templates)

    for category in site.categories:
        print(f"name: {category.name}")
        renderer.render(category, category.url, category.templates)

        for item in category.items:
            print(f"name: {item.value}")
            renderer.render(item, item.url, item.templates)
