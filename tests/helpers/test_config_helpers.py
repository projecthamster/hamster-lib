# -*- coding: utf-8 -*-


from __future__ import absolute_import, unicode_literals

import os

import pytest
from backports.configparser import SafeConfigParser
from hamster_lib.helpers import config_helpers
from hamster_lib.helpers.config_helpers import HamsterAppDirs


class TestHamsterAppDirs(object):
    """Make sure that our custom AppDirs works as intended."""

    def test_user_data_dir_returns_directoy(self, tmpdir, mocker):
        """Make sure method returns directory."""
        path = tmpdir.strpath
        mocker.patch('hamster_lib.helpers.config_helpers.appdirs.user_data_dir', return_value=path)
        appdir = HamsterAppDirs('hamster-lib')
        assert appdir.user_data_dir == path

    @pytest.mark.parametrize('create', [True, False])
    def test_user_data_dir_creates_file(self, tmpdir, mocker, create, faker):
        """Make sure that path creation depends on ``create`` attribute."""
        path = os.path.join(tmpdir.strpath, '{}/'.format(faker.word()))
        mocker.patch('hamster_lib.helpers.config_helpers.appdirs.user_data_dir', return_value=path)
        appdir = HamsterAppDirs('hamster-lib')
        appdir.create = create
        assert os.path.exists(appdir.user_data_dir) is create

    def test_site_data_dir_returns_directoy(self, tmpdir, mocker):
        """Make sure method returns directory."""
        path = tmpdir.strpath
        mocker.patch('hamster_lib.helpers.config_helpers.appdirs.site_data_dir', return_value=path)
        appdir = HamsterAppDirs('hamster-lib')
        assert appdir.site_data_dir == path

    @pytest.mark.parametrize('create', [True, False])
    def test_site_data_dir_creates_file(self, tmpdir, mocker, create, faker):
        """Make sure that path creation depends on ``create`` attribute."""
        path = os.path.join(tmpdir.strpath, '{}/'.format(faker.word()))
        mocker.patch('hamster_lib.helpers.config_helpers.appdirs.site_data_dir', return_value=path)
        appdir = HamsterAppDirs('hamster-lib')
        appdir.create = create
        assert os.path.exists(appdir.site_data_dir) is create

    def test_user_config_dir_returns_directoy(self, tmpdir, mocker):
        """Make sure method returns directory."""
        path = tmpdir.strpath
        mocker.patch('hamster_lib.helpers.config_helpers.appdirs.user_config_dir',
                    return_value=path)
        appdir = HamsterAppDirs('hamster-lib')
        assert appdir.user_config_dir == path

    @pytest.mark.parametrize('create', [True, False])
    def test_user_config_dir_creates_file(self, tmpdir, mocker, create, faker):
        """Make sure that path creation depends on ``create`` attribute."""
        path = os.path.join(tmpdir.strpath, '{}/'.format(faker.word()))
        mocker.patch('hamster_lib.helpers.config_helpers.appdirs.user_config_dir',
                     return_value=path)
        appdir = HamsterAppDirs('hamster-lib')
        appdir.create = create
        assert os.path.exists(appdir.user_config_dir) is create

    def test_site_config_dir_returns_directoy(self, tmpdir, mocker):
        """Make sure method returns directory."""
        path = tmpdir.strpath
        mocker.patch('hamster_lib.helpers.config_helpers.appdirs.site_config_dir',
                     return_value=path)
        appdir = HamsterAppDirs('hamster-lib')
        assert appdir.site_config_dir == path

    @pytest.mark.parametrize('create', [True, False])
    def test_site_config_dir_creates_file(self, tmpdir, mocker, create, faker):
        """Make sure that path creation depends on ``create`` attribute."""
        path = os.path.join(tmpdir.strpath, '{}/'.format(faker.word()))
        mocker.patch('hamster_lib.helpers.config_helpers.appdirs.site_config_dir',
                     return_value=path)
        appdir = HamsterAppDirs('hamster-lib')
        appdir.create = create
        assert os.path.exists(appdir.site_config_dir) is create

    def test_user_cache_dir_returns_directoy(self, tmpdir, mocker):
        """Make sure method returns directory."""
        path = tmpdir.strpath
        mocker.patch('hamster_lib.helpers.config_helpers.appdirs.user_cache_dir',
                     return_value=path)
        appdir = HamsterAppDirs('hamster-lib')
        assert appdir.user_cache_dir == path

    @pytest.mark.parametrize('create', [True, False])
    def test_user_cache_dir_creates_file(self, tmpdir, mocker, create, faker):
        """Make sure that path creation depends on ``create`` attribute."""
        path = os.path.join(tmpdir.strpath, '{}/'.format(faker.word()))
        mocker.patch('hamster_lib.helpers.config_helpers.appdirs.user_cache_dir',
                     return_value=path)
        appdir = HamsterAppDirs('hamster-lib')
        appdir.create = create
        assert os.path.exists(appdir.user_cache_dir) is create

    def test_user_log_dir_returns_directoy(self, tmpdir, mocker):
        """Make sure method returns directory."""
        path = tmpdir.strpath
        mocker.patch('hamster_lib.helpers.config_helpers.appdirs.user_log_dir', return_value=path)
        appdir = HamsterAppDirs('hamster-lib')
        assert appdir.user_log_dir == path

    @pytest.mark.parametrize('create', [True, False])
    def test_user_log_dir_creates_file(self, tmpdir, mocker, create, faker):
        """Make sure that path creation depends on ``create`` attribute."""
        path = os.path.join(tmpdir.strpath, '{}/'.format(faker.word()))
        mocker.patch('hamster_lib.helpers.config_helpers.appdirs.user_log_dir', return_value=path)
        appdir = HamsterAppDirs('hamster-lib')
        appdir.create = create
        assert os.path.exists(appdir.user_log_dir) is create


class TestGetConfigPath(object):
    """Test config pathj retrieval."""

    def test_get_config_path(self, appdirs):
        """Make sure the config target path is constructed to our expectations."""
        expectation = os.path.join(appdirs.user_config_dir, config_helpers.DEFAULT_CONFIG_FILENAME)
        result = config_helpers.get_config_path()
        assert result == expectation


class TestWriteConfigFile(object):
    """Make sure writing a config instance to disk works as expected."""

    def test_file_is_written(self, config_instance, appdirs):
        """
        Make sure the file is written.

        Note: Content is not checked, this is ConfigParsers job.
        """
        config_helpers.write_config_file(config_instance)
        expected_location = config_helpers.get_config_path()
        assert os.path.lexists(expected_location)

    def test_return_config_instance(self, config_instance, appdirs):
        """Make sure we return a ``SafeConfigParser`` instance."""
        result = config_helpers.write_config_file(config_instance)
        assert isinstance(result, SafeConfigParser)


class TestLoadConfigFile(object):
    """Make sure file retrival works as expected."""

    def test_no_file_present(self, appdirs, config_instance):
        """
        Make sure we return ``None``.

        Notw:
            We use the ``appdirs`` fixture to make sure the required dirs exist.
        """
        result = config_helpers.load_config_file(fallback_config_instance=config_instance)
        assert result == config_instance

    def test_file_present(self, config_instance, backend_config):
        """Make sure we try parsing a found config file."""
        result = config_helpers.load_config_file()
        assert result == config_helpers.backend_config_to_configparser(backend_config)


class TestConfigParserToBackendConfig(object):
    """Make sure that conversion works expected."""

    def test_regular_usecase(self, configparser_instance):
        """Make sure basic mechanics work and int/time types are created."""
        cp_instance, expectation = configparser_instance
        result = config_helpers.configparser_to_backend_config(cp_instance)
        assert result == expectation
