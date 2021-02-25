#!/usr/bin/env python
from codecs import open
from setuptools import setup

README = open("README.md").read()

setup(
    name="dirmaker",
    version="0.1.0",
    description="A simple static site generator for generating directory websites.",
    long_description=README,
    long_description_content_type="text/markdown",
    author="Kailash Nadh",
    author_email="kailash@nadh.in",
    url="https://github.com/knadh/dirmaker",
    packages=['dirmaker'],
    include_package_data=True,
    download_url="https://github.com/knadh/dirmaker",
    license="MIT License",
    entry_points={
        'console_scripts': [
            'dirmaker = dirmaker:main'
        ],
    },
    classifiers=[
        "Topic :: Text Editors :: Text Processing",
        "Topic :: Internet :: WWW/HTTP :: Site Management",
        "Topic :: Documentation"
    ],
    install_required=["jinja2"],
)
