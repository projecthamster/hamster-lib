# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

import logging

import pytest
from hamster_lib.storage import BaseStore


class TestController:
    @pytest.mark.parametrize('storetype', ['sqlalchemy'])
    def test_get_store_valid(self, controller, storetype):
        """Make sure  we recieve a valid ``store`` instance."""
        # [TODO]
        # Once we got backend registration up and running this should be
        # improved to check actual store type for that backend.
        controller.config['store'] = storetype
        assert isinstance(controller._get_store(), BaseStore)

    def test_get_store_invalid(self, controller):
        """Make sure we get an exception if store retrieval fails."""
        controller.config['store'] = None
        with pytest.raises(KeyError):
            controller._get_store()

    def test_update_config(self, controller, base_config, mocker):
        """Make sure we assign new config and get a new store."""
        controller._get_store = mocker.MagicMock()
        controller.update_config({})
        assert controller.config == {}
        assert controller._get_store.called

    def test_get_logger(self, controller):
        """Make sure we recieve a logger that maches our expectations."""
        logger = controller._get_logger()
        assert isinstance(logger, logging.Logger)
        assert logger.name == 'hamster-lib.log'
        # [FIXME]
        # assert len(logger.handlers) == 1
        assert isinstance(logger.handlers[0], logging.NullHandler)
