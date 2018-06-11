#!/usr/bin/env python
"""
Builds packages so that each package can be imported (and allow relative imports)

Usage:
    python setup.py build
    python setup.py install

Depending on whether there is a virtualenv, packages may be installed in a location like:
    /usr/local/lib/python2.7/dist-packages/
    /usr/local/lib/python2.7/site-packages/
"""
from setuptools import setup

setup(
    name='scrapy',
    version='0.0.1',
    description="Scraper that wont take no for an answer",
    author="""politeauthority""",
)
