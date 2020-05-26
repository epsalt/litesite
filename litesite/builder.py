import os

import content


def load_content(site):
    walker = os.walk(site.settings["content"])
    queue = []
    parent = None

    for path, dirs, files in walker:
        if queue:
            parent = queue.pop()

        section = build_section(path, files, parent, site)

        for _dir in dirs:
            queue.append(section)

        if parent:
            parent.subsections.append(section)
        else:
            top = section

    return top


def build_section(path, files, parent, site):
    rel = os.path.relpath(path, site.settings["content"])
    name = os.path.basename(rel)
    section = content.Section(name, rel, parent)

    for _file in files:
        page = build_page(path, _file, section, site)

        if page.is_index:
            section.index = page
        else:
            section.pages.append(page)

    return section


def build_page(path, _file, section, site):
    fname = os.path.join(path, _file)
    name = os.path.basename(os.path.splitext(_file)[0])
    text, metadata = site.reader.read(fname)

    page = content.Page(name, text, metadata, section)

    ## Set custom URLs
    if section.name in site.settings["url_format"].keys():
        template = site.settings["url_format"][section.name]
        args = {page.kind: page}
        page.url = site.renderer.render_from_string(template, args)

    return page


def load_categories(site):
    for group, name in site.settings["categories"].items():
        category = content.Category(name, group)
        for page in site.pages:
            if page.metadata.get(group):
                category.pages.append(page)

        vals = set()
        for page in category.pages:
            for val in page.metadata.get(group):
                vals.add(val)

        category.items = [content.CategoryItem(category, val) for val in vals]
        yield category
