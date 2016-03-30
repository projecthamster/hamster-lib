# -*- encoding: utf-8 -*-

from __future__ import unicode_literals
from builtins import str
from future.utils import python_2_unicode_compatible
import pytest

from hamsterlib.backends.sqlalchemy import AlchemyCategory, AlchemyActivity, AlchemyFact


class TestAlchemyCategory():
    def test__init__valid(self, category_valid_parametrized_without_none):
        """
        Make sure that an AlchemyCategory has same field values as the 'original'.

        Note:
            We assemtle the category ourself instead of using the parametrized fixture
            as we don't want to deal with ``category=None``.
        """
        alchemy_category = AlchemyCategory(category_valid_parametrized_without_none)
        assert category_valid_parametrized_without_none.equal_fields(alchemy_category)

    def test__init__invalid(self, category):
        """Make sure that not passing a ``hamsterlib.Category`` raises an error."""
        with pytest.raises(TypeError):
            AlchemyCategory(category.name)

    def test_as_hamster(self, existing_category_valid_without_none_parametrized):
        """Make sure that conversion into a ``hamsterlib.Category```works as expected."""
        category = existing_category_valid_without_none_parametrized.as_hamster()
        assert category.equal_fields(existing_category_valid_without_none_parametrized)


class TestAlchemyActivity():
    def test__init__valid(self, activity_valid_parametrized):
        """
        Make sure that an AlchemyActivity has same field values as the 'original'.

        We can't profit from ``equal_fields`` here because the initialized ``AlchemyActivity``
        lacks the category.
        """
        result = AlchemyActivity(activity_valid_parametrized)
        assert result.pk == activity_valid_parametrized.pk
        assert result.name == activity_valid_parametrized.name
        assert result.deleted == activity_valid_parametrized.deleted

    def test__init__invalid(self, activity):
        """Make sure that not passing a ``hamsterlib.Activity`` raises an error."""
        with pytest.raises(TypeError):
            AlchemyActivity(activity.name)

    def test_as_hamster(self, existing_activity_valid_parametrized):
        """Make sure that conversion into a ``hamsterlib.Activity```works as expected."""
        activity = existing_activity_valid_parametrized.as_hamster()
        assert activity.equal_fields(existing_activity_valid_parametrized)


class TestAlchemyFact():
    def test__init__valid(self, fact):
        """
        Make sure that an AlchemyFact has same field values as the 'original'.

        We can't profit from ``equal_fields`` here because the initialized ``AlchemyFact``
        lacks the activity.
        """
        result = AlchemyFact(fact)
        assert result.pk == fact.pk
        assert result.start == fact.start
        assert result.end == fact.end
        assert result.description == fact.description
        # [TODO]
        # Once implemented, need to add tags.

    def test__init__invalid(self, fact):
        """Make sure that not passing a ``hamsterlib.Fact`` raises an error."""
        with pytest.raises(TypeError):
            AlchemyFact(fact.activity)

    def test_as_hamster(self, existing_fact_valid_parametrized):
        """Make sure that conversion into a ``hamsterlib.Fact```works as expected."""
        fact = existing_fact_valid_parametrized.as_hamster()
        assert fact.equal_fields(existing_fact_valid_parametrized)
