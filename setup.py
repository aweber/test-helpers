#!/usr/bin/env python
import sys

from setuptools import setup, find_packages


if sys.version_info < (2, 6):
    raise Exception("This package requires Python 2.6 or higher.")


def read_release_version():
    """Read the version from the file ``RELEASE-VERSION``"""
    with open("RELEASE-VERSION", "r") as f:
        version = f.readlines()[0]
        return version.strip()


setup(
    name = '@@baseservice@@',
    description = 'A git repo scaffold for new projects',
    packages = find_packages(),
    include_package_data = True,
    zip_safe = False,
    install_requires = [
    ],
    long_description = '''A git repo scaffold for new projects''',
    dependency_links=['https://nebula.ofc.lair/python-dist/'],
    version = read_release_version(),
    author = 'AWeber Communications',
    author_email = '@aweber.com',
    entry_points = {
        'console_scripts': [
        ],
    }
)
