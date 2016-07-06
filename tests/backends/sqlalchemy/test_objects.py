# -*- encoding: utf-8 -*-

from __future__ import unicode_literals


class TestAlchemyCategory(object):
    """Make sure our custom methods behave properly."""
    def test_as_hamster(self, alchemy_store, alchemy_category):
        """Make sure that conversion into a ``hamster_lib.Category```works as expected."""
        category = alchemy_category.as_hamster()
        assert category.equal_fields(alchemy_category)


class TestAlchemyActivity(object):
    """Make sure our custom methods behave properly."""
    def test_as_hamster(self, alchemy_store, alchemy_activity):
        """Make sure that conversion into a ``hamster_lib.Activity```works as expected."""
        activity = alchemy_activity.as_hamster()
        assert activity.equal_fields(alchemy_activity)

    def test_activity_has_facts(self, alchemy_store, alchemy_fact):
        """Make sure that an activity can access ``Fact`` instances."""
        assert alchemy_fact.activity
        activity = alchemy_fact.activity
        assert activity.facts


class TestAlchemyFact(object):
    """Make sure our custom methods behave properly."""
    def test_as_hamster(self, alchemy_store, alchemy_fact):
        """Make sure that conversion into a ``hamster_lib.Fact```works as expected."""
        fact = alchemy_fact.as_hamster()
        assert fact.equal_fields(alchemy_fact)
