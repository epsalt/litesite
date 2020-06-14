"""Command line entry points."""

import argparse
import sys

import yaml

from litesite.builder import build_site, render_site


def parse_args(args):
    """Argument parser for CLI entry point."""

    parser = argparse.ArgumentParser(
        description="Litesite is a little static site generator."
    )

    parser.add_argument(
        "config", type=argparse.FileType("r"), help="Configuration YAML file location."
    )

    return parser.parse_args(args)


def main():
    """Load YAML settings, then build and render the site."""

    parser = parse_args(sys.argv[1:])
    settings = yaml.load(parser.config, Loader=yaml.SafeLoader)
    site = build_site(settings)
    render_site(site)


if __name__ == """__main__""":
    main()
