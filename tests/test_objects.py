# -*- encoding: utf-8 -*-
from __future__ import unicode_literals

import pytest
import datetime
import faker as faker_

from hamsterlib.objects import Category, Activity, Fact

faker = faker_.Faker()

@pytest.fixture(params=[
    {'name': faker.name(), 'pk': 1},
    {'name': faker.name(), 'pk': None},
])
def category_init_valid_values(request):
    """Valid (name, pk) tuples."""
    return request.param

@pytest.fixture(params=[
    {'name': None, 'pk': 2, 'exception': ValueError},
    {'name': '','pk': None, 'exception': ValueError},
    {'name': 12, 'pk': None, 'exception': TypeError},
])
def category_init_invalid_values(request):
    """Invalid (name, pk) values and their expected Exception."""
    return request.param


class TestCategory:
    def test_init_valid(self, category_init_valid_values):
        """Make sure that Category constructor accepts all valid values."""
        category = Category(**category_init_valid_values)
        assert category.name == category_init_valid_values['name']
        assert category.pk == category_init_valid_values['pk']

    def test_init_invalid(self, category_init_invalid_values):
        """Make sure that Category constructor rejects all invalid values."""
        with pytest.raises(category_init_invalid_values.pop('exception')):
            category = Category(**category_init_invalid_values)


class TestActivity:
    def test_init_valid(self, activity_init_valid_values):
        """Test that init accepts all valid values."""
        activity = Activity(**activity_init_valid_values)
        assert activity.name == activity_init_valid_values['name']
        assert activity.pk == activity_init_valid_values['pk']
        assert activity.category == activity_init_valid_values['category']
        assert activity.deleted == activity_init_valid_values['deleted']

    def test_init_invalid(self, activity_init_invalid_values):
        """Test that init rejects all invalid values."""
        with pytest.raises(ValueError):
            activity = Activity(**activity_init_invalid_values)

    def test_str_without_category(self, activity):
        activity.category = None
        assert str(activity) == '[{a.pk}] {a.name}'.format(a=activity)

    def test_str_with_category(self, activity):
        assert str(activity) == '[{a.pk}] {a.name} ({a.category.name})'.format(a=activity)

    def test_as_dict(self, activity):
        expectation = {
            'pk': activity.pk,
            'name': activity.name,
            'category': activity.category.pk,
            'deleted': activity.deleted,
        }
        assert activity.as_dict() == expectation


class TestFact:
    def test_fact_init_valid(self, fact_init_valid_values):
        """Make sure valid values instaniate a Fact."""

        fact = Fact(**fact_init_valid_values)
        assert fact.activity == fact_init_valid_values['activity']
        assert fact.description == fact_init_valid_values['description']
        assert fact.start == fact_init_valid_values['start']
        assert fact.end == fact_init_valid_values['end']

    def test_delta(self, fact):
        assert fact.delta == fact.end - fact.start

    def test_delta_no_end(self, fact):
        fact.end = None
        assert fact.delta == None


    def test_date(self, fact):
        assert fact.date == fact.start.date()

    def test_serialized_name_with_category_and_description(self, fact):
        expectation = '{f.activity.name}@{f.category.name}, {f.description}'.format(f=fact)
        assert fact.serialized_name == expectation

    def test_serialized_name_with_category_no_description(self, fact):
        fact.description = None
        expectation = '{f.activity.name}@{f.category.name}'.format(f=fact)
        assert fact.serialized_name == expectation

    def test_serialized_name_with_description_no_category(self, fact):
        fact.activity.category = None
        expectation = '{f.activity.name}, {f.description}'.format(f=fact)
        assert fact.serialized_name == expectation

    def test_str(self, fact):
        expectation = '{start} - {end} {serialized_name}'.format(
            start = fact.start.strftime("%d-%m-%Y %H:%M"),
            end = fact.end.strftime("%H:%M"),
            serialized_name = fact.serialized_name)
        assert str(fact) == expectation

    def test_str_no_end(self, fact):
        fact.end = None
        expectation = '{start} {serialized_name}'.format(
            start = fact.start.strftime("%d-%m-%Y %H:%M"),
            serialized_name = fact.serialized_name)
        assert str(fact) == expectation

    def test_as_dict(self, fact):
        expectation = {
            'pk': fact.pk,
            'activity': fact.activity,
            'start': fact.start,
            'end': fact.end,
            'description': fact.description,
        }
        assert fact.as_dict() == expectation

