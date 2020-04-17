"""Site level config reading and publishing"""
import os

import content


def publish(config):
    site = content.Site(config)

    if not os.path.exists(site.site):
        os.makedirs(site.site)

    render(site)


def render(site):
    for page in site.pages:
        print(f"name: {page.name}, section: {page.section.name}, rel: {page.rel}")
        page.render()

    for category in site.categories:
        print(f"name: {category.name}, rel: {category.rel}")
        category.render()

        for item in category.items:
            print(f"name: {item.value}, rel: {item.rel}")
            item.render()
