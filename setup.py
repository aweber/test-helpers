#!/usr/bin/env python
import sys

from setuptools import setup, find_packages

if sys.version_info < (2, 6):
    raise Exception("This package requires Python 2.6 or higher.")

install_requires = ['fake_servers', 'remembrall', 'tornado>=3.1']

if sys.version_info < (3, 2):
    install_requires.append('mock')

if sys.version_info < (2, 7):
    install_requires.append('unittest2')


def read_release_version():
    """Read the version from the file ``RELEASE-VERSION``."""
    with open("RELEASE-VERSION", "r") as f:
        return f.readline().strip()

setup(
    name='test-helpers',
    description='A collection of test helpers to consolidate common patterns',
    packages=find_packages(
        exclude=['fabfile', 'fabfile.*', 'tests', 'tests.*'],
    ),
    test_suite='nose.collector',
    include_package_data=True,
    zip_safe=False,
    install_requires=install_requires,
    long_description='''
        A collection of test helpers to consolidate common patterns.
    ''',
    dependency_links=['http://pypi.colo.lair/simple/'],
    version=read_release_version(),
    author='AWeber Communications',
    author_email='packages@aweber.com',
    entry_points={
        'console_scripts': [
        ],
    }
)
