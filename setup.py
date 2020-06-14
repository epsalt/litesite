from setuptools import setup, find_packages

setup(
    name="litesite",
    version="1.0",
    packages=find_packages(),
    entry_points={"console_scripts": "litesite = litesite.cli:main"},
)
