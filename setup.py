#!/usr/bin/env python
"""
Builds packages so that each package can be imported (and allow relative imports)

"""


import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="CarpetBag",
    version="0.0.1",
    packages=["carpetbag"],
    author="politeauthority",
    description="A python scraper that wont take no for an answer",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/politeauthority/carpetbag",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
