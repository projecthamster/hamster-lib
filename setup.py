#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Packaging instruction for setup tools."""


try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup


with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read().replace('.. :changelog:', '')

requirements = [
    'appdirs',
    'future',
    'sqlalchemy',
    'icalendar',
    'six',
    'configparser >= 3.5.0b2',
]

setup(
    name='hamster-lib',
    version='0.13.1',
    description="A library for common timetracking functionality.",
    long_description=readme + '\n\n' + history,
    author="Eric Goller",
    author_email='eric.goller@ninjaduck.solutions',
    url='https://github.com/projecthamster/hamster-lib',
    packages=find_packages(),
    install_requires=requirements,
    license="GPL3",
    zip_safe=False,
    keywords='hamster-lib',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
    ],
)
