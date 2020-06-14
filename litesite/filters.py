"""Custom filters for jinja2 templates.

New custom filters have to be registered in the `filters` dict before
they are available during template rendering.

"""

from urllib.parse import urljoin

from bs4 import BeautifulSoup
from dateutil.parser import parse


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


def canonify(url, base):
    """Convert a relative link to absolute."""

    return urljoin(base, url)


def canonify_media(content, base):
    """Convert all img and video tag src links to absolute."""

    soup = BeautifulSoup(content, features="html.parser")
    for media in ["img", "video"]:
        for element in soup.findAll(media):
            element["src"] = canonify(element["src"], base)

    return str(soup)


filters = {
    "canonify": canonify,
    "canonify_media": canonify_media,
    "date": date,
    "datetime": datetime,
    "isoformat": isoformat,
    "slug": slug,
}
