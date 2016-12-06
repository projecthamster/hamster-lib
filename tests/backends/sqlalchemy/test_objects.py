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

    def test_activity_has_facts(self, alchemy_store, alchemy_fact_factory):
        """Make sure that an activity can access ``Fact`` instances."""
        alchemy_fact = alchemy_fact_factory()
        assert alchemy_fact.activity
        activity = alchemy_fact.activity
        assert activity.facts


class TestAlchemyTag(object):
    """Make sure our custom methods behave properly."""
    def test_as_hamster(self, alchemy_tag):
        """Make sure that conversion into a ``hamster_lib.Tag``works as expected."""
        tag = alchemy_tag.as_hamster()
        assert tag.equal_fields(alchemy_tag)


class TestAlchemyFact(object):
    """Make sure our custom methods behave properly."""

    def test_adding_tags(self, alchemy_store, alchemy_fact, alchemy_tag):
        """
        Make sure that adding tags works as expected.

        This is closer to testing we got SQLAlchemy right than actual code.
        """
        assert len(alchemy_fact.tags) == 4
        alchemy_fact.tags.append(alchemy_tag)
        assert len(alchemy_fact.tags) == 5
        assert alchemy_tag in alchemy_fact.tags

    def test_setting_tags(self, alchemy_store, alchemy_fact, alchemy_tag_factory):
        """
        Make sure that adding tags works as expected.

        This is closer to testing we got SQLAlchemy right than actual code.
        """
        assert alchemy_fact.tags
        new_tags = [alchemy_tag_factory() for i in range(5)]
        alchemy_fact.tags = new_tags
        assert len(alchemy_fact.tags) == 5
        assert alchemy_fact.tags == new_tags

    def test_as_hamster(self, alchemy_store, alchemy_fact):
        """Make sure that conversion into a ``hamster_lib.Fact```works as expected."""
        fact = alchemy_fact.as_hamster()
        assert fact.equal_fields(alchemy_fact)
