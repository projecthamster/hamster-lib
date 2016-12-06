# -*- encoding: utf-8 -*-

from __future__ import absolute_import, unicode_literals

import pickle

import pytest
from hamster_lib.helpers import helpers


class TestLoadTmpFact(object):
    """Test related to the loading of the 'ongoing fact'."""
    def test_no_file_present(self):
        """Make sure that we return ``False`` if there is no 'tmpfile' present."""
        assert helpers._load_tmp_fact('non_existing_file') is False

    def test_file_instance_invalid(self, base_config):
        """Make sure we throw an error if the instance picked in the file is no ``Fact``."""
        with open(base_config['tmpfile_path'], 'wb') as fobj:
            pickle.dump('foobar', fobj)
        with pytest.raises(TypeError):
            helpers._load_tmp_fact(base_config['tmpfile_path'])

    def test_valid(self, base_config, tmp_fact):
        """Make sure that we return the stored 'ongoing fact' as expected."""
        result = helpers._load_tmp_fact(base_config['tmpfile_path'])
        assert result == tmp_fact


class TestParseRawFact(object):
    def test_parsing(self, raw_fact_parametrized):
        """Make sure extracted components match our expectations."""
        raw_fact, expectation = raw_fact_parametrized
        result = helpers.parse_raw_fact(raw_fact)
        assert result['timeinfo'] == expectation['timeinfo']
        assert result['activity'] == expectation['activity']
        assert result['category'] == expectation['category']
        assert result['description'] == expectation['description']
