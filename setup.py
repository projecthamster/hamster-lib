#!/usr/bin/env python
# -*- coding: utf-8 -*-


try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read().replace('.. :changelog:', '')

requirements = [
    'future', 'sqlalchemy',
]

test_requirements = [
    # TODO: put package test requirements here
]

setup(
    name='hamsterlib',
    version='0.0.2',
    description="A library for common timetracking functionality.",
    long_description=readme + '\n\n' + history,
    author="Eric Goller",
    author_email='Elbenfreund@DenkenInEchtzeit.net',
    url='https://github.com/elbenfreund/hamsterlib',
    packages=[
        'hamsterlib',
    ],
    package_dir={'hamsterlib':
                 'hamsterlib'},
    # include_package_data=True,
    install_requires=requirements,
    license="GPL3",
    zip_safe=False,
    keywords='hamsterlib',
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
