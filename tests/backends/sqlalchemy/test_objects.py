# -*- encoding: utf-8 -*-

from __future__ import unicode_literals
from builtins import str
from future.utils import python_2_unicode_compatible
import pytest

from hamsterlib.backends.sqlalchemy import AlchemyCategory, AlchemyActivity, AlchemyFact


@python_2_unicode_compatible
class TestAlchemyCategory():
    def test__init__valid(self, category_factory, name_string_valid_parametrized):
        """
        Make sure that an AlchemyCategory has same field values as the 'original'.

        Note:
            We assemtle the category ourself instead of using the parametrized fixture
            as we don't want to deal with ``category=None``.
        """
        category = category_factory(name=name_string_valid_parametrized)
        alchemy_category = AlchemyCategory(category)
        assert category.equal_fields(alchemy_category)

    def test__init__invalid(self, category):
        """Make sure that not passing a ``hamsterlib.Category`` raises an error."""
        with pytest.raises(TypeError):
            AlchemyCategory(category.name)

    def test_as_tuple_include_pk(self, existing_category_valid_without_none_parametrized):
        """Make sure that returned tuple contains all expected values."""
        result = existing_category_valid_without_none_parametrized.as_tuple(include_pk=True)
        assert result.pk == existing_category_valid_without_none_parametrized.pk
        assert result.name == existing_category_valid_without_none_parametrized.name

    def test_as_tuple_exclude_pk(self, existing_category_valid_without_none_parametrized):
        """Make sure that returned tuple contains all expected values."""
        result = existing_category_valid_without_none_parametrized.as_tuple(include_pk=False)
        assert result.pk is False
        assert result.name == existing_category_valid_without_none_parametrized.name

    def test_as_hamster(self, existing_category_valid_without_none_parametrized):
        """Make sure that conversion into a ``hamsterlib.Category```works as expected."""
        category = existing_category_valid_without_none_parametrized.as_hamster()
        assert category.equal_fields(existing_category_valid_without_none_parametrized)


@python_2_unicode_compatible
class TestAlchemyActivity():
    def test__init__valid(self, activity_valid_parametrized):
        """Make sure that an AlchemyActivity has same field values as the 'original'."""
        result = AlchemyActivity(activity_valid_parametrized)
        assert activity_valid_parametrized.equal_fields(result)

    def test__init__invalid(self, activity):
        """Make sure that not passing a ``hamsterlib.Activity`` raises an error."""
        with pytest.raises(TypeError):
            AlchemyActivity(activity.name)

    def test_as_tuple_include_pk(self, existing_activity_valid_parametrized):
        """Make sure that returned tuple contains all expected values."""
        result = existing_activity_valid_parametrized.as_tuple(include_pk=True)
        assert result.pk == existing_activity_valid_parametrized.pk
        assert result.name == existing_activity_valid_parametrized.name
        assert result.category == existing_activity_valid_parametrized.category
        assert result.deleted == existing_activity_valid_parametrized.deleted

    def test_as_tuple_exclude_pk(self, existing_activity_valid_parametrized):
        """Make sure that returned tuple contains all expected values."""
        result = existing_activity_valid_parametrized.as_tuple(include_pk=False)
        assert result.pk is False
        assert result.category == existing_activity_valid_parametrized.category
        assert result.deleted == existing_activity_valid_parametrized.deleted

    def test_as_hamster(self, existing_activity_valid_parametrized):
        """Make sure that conversion into a ``hamsterlib.Activity```works as expected."""
        activity = existing_activity_valid_parametrized.as_hamster()
        assert activity.equal_fields(existing_activity_valid_parametrized)


@python_2_unicode_compatible
class TestAlchemyFact():
    def test__init__valid(self, fact):
        """Make sure that an AlchemyFact has same field values as the 'original'."""
        result = AlchemyFact(fact)
        assert fact.equal_fields(result)

    def test__init__invalid(self, fact):
        """Make sure that not passing a ``hamsterlib.Fact`` raises an error."""
        with pytest.raises(TypeError):
            AlchemyFact(fact.activity)

    def test_as_tuple_include_pk(self, existing_fact_valid_parametrized):
        """Make sure that returned tuple contains all expected values."""
        result = existing_fact_valid_parametrized.as_tuple(include_pk=True)
        assert result.pk == existing_fact_valid_parametrized.pk
        assert result.activity == existing_fact_valid_parametrized.activity
        assert result.start == existing_fact_valid_parametrized.start
        assert result.end == existing_fact_valid_parametrized.end
        assert result.description == existing_fact_valid_parametrized.description
        assert result.tags == existing_fact_valid_parametrized.tags

    def test_as_tuple_exclude_pk(self, existing_fact_valid_parametrized):
        """Make sure that returned tuple contains all expected values."""
        result = existing_fact_valid_parametrized.as_tuple(include_pk=False)
        assert result.pk is False
        assert result.activity == existing_fact_valid_parametrized.activity
        assert result.start == existing_fact_valid_parametrized.start
        assert result.end == existing_fact_valid_parametrized.end
        assert result.description == existing_fact_valid_parametrized.description
        assert result.tags == existing_fact_valid_parametrized.tags

    def test_as_hamster(self, existing_fact_valid_parametrized):
        """Make sure that conversion into a ``hamsterlib.Fact```works as expected."""
        fact = existing_fact_valid_parametrized.as_hamster()
        assert fact.equal_fields(existing_fact_valid_parametrized)
