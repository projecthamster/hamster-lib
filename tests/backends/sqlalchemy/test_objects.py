# -*- encoding: utf-8 -*-

from __future__ import unicode_literals
from builtins import str
from future.utils import python_2_unicode_compatible
import pytest

from hamsterlib.backends.sqlalchemy.alchemy import (AlchemyCategory,
                                                    AlchemyActivity,
                                                    AlchemyFact)


@python_2_unicode_compatible
class TestAlchemyCategory():
    def test_init_not_hamster_category(self):
        with pytest.raises(TypeError):
            AlchemyCategory({})


@python_2_unicode_compatible
class TestAlchemyActivity():
    def test_init_not_hamster_activity(self):
        with pytest.raises(TypeError):
            AlchemyActivity({})


@python_2_unicode_compatible
class TestAlchemyFact():
    def test_init_not_hamster_fact(self):
        with pytest.raises(TypeError):
            AlchemyFact({})
