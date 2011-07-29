#!/usr/bin/env python
import sys

from setuptools import setup, find_packages

from version import get_git_version

if sys.version_info < (2, 6):
    raise Exception("This package requires Python 2.6 or higher.")

setup(
    name = 'baseservice',
    description = 'A git repo scaffold for new projects',
    packages = find_packages(),
    include_package_data = True,
    zip_safe = False,
    install_requires = [
    ],
    long_description = '''A git repo scaffold for new projects''',
    dependency_links=['https://nebula.ofc.lair/python-dist/'],
    version = get_git_version(use_tags=True),
    author = 'AWeber Communications',
    author_email = '@aweber.com',
    entry_points = {
        'console_scripts': [
        ],
    }
)
