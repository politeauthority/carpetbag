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

from distutils.core import setup
setup(
    name='CarpetBag',
    version='0.0.1',
    packages=['carpetbag'],
    author="""politeauthority""",
    description="Scraper that wont take no for an answer",
    url="https://github.com/politeauthority/carpetbag")
