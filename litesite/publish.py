"""Site level config reading and publishing"""
import os

import yaml

from litesite.builder import build_site
from litesite.renderers import ContentRenderer


def publish(config):
    with open(config, "r") as stream:
        settings = yaml.safe_load(stream)

    site = build_site(settings)
    render(site, settings)


def render(site, settings):
    dest = settings["site"]

    os.makedirs(dest, exist_ok=True)
    renderer = ContentRenderer(settings)

    for page in site.pages:
        print(f"name: {page.name}, section: {page.section.name}")

        out = os.path.join(dest, page.url)
        args = {"page": page, "site": site, "settings": settings}
        renderer.render(out, page.templates, args)

    for category in site.categories:
        print(f"name: {category.name}")

        out = os.path.join(dest, category.url)
        args = {"category": category, "site": site, "settings": settings}
        renderer.render(out, category.templates, args)

        for item in category.items:
            print(f"name: {item.value}")

            out = os.path.join(dest, item.url)
            args = {"item": item, "site": site, "settings": settings}
            renderer.render(out, item.templates, args)
