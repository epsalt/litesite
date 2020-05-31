"""Site level config reading and publishing"""

import yaml

from litesite.builder import Builder


def publish(config):
    with open(config, "r") as stream:
        settings = yaml.safe_load(stream)

    builder = Builder(settings)
    builder.build_site()
    builder.render_site()
