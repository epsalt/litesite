from setuptools import setup, find_packages

requires = [
    "beautifulsoup4",
    "cached-property",
    "Jinja2",
    "markdown-full-yaml-metadata",
    "Markdown",
    "PyYAML",
    "pygments",
    "python-dateutil",
]


setup(
    name="litesite",
    version="1.0",
    packages=find_packages(),
    entry_points={"console_scripts": "litesite = litesite.cli:main"},
    install_requires=requires,
)
