# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

import copy
import datetime
from builtins import str as text
from operator import attrgetter

import faker as faker_
import pytest
from freezegun import freeze_time
from hamster_lib import Activity, Category, Fact, Tag
from six import text_type

faker = faker_.Faker()


class TestCategory(object):
    def test_init_valid(self, name_string_valid_parametrized, pk_valid_parametrized):
        """Make sure that Category constructor accepts all valid values."""
        category = Category(name_string_valid_parametrized, pk_valid_parametrized)
        assert category.name == name_string_valid_parametrized
        assert category.pk == pk_valid_parametrized

    def test_init_invalid(self, name_string_invalid_parametrized):
        """Make sure that Category constructor rejects all invalid values."""
        with pytest.raises(ValueError):
            Category(name_string_invalid_parametrized)

    def test_as_tuple_include_pk(self, category):
        """Make sure categories tuple representation works as intended and pk is included."""
        assert category.as_tuple() == (category.pk, category.name)

    def test_as_tuple_exclude_pf(self, category):
        """Make sure categories tuple representation works as intended and pk is excluded."""
        assert category.as_tuple(include_pk=False) == (False, category.name)

    def test_equal_fields_true(self, category):
        """Make sure that two categories that differ only in their PK compare equal."""
        other_category = copy.deepcopy(category)
        other_category.pk = 1
        assert category.equal_fields(other_category)

    def test_equal_fields_false(self, category):
        """Make sure that two categories that differ not only in their PK compare unequal."""
        other_category = copy.deepcopy(category)
        other_category.pk = 1
        other_category.name += 'foobar'
        assert category.equal_fields(other_category) is False

    def test__eq__false(self, category):
        """Make sure that two distinct categories return ``False``."""
        other_category = copy.deepcopy(category)
        other_category.pk = 1
        assert category is not other_category
        assert category != other_category

    def test__eq__true(self, category):
        """Make sure that two identical categories return ``True``."""
        other_category = copy.deepcopy(category)
        assert category is not other_category
        assert category == other_category

    def test_is_hashable(self, category):
        """Test that ``Category`` instances are hashable."""
        assert hash(category)

    def test_hash_method(self, category):
        """Test that ``__hash__`` returns the hash expected."""
        assert hash(category) == hash(category.as_tuple())

    def test_hash_different_between_instances(self, category_factory):
        """
        Test that different instances have different hashes.

        This is actually unneeded as we are merely testing the builtin ``hash``
        function and ``Category.as_tuple`` but for reassurance we test it anyway.
        """
        assert hash(category_factory()) != hash(category_factory())

    def test__str__(self, category):
        """Test string representation."""
        assert '{name}'.format(name=category.name) == text(category)

    def test__repr__(self, category):
        """Test representation method."""
        result = repr(category)
        assert isinstance(result, str)
        expectation = '[{pk}] {name}'.format(pk=repr(category.pk),
            name=repr(category.name))
        assert result == expectation


class TestActivity(object):
    def test_init_valid(self, name_string_valid_parametrized, pk_valid_parametrized,
            category_valid_parametrized, deleted_valid_parametrized):
        """Test that init accepts all valid values."""
        activity = Activity(name_string_valid_parametrized, pk=pk_valid_parametrized,
            category=category_valid_parametrized, deleted=deleted_valid_parametrized)
        assert activity.name == name_string_valid_parametrized
        assert activity.pk == pk_valid_parametrized
        assert activity.category == category_valid_parametrized
        assert activity.deleted == bool(deleted_valid_parametrized)

    def test_init_invalid(self, name_string_invalid_parametrized):
        """
        Test that init rejects all invalid values.

        Note:
            Right now, the only aspect that can have concievable invalid value
            is the name.
        """
        with pytest.raises(ValueError):
            Activity(name_string_invalid_parametrized)

    def test_create_from_composite(self, activity):
        result = Activity.create_from_composite(activity.name, activity.category.name)
        assert result.name == activity.name
        assert result.category == activity.category

    def test_as_tuple_include_pk(self, activity):
        """Make sure that conversion to a tuple matches our expectations."""
        assert activity.as_tuple() == (activity.pk, activity.name,
            activity.category, activity.deleted)

    def test_as_tuple_exclude_pk(self, activity):
        """Make sure that conversion to a tuple matches our expectations."""
        assert activity.as_tuple(include_pk=False) == (False, activity.name,
            (False, activity.category.name), activity.deleted)

    def test_equal_fields_true(self, activity):
        """Make sure that two activities that differ only in their PK compare equal."""
        other = copy.deepcopy(activity)
        other.pk = 1
        assert activity.equal_fields(other)

    def test_equal_fields_false(self, activity):
        """Make sure that two activities that differ not only in their PK compare unequal."""
        other = copy.deepcopy(activity)
        other.pk = 1
        other.name += 'foobar'
        assert activity.equal_fields(other) is False

    def test__eq__false(self, activity):
        """Make sure that two distinct activities return ``False``."""
        other = copy.deepcopy(activity)
        other.pk = 1
        assert activity is not other
        assert activity != other

    def test__eq__true(self, activity):
        """Make sure that two identical activities return ``True``."""
        other = copy.deepcopy(activity)
        assert activity is not other
        assert activity == other

    def test_is_hashable(self, activity):
        """Test that ``Category`` instances are hashable."""
        assert hash(activity)

    def test_hash_method(self, activity):
        """Test that ``__hash__`` returns the hash expected."""
        assert hash(activity) == hash(activity.as_tuple())

    def test_hash_different_between_instances(self, activity_factory):
        """
        Test that different instances have different hashes.

        This is actually unneeded as we are merely testing the builtin ``hash``
        function and ``Category.as_tuple`` but for reassurance we test it anyway.
        """
        assert hash(activity_factory()) != hash(activity_factory())

    def test__str__without_category(self, activity):
        activity.category = None
        assert text(activity) == '{name}'.format(name=activity.name)

    def test__str__with_category(self, activity):
        assert text(activity) == '{name} ({category})'.format(
            name=activity.name, category=activity.category.name)

    def test__repr__with_category(self, activity):
        """Make sure our debugging representation matches our expectations."""
        result = repr(activity)
        assert isinstance(result, str)
        expectation = '[{pk}] {name} ({category})'.format(
            pk=repr(activity.pk), name=repr(activity.name), category=repr(activity.category.name))
        assert result == expectation

    def test__repr__without_category(self, activity):
        """Make sure our debugging representation matches our expectations."""
        activity.category = None
        result = repr(activity)
        assert isinstance(result, str)
        expectation = '[{pk}] {name}'.format(pk=repr(activity.pk), name=repr(activity.name))
        assert result == expectation


class TestTag(object):
    def test_init_valid(self, name_string_valid_parametrized, pk_valid_parametrized):
        """Make sure that Tag constructor accepts all valid values."""
        tag = Tag(name_string_valid_parametrized, pk_valid_parametrized)
        assert tag.name == name_string_valid_parametrized
        assert tag.pk == pk_valid_parametrized

    def test_init_invalid(self, name_string_invalid_parametrized):
        """Make sure that Tag constructor rejects all invalid values."""
        with pytest.raises(ValueError):
            Tag(name_string_invalid_parametrized)

    def test_as_tuple_include_pk(self, tag):
        """Make sure tags tuple representation works as intended and pk is included."""
        assert tag.as_tuple() == (tag.pk, tag.name)

    def test_as_tuple_exclude_pf(self, tag):
        """Make sure tags tuple representation works as intended and pk is excluded."""
        assert tag.as_tuple(include_pk=False) == (False, tag.name)

    def test_equal_fields_true(self, tag):
        """Make sure that two tags that differ only in their PK compare equal."""
        other_tag = copy.deepcopy(tag)
        other_tag.pk = 1
        assert tag.equal_fields(other_tag)

    def test_equal_fields_false(self, tag):
        """Make sure that two tags that differ not only in their PK compare unequal."""
        other_tag = copy.deepcopy(tag)
        other_tag.pk = 1
        other_tag.name += 'foobar'
        assert tag.equal_fields(other_tag) is False

    def test__eq__false(self, tag):
        """Make sure that two distinct tags return ``False``."""
        other_tag = copy.deepcopy(tag)
        other_tag.pk = 1
        assert tag is not other_tag
        assert tag != other_tag

    def test__eq__true(self, tag):
        """Make sure that two identical categories return ``True``."""
        other_tag = copy.deepcopy(tag)
        assert tag is not other_tag
        assert tag == other_tag

    def test_is_hashable(self, tag):
        """Test that ``Tag`` instances are hashable."""
        assert hash(tag)

    def test_hash_method(self, tag):
        """Test that ``__hash__`` returns the hash expected."""
        assert hash(tag) == hash(tag.as_tuple())

    def test_hash_different_between_instances(self, tag_factory):
        """
        Test that different instances have different hashes.

        This is actually unneeded as we are merely testing the builtin ``hash``
        function and ``Tag.as_tuple`` but for reassurance we test it anyway.
        """
        assert hash(tag_factory()) != hash(tag_factory())

    def test__str__(self, tag):
        """Test string representation."""
        assert '{name}'.format(name=tag.name) == text(tag)

    def test__repr__(self, tag):
        """Test representation method."""
        result = repr(tag)
        assert isinstance(result, str)
        expectation = '[{pk}] {name}'.format(pk=repr(tag.pk),
            name=repr(tag.name))
        assert result == expectation


class TestFact(object):
    def test_fact_init_valid(self, activity, start_end_datetimes, pk_valid_parametrized,
            description_valid_parametrized, tag_list_valid_parametrized):
        """Make sure valid values instaniate a Fact."""

        fact = Fact(activity, start_end_datetimes[0], start_end_datetimes[1],
            pk_valid_parametrized, description_valid_parametrized, tag_list_valid_parametrized)
        assert fact.activity == activity
        assert fact.pk == pk_valid_parametrized
        assert fact.description == description_valid_parametrized
        assert fact.start == start_end_datetimes[0]
        assert fact.end == start_end_datetimes[1]
        assert fact.tags == tag_list_valid_parametrized

    def test_create_from_raw_fact_valid(self, valid_raw_fact_parametrized):
        """Make sure that a valid raw fact creates a proper Fact."""
        assert Fact.create_from_raw_fact(valid_raw_fact_parametrized)

    def test_create_from_raw_fact_invalid(self, invalid_raw_fact_parametrized):
        """Make sure invalid string raises an exception."""
        with pytest.raises(ValueError):
            Fact.create_from_raw_fact(invalid_raw_fact_parametrized)

    @pytest.mark.parametrize(('raw_fact', 'expectations'), [
        ('-7 foo@bar, palimpalum',
         {'start': datetime.datetime(2015, 5, 2, 18, 0, 0),
          'end': None,
          'activity': 'foo',
          'category': 'bar',
          'description': 'palimpalum'},
         ),
    ])
    @freeze_time('2015-05-02 18:07')
    def test_create_from_raw_fact_with_delta(self, raw_fact, expectations):
        fact = Fact.create_from_raw_fact(raw_fact)
        assert fact.start == expectations['start']

    @pytest.mark.parametrize('start', [None, faker.date_time()])
    def test_start_valid(self, fact, start):
        """Make sure that valid arguments get stored by the setter."""
        fact.start = start
        assert fact.start == start

    def test_start_invalid(self, fact):
        """Make sure that trying to store dateimes as strings throws an error."""
        with pytest.raises(TypeError):
            fact.start = faker.date_time().strftime('%y-%m-%d %H:%M')

    @pytest.mark.parametrize('end', [None, faker.date_time()])
    def test_end_valid(self, fact, end):
        """Make sure that valid arguments get stored by the setter."""
        fact.end = end
        assert fact.end == end

    def test_end_invalid(self, fact):
        """Make sure that trying to store dateimes as strings throws an error."""
        with pytest.raises(TypeError):
            fact.end = faker.date_time().strftime('%y-%m-%d %H:%M')

    def test_description_valid(self, fact, description_valid_parametrized):
        """Make sure that valid arguments get stored by the setter."""
        fact.description = description_valid_parametrized
        assert fact.description == description_valid_parametrized

    def test_delta(self, fact):
        """Make sure that valid arguments get stored by the setter."""
        assert fact.delta == fact.end - fact.start

    def test_delta_no_end(self, fact):
        """Make sure that a missing end datetime results in ``delta=None``."""
        fact.end = None
        assert fact.delta is None

    @pytest.mark.parametrize('offset', [
        (15, {'%M': '15', '%H:%M': '00:15'}),
        (452, {'%M': '452', '%H:%M': '07:32'}),
        (912, {'%M': '912', '%H:%M': '15:12'}),
    ])
    def test_get_string_delta_valid_format(self, fact, offset,
            start_end_datetimes_from_offset, string_delta_format_parametrized):
        """Make sure that the resulting string matches our expectation."""
        offset, expectation = offset
        fact.start, fact.end = start_end_datetimes_from_offset(offset)
        result = fact.get_string_delta(string_delta_format_parametrized)
        assert result == expectation[string_delta_format_parametrized]

    def test_get_string_delta_invalid_format(self, fact):
        """Ensure that passing an invalid format will raise an exception."""
        with pytest.raises(ValueError):
            fact.get_string_delta('foobar')

    def test_date(self, fact):
        """Make sure the property returns just the date of ``Fact().start``."""
        assert fact.date == fact.start.date()

    def test_category_property(self, fact):
        """Make sure the property returns this facts category."""
        assert fact.category == fact.activity.category

    def test_serialized_string(self, fact):
        """Make sure that a serialized string with full information matches our expectation."""
        expectation = '{start} - {end} {activity}@{category} #{tag}, {description}'.format(
            start=fact.start.strftime('%Y-%m-%d %H:%M'),
            end=fact.end.strftime('%Y-%m-%d %H:%M'),
            activity=fact.activity.name,
            category=fact.category.name,
            tag=sorted(list(fact.tags), key=attrgetter('name'))[0].name,
            description=fact.description
        )
        result = fact.get_serialized_string()
        assert isinstance(result, text_type)
        assert result == expectation

    @pytest.mark.parametrize(('values', 'expectation'), (
        ({'start': datetime.datetime(2016, 1, 1, 18),
          'end': datetime.datetime(2016, 1, 1, 19),
          'activity': Activity('homework', category=Category('school')),
          'tags': set([Tag('math'), Tag('science')]),
          'description': 'something clever ...',
          },
         '2016-01-01 18:00 - 2016-01-01 19:00 homework@school #math #science, something clever ...'
         ),
        ({'start': datetime.datetime(2016, 1, 1, 18),
          'end': datetime.datetime(2016, 1, 1, 19),
          'activity': Activity('homework', category=None),
          'tags': set([Tag('math'), Tag('science'), Tag('science fiction')]),
          'description': 'something',
          },
         '2016-01-01 18:00 - 2016-01-01 19:00 homework #math #science #science fiction, something'
         ),
        ({'start': datetime.datetime(2016, 1, 1, 18),
          'end': datetime.datetime(2016, 1, 1, 19),
          'activity': Activity('homework', category=Category('school')),
          'tags': set(),
          'description': 'something clever ...',
          },
         '2016-01-01 18:00 - 2016-01-01 19:00 homework@school, something clever ...'
         ),
        ({'start': datetime.datetime(2016, 1, 1, 18),
          'end': datetime.datetime(2016, 1, 1, 19),
          'activity': Activity('homework', category=Category('school')),
          'tags': set([Tag('science'), Tag('math')]),
          'description': '',
          },
         '2016-01-01 18:00 - 2016-01-01 19:00 homework@school #math #science'
         ),
        ({'start': datetime.datetime(2016, 1, 1, 18),
          'end': datetime.datetime(2016, 1, 1, 19),
          'activity': Activity('homework', category=Category('school')),
          'tags': set(),
          'description': '',
          },
         '2016-01-01 18:00 - 2016-01-01 19:00 homework@school'
         ),
        ({'start': None,
          'end': datetime.datetime(2016, 1, 1, 19),
          'activity': Activity('homework', category=Category('school')),
          'tags': set([Tag('math'), Tag('science')]),
          'description': 'something clever ...',
          },
         'homework@school #math #science, something clever ...'
         ),
        ({'start': None,
          'end': None,
          'activity': Activity('homework', category=Category('school')),
          'tags': set([Tag('math'), Tag('science')]),
          'description': 'something clever ...',
          },
         'homework@school #math #science, something clever ...'
         ),
        ({'start': datetime.datetime(2016, 1, 1, 18),
          'end': None,
          'activity': Activity('homework', category=Category('school')),
          'tags': set([Tag('math'), Tag('science')]),
          'description': 'something clever ...',
          },
         '2016-01-01 18:00 homework@school #math #science, something clever ...'
         ),
    ))
    def test_serialized_string_various_missing_values(self, fact, values, expectation):
        """Make sure the serialized string is correct even if some information is missing."""
        for attribute, value in values.items():
            setattr(fact, attribute, value)
        assert fact.get_serialized_string() == expectation

    def test_as_tuple_include_pk(self, fact):
        """Make sure that conversion to a tuple matches our expectations."""
        assert fact.as_tuple() == (fact.pk, fact.activity.as_tuple(include_pk=True),
            fact.start, fact.end, fact.description, frozenset(fact.tags))

    def test_as_tuple_exclude_pk(self, fact):
        """Make sure that conversion to a tuple matches our expectations."""
        assert fact.as_tuple(include_pk=False) == (False, fact.activity.as_tuple(include_pk=False),
            fact.start, fact.end, fact.description,
            frozenset([tag.as_tuple(include_pk=False) for tag in fact.tags]))

    def test_equal_fields_true(self, fact):
        """Make sure that two facts that differ only in their PK compare equal."""
        other = copy.deepcopy(fact)
        other.pk = 1
        assert fact.equal_fields(other)

    def test_equal_fields_false(self, fact):
        """Make sure that two facts that differ not only in their PK compare unequal."""
        other = copy.deepcopy(fact)
        other.pk = 1
        other.description += 'foobar'
        assert fact.equal_fields(other) is False

    def test__eq__false(self, fact):
        """Make sure that two distinct facts return ``False``."""
        other = copy.deepcopy(fact)
        other.pk = 1
        assert fact is not other
        assert fact != other

    def test__eq__true(self, fact):
        """Make sure that two identical facts return ``True``."""
        other = copy.deepcopy(fact)
        assert fact is not other
        assert fact == other

    def test_is_hashable(self, fact):
        """Test that ``Fact`` instances are hashable."""
        assert hash(fact)

    def test_hash_method(self, fact):
        """Test that ``__hash__`` returns the hash expected."""
        assert hash(fact) == hash(fact.as_tuple())

    def test_hash_different_between_instances(self, fact_factory):
        """
        Test that different instances have different hashes.

        This is actually unneeded as we are merely testing the builtin ``hash``
        function and ``Fact.as_tuple`` but for reassurance we test it anyway.
        """
        assert hash(fact_factory()) != hash(fact_factory())

    def test__str__(self, fact):
        expectation = '{start} to {end} {activity}@{category}, {description}'.format(
            start=fact.start.strftime('%Y-%m-%d %H:%M'),
            end=fact.end.strftime('%Y-%m-%d %H:%M'),
            activity=fact.activity.name,
            category=fact.category.name,
            description=fact.description
        )
        assert text(fact) == expectation

    def test__str__no_end(self, fact):
        fact.end = None
        expectation = '{start} {activity}@{category}, {description}'.format(
            start=fact.start.strftime('%Y-%m-%d %H:%M'),
            activity=fact.activity.name,
            category=fact.category.name,
            description=fact.description
        )
        assert text(fact) == expectation

    def test__str__no_start_no_end(self, fact):
        fact.start = None
        fact.end = None
        expectation = '{activity}@{category}, {description}'.format(
            activity=fact.activity.name,
            category=fact.category.name,
            description=fact.description
        )
        assert text(fact) == expectation

    def test__repr__(self, fact):
        """Make sure our debugging representation matches our expectations."""
        expectation = '{start} to {end} {activity}@{category}, {description}'.format(
            start=repr(fact.start.strftime('%Y-%m-%d %H:%M')),
            end=repr(fact.end.strftime('%Y-%m-%d %H:%M')),
            activity=repr(fact.activity.name),
            category=repr(fact.category.name),
            description=repr(fact.description)
        )
        result = repr(fact)
        assert isinstance(result, str)
        assert result == expectation

    def test__repr__no_end(self, fact):
        """Test that facts without end datetime are represented properly."""
        result = repr(fact)
        assert isinstance(result, str)
        fact.end = None
        expectation = '{start} {activity}@{category}, {description}'.format(
            start=repr(fact.start.strftime('%Y-%m-%d %H:%M')),
            activity=repr(fact.activity.name),
            category=repr(fact.category.name),
            description=repr(fact.description)
        )
        result = repr(fact)
        assert isinstance(result, str)
        assert result == expectation

    def test__repr__no_start_no_end(self, fact):
        """Test that facts without timeinfo are represented properly."""
        fact.start = None
        fact.end = None
        expectation = '{activity}@{category}, {description}'.format(
            activity=repr(fact.activity.name),
            category=repr(fact.category.name),
            description=repr(fact.description)
        )
        result = repr(fact)
        assert isinstance(result, str)
        assert result == expectation
