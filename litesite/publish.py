"""Site level config reading and publishing"""
import os

import content
import renderers
import settings


def publish(config):
    sets = settings.Settings(config)
    site = content.Site(sets)
    os.makedirs(sets.site, exist_ok=True)

    render(site, sets)


def render(site, sets):
    renderer = renderers.Renderer(site, sets)

    for page in site.pages:
        print(f"name: {page.name}, section: {page.section.name}")
        renderer.render(page, page.out, page.templates)

    for category in site.categories:
        print(f"name: {category.name}")
        renderer.render(category, category.out, category.templates)

        for item in category.items:
            print(f"name: {item.value}")
            renderer.render(item, item.out, item.templates)
