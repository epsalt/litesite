"""Custom filters for jinja2 templates.

New custom filters have to be registered in the `filters` dict before
they are available during template rendering.

"""

from urllib.parse import urljoin

from dateutil.parser import parse
from jinja2 import contextfilter


def datetime(string):
    """Parse a date or datetime string with dateutil.parse"""

    return parse(string)


def isoformat(dt):
    """Convert a datetime to ISO 8601 string format.

    This filter can be chained with the datetime filter to convert
    datetime strings to ISO 8601 for RSS feed generation.

    """

    return dt.isoformat()


def slug(page):
    """Returns the slug from page metadata.

    This filter helps to keep custom URL templates short.

    """
    return page.metadata["slug"]


def date(page, fmt):
    """Page date formatter."""

    return page.metadata["date"].strftime(fmt)


@contextfilter
def permalink(context, url):
    """Join URL with site basename."""

    if context.get("settings"):
        base = context["settings"]["base"]
        return urljoin(base, url)

    return None


filters = {
    "date": date,
    "datetime": datetime,
    "isoformat": isoformat,
    "permalink": permalink,
    "slug": slug,
}
