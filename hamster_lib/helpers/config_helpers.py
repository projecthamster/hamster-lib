# -*- coding: utf-8 -*-

# This file is part of 'hamster-lib'.
#
# 'hamster-lib' is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# 'hamster-lib' is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with 'hamster-lib'.  If not, see <http://www.gnu.org/licenses/>.

"""
Provide functions that provide common config related functionality.

This module provide easy to use convenience functions to handle common configuration
related tasks. Clients can use those to provide consistent behaviour and focus on
their specific requirements instead.
"""


from __future__ import absolute_import, unicode_literals

import os

import appdirs
from backports.configparser import SafeConfigParser

DEFAULT_APP_NAME = 'projecthamster'
DEFAULT_CONFIG_FILENAME = 'config.conf'


class HamsterAppDirs(appdirs.AppDirs):
    """Custom class that ensure appdirs exist."""

    def __init__(self, *args, **kwargs):
        """Add create flag value to instance."""
        super(HamsterAppDirs, self).__init__(*args, **kwargs)
        self.create = True

    @property
    def user_data_dir(self):
        """Return ``user_data_dir``."""
        directory = appdirs.user_data_dir(self.appname, self.appauthor,
                             version=self.version, roaming=self.roaming)
        if self.create:
            self._ensure_directory_exists(directory)
        return directory

    @property
    def site_data_dir(self):
        """Return ``site_data_dir``."""
        directory = appdirs.site_data_dir(self.appname, self.appauthor,
                             version=self.version, multipath=self.multipath)
        if self.create:
            self._ensure_directory_exists(directory)
        return directory

    @property
    def user_config_dir(self):
        """Return ``user_config_dir``."""
        directory = appdirs.user_config_dir(self.appname, self.appauthor,
                               version=self.version, roaming=self.roaming)
        if self.create:
            self._ensure_directory_exists(directory)
        return directory

    @property
    def site_config_dir(self):
        """Return ``site_config_dir``."""
        directory = appdirs.site_config_dir(self.appname, self.appauthor,
                             version=self.version, multipath=self.multipath)
        if self.create:
            self._ensure_directory_exists(directory)
        return directory

    @property
    def user_cache_dir(self):
        """Return ``user_cache_dir``."""
        directory = appdirs.user_cache_dir(self.appname, self.appauthor,
                              version=self.version)
        if self.create:
            self._ensure_directory_exists(directory)
        return directory

    @property
    def user_log_dir(self):
        """Return ``user_log_dir``."""
        directory = appdirs.user_log_dir(self.appname, self.appauthor,
                            version=self.version)
        if self.create:
            self._ensure_directory_exists(directory)
        return directory

    def _ensure_directory_exists(self, directory):
        """Ensure that the passed path exists."""
        if not os.path.lexists(directory):
            os.makedirs(directory)
        return directory


def get_config_path(app_name=DEFAULT_APP_NAME, file_name=DEFAULT_CONFIG_FILENAME):
    """
    Return the path where the config file is stored.

    Args:
        app_name (text_type, optional): Name of the application, defaults to
        ``'projecthamster``. Allows you to use your own application specific
        namespace if you wish.
        file_name (text_type, optional): Name of the config file. Defaults to
        ``config.conf``.

    Returns:
        str: Fully qualified path (dir & filename) where we expect the config file.
    """
    appdirs_ = HamsterAppDirs(app_name)
    config_dir = appdirs_.user_config_dir
    return os.path.join(config_dir, file_name)


def write_config_file(config_instance, app_name=DEFAULT_APP_NAME,
                      file_name=DEFAULT_CONFIG_FILENAME):
    """
    Write a ConfigParser instance to file at the correct location.

    Args:
        config_instance: Config instance to safe to file.
        app_name (text_type, optional): Name of the application, defaults to
        ``'projecthamster``. Allows you to use your own application specific
        namespace if you wish.
        file_name (text_type, optional): Name of the config file. Defaults to
        ``config.conf``.

    Returns:
        SafeConfigParser: Instance written to file.
    """
    path = get_config_path(app_name, file_name)
    with open(path, 'w') as fobj:
        config_instance.write(fobj)
    return config_instance


def get_config_instance(fallback_config_instance, app_name=DEFAULT_APP_NAME,
        file_name=DEFAULT_CONFIG_FILENAME):
    """
    Either retrieve a ``SafeConfigParser`` instance from disk of create a fallback config.

    If we can not find a config file under its expected location, we trigger creation
    of a new default file. Either way a ``SafeConfigParser`` instance is returned.

    Args:
        fallback_config_instance: Default config instance to be written to disk if none
            is present.
        app_name (text_type, optional): Name of the application, defaults to
        ``'projecthamster``. Allows you to use your own application specific
        namespace if you wish.
        file_name (text_type, optional): Name of the config file. Defaults to
        ``config.conf``.

    Returns:
        SafeConfigParser: Either the config loaded from file or an instance representing
            the content of our newly creating default config.
    """
    config = SafeConfigParser()
    path = get_config_path(app_name)
    if not config.read(path):
        config = write_config_file(app_name, fallback_config_instance, file_name=file_name)
    return config
