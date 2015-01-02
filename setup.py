#!/usr/bin/env python
import codecs

from setuptools import setup, find_packages
import test_helpers


def read_requirements_file(filename):
    """Read pip-formatted requirements from a file."""
    with open(filename, 'r') as f:
        return [
            line.strip() for line in f.readlines()
            if not line.startswith('#')
        ]

setup(
    name='test-helpers',
    description='A collection of test helpers to facilitate AAA testing.',
    packages=find_packages(exclude=['tests', 'tests.*']),
    test_suite='nose.collector',
    include_package_data=True,
    zip_safe=False,
    long_description=codecs.open('README.rst', encoding='utf-8').read(),
    install_requires=read_requirements_file('requirements.txt'),
    tests_require=read_requirements_file('dev-requirements.txt'),
    version=test_helpers.__version__,
    author='AWeber Communications',
    author_email='api@aweber.com',
    entry_points={'console_scripts': []},
    extras_require={
        'tornado': ['tornado>=3.1'],
        'rabbit': ['requests>=2.3'],
        'postgres': ['psycopg2>=2.5,<3.0'],
        'mongo': ['pymongo>=2.7,<2.8']
    },
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: Implementation :: CPython',
    ],
)
