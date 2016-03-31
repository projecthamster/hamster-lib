# -*- encoding: utf-8 -*-

from __future__ import unicode_literals
from builtins import str


class TestAlchemyCategory():
    def test_as_hamster(self, alchemy_category):
        """Make sure that conversion into a ``hamsterlib.Category```works as expected."""
        category = alchemy_category.as_hamster()
        assert category.equal_fields(alchemy_category)


class TestAlchemyActivity():
    def test_as_hamster(self, alchemy_activity):
        """Make sure that conversion into a ``hamsterlib.Activity```works as expected."""
        activity = alchemy_activity.as_hamster()
        assert activity.equal_fields(alchemy_activity)


class TestAlchemyFact():
    def test_as_hamster(self, alchemy_fact):
        """Make sure that conversion into a ``hamsterlib.Fact```works as expected."""
        fact = alchemy_fact.as_hamster()
        assert fact.equal_fields(alchemy_fact)
