"""Site level config reading and publishing"""
import os

import content
import settings


def publish(config):
    sets = settings.Settings(config)
    site = content.Site(sets)
    os.makedirs(sets.site, exist_ok=True)

    render(site)


def render(site):
    for page in site.pages:
        print(f"name: {page.name}, section: {page.section.name}, rel: {page.rel}")
        page.render(site)

    for category in site.categories:
        print(f"name: {category.name}, rel: {category.rel}")
        category.render(site)

        for item in category.items:
            print(f"name: {item.value}, rel: {item.rel}")
            item.render(site)
