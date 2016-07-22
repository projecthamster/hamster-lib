# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

import logging

import pytest
from hamster_lib.storage import BaseStore


class TestControler:
    @pytest.mark.parametrize('storetype', ['sqlalchemy'])
    def test_get_store_valid(self, controler, storetype):
        """Make sure  we recieve a valid ``store`` instance."""
        # [TODO]
        # Once we got backend registration up and running this should be
        # improved to check actual store type for that backend.
        controler.config['store'] = storetype
        assert isinstance(controler._get_store(), BaseStore)

    def test_get_store_invalid(self, controler):
        """Make sure we get an exception if store retrieval fails."""
        controler.config['store'] = None
        with pytest.raises(KeyError):
            controler._get_store()

    def test_update_config(self, controler, base_config, mocker):
        """Make sure we assign new config and get a new store."""
        controler._get_store = mocker.MagicMock()
        controler.update_config({})
        assert controler.config == {}
        assert controler._get_store.called

    def test_get_logger(self, controler):
        """Make sure we recieve a logger that maches our expectations."""
        logger = controler._get_logger()
        assert isinstance(logger, logging.Logger)
        assert logger.name == 'hamster-lib.log'
        # [FIXME]
        # assert len(logger.handlers) == 1
        assert isinstance(logger.handlers[0], logging.NullHandler)
