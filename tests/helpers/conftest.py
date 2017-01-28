# -*- coding: utf-8 -*-

"""Fixtures needed to test helper submodule."""

from __future__ import absolute_import, unicode_literals

import codecs
import datetime
import os

import fauxfactory
import pytest
from backports.configparser import SafeConfigParser
from hamster_lib.helpers import config_helpers
from hamster_lib.helpers.time import TimeFrame


@pytest.fixture
def filename():
    """Provide a filename string."""
    return fauxfactory.gen_utf8()


@pytest.fixture
def filepath(tmpdir, filename):
    """Provide a fully qualified pathame within our tmp-dir."""
    return os.path.join(tmpdir.strpath, filename)


@pytest.fixture
def config_instance(request):
    """A dummy instance of ``SafeConfigParse``."""
    return SafeConfigParser()


@pytest.fixture
def appdirs(mocker, tmpdir):
    """Provide mocked version specific user dirs using a tmpdir."""
    def ensure_directory_exists(directory):
        if not os.path.lexists(directory):
            os.makedirs(directory)
        return directory

    config_helpers.HamsterAppDirs.user_config_dir = ensure_directory_exists(os.path.join(
        tmpdir.mkdir('config').strpath, 'hamster-lib/'))
    config_helpers.HamsterAppDirs.user_data_dir = ensure_directory_exists(os.path.join(
        tmpdir.mkdir('data').strpath, 'hamster-lib/'))
    config_helpers.HamsterAppDirs.user_cache_dir = ensure_directory_exists(os.path.join(
        tmpdir.mkdir('cache').strpath, 'hamster-lib/'))
    config_helpers.HamsterAppDirs.user_log_dir = ensure_directory_exists(os.path.join(
        tmpdir.mkdir('log').strpath, 'hamster-lib/'))
    return config_helpers.HamsterAppDirs


@pytest.fixture
def config_file(config_instance, appdirs):
    """Provide a config file stored under our fake config dir."""
    with codecs.open(os.path.join(appdirs.user_config_dir, 'config.conf'),
            'w', encoding='utf-8') as fobj:
        config_instance.write(fobj)


@pytest.fixture(params=[
    ('foobar', {
        'timeinfo': TimeFrame(None, None, None, None, None),
        'activity': 'foobar',
        'category': None,
        'description': None,
    }),
    ('11:00 12:00 foo@bar', {
        'timeinfo': TimeFrame(None, datetime.time(11), None, None, None),
        'activity': '12:00 foo',
        'category': 'bar',
        'description': None,
    }),
    ('rumpelratz foo@bar', {
        'timeinfo': TimeFrame(None, None, None, None, None),
        'start': None,
        'end': None,
        'activity': 'rumpelratz foo',
        'category': 'bar',
        'description': None,
    }),
    ('foo@bar', {
        'timeinfo': TimeFrame(None, None, None, None, None),
        'activity': 'foo',
        'category': 'bar',
        'description': None,
    }),
    ('foo@bar, palimpalum', {
        'timeinfo': TimeFrame(None, None, None, None, None),
        'activity': 'foo',
        'category': 'bar',
        'description': 'palimpalum',
    }),
    ('12:00 foo@bar, palimpalum', {
        'timeinfo': TimeFrame(None, datetime.time(12), None, None, None),
        'activity': 'foo',
        'category': 'bar',
        'description': 'palimpalum',
    }),
    ('12:00 - 14:14 foo@bar, palimpalum', {
        'timeinfo': TimeFrame(None, datetime.time(12), None, datetime.time(14, 14), None),
        'activity': 'foo',
        'category': 'bar',
        'description': 'palimpalum',
    }),
    # Missing whitespace around ``-`` will prevent timeinfo from beeing parsed.
    ('12:00-14:14 foo@bar, palimpalum', {
        'timeinfo': TimeFrame(None, None, None, None, None),
        'activity': '12:00-14:14 foo',
        'category': 'bar',
        'description': 'palimpalum',
    }),
])
def raw_fact_parametrized(request):
    """Provide a variety of raw facts as well as a dict of its proper components."""
    return request.param
