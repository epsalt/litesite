"""Site level config reading and publishing"""

import yaml

from litesite.builder import SiteBuilder
from litesite.content import Site


def publish(config):
    with open(config, "r") as stream:
        settings = yaml.safe_load(stream)

    site = Site(settings)
    builder = SiteBuilder(site)

    builder.build_site()
    builder.render_site()

    return site
