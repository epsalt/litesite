from urllib.parse import urljoin

from dateutil.parser import parse
from jinja2 import contextfilter


def datetime(string):
    return parse(string)


def isoformat(dt):
    return dt.isoformat()


def slug(page):
    return page.metadata["slug"]


def date(page, fmt):
    return page.metadata["date"].strftime(fmt)


@contextfilter
def permalink(context, url):
    if context.vars.get("settings"):
        return urljoin(context.vars["settings"]["base"], url)

    return None


filters = {
    "date": date,
    "datetime": datetime,
    "isoformat": isoformat,
    "permalink": permalink,
    "slug": slug,
}
