# -*- encoding: utf-8 -*-
from __future__ import unicode_literals
from builtins import str

import pytest
import fauxfactory
import datetime
import faker as faker_
from pytest_factoryboy import register

from . import factories
from hamsterlib.lib import HamsterControl


register(factories.CategoryFactory)
register(factories.ActivityFactory)
register(factories.FactFactory)

faker = faker_.Faker()


# Refactored fixtures
def convert_time_to_datetime(time_string):
        """
        Helper method.

        If given a %H:%M string, return a datetime.datetime object with todays
        date.
        """

        return datetime.datetime.combine(
            datetime.datetime.now().date(),
            datetime.datetime.strptime(time_string, "%H:%M").time()
        )


# General Data
@pytest.fixture(params='cyrillic utf8'.split())
def name_string_valid_parametrized(request):
    """Provide a variety of strings that should be valid *names*."""
    return fauxfactory.gen_string(request.param)


@pytest.fixture(params=(None, ''))
def name_string_invalid_parametrized(request):
    """Provide a variety of strings that should be valid *names*."""
    return request.param


@pytest.fixture(params=(
    fauxfactory.gen_string('numeric'),
    fauxfactory.gen_string('alphanumeric'),
    fauxfactory.gen_string('utf8'),
    None,
))
def pk_valid_parametrized(request):
    """Provide a variety of valid primary keys.

    Note:
        At our current stage we do *not* make assumptions about the type of primary key.
        Of cause, this may be a different thing on the backend level!
    """
    return request.param


@pytest.fixture(params=(True, False, 0, 1, '', 'foobar'))
def deleted_valid_parametrized(request):
    return request.param


@pytest.fixture
def start_end_datetimes_from_offset():
    """Generate start/end datetime tuple with given offset in minutes."""
    def generate(offset):
        end = datetime.datetime.now()
        start = end - datetime.timedelta(minutes=offset)
        return (start, end)
    return generate


@pytest.fixture
def start_end_datetimes(start_end_datetimes_from_offset):
    """Return a start/end-datetime-tuple."""
    return start_end_datetimes_from_offset(15)


# Controler
@pytest.fixture
def base_config():
    """Provide a generic baseline configuration."""
    return {
        'unsorted_localized': 'Unsorted',
        'store': 'sqlalchemy',
        'day_start': datetime.time(hour=5, minute=30, second=0),
        'db-path': 'sqlite:///:memory:',
    }


# [TODO] Parametrize over all available stores.
@pytest.yield_fixture
def controler(base_config):
    controler = HamsterControl(base_config)
    yield controler
    controler.store.cleanup()

# Categories




@pytest.fixture(params=(None, True,))
def category_valid_parametrized(request, category_factory, name_string_valid_parametrized):
    """Provide a variety of valid category fixtures."""
    if request.param:
        result = category_factory(name=name_string_valid_parametrized)
    else:
        result = None
    return result


@pytest.fixture
def category_valid_parametrized_without_none(request, category_factory,
        name_string_valid_parametrized):
    """
    Provide a parametrized category fixture but not ``None``.

    This fixuture will represent a wide array of potential name charsets as well
    but not ``category=None``.
    """
    return category_factory(name=name_string_valid_parametrized)


@pytest.fixture
def new_category_values():
    """Return garanteed modified values for a given category."""
    def modify(category):
        return {
            'name': category.name + 'foobar',
        }
    return modify


# Activities

@pytest.fixture
def activity_valid_parametrized(request, activity_factory, name_string_valid_parametrized,
        category_valid_parametrized, deleted_valid_parametrized):
    """Provide a huge array of possible activity versions. Including None."""
    return activity_factory(name=name_string_valid_parametrized,
            category=category_valid_parametrized, deleted=deleted_valid_parametrized)

@pytest.fixture
def new_activity_values(category):
    """Return garanteed modified values for a given activity."""
    def modify(activity):
        return {
            'name': activity.name + 'foobar',
        }
    return modify


# Facts
@pytest.fixture
def fact_factory():
    return factories.FactFactory.build


@pytest.fixture
def fact():
    """Provides a randomized Fact-instance."""
    return factories.FactFactory.build()


@pytest.fixture
def list_of_facts(fact_factory):
    """Provide a factory that returns a list with given amount of Fact instances."""
    def get_list_of_facts(number_of_facts):
        facts = []
        for i in range(number_of_facts):
            facts.append(fact_factory())
        return facts
    return get_list_of_facts

@pytest.fixture(params='alpha cyrillic latin1 utf8'.split())
def description_valid_parametrized(request):
    """Provide a variety of strings that should be valid *descriptions*."""
    return fauxfactory.gen_string(request.param)

@pytest.fixture(params='alpha cyrillic latin1 utf8'.split())
def tag_list_valid_parametrized(request):
    """Provide a variety of strings that should be valid *descriptions*."""
    return [fauxfactory.gen_string(request.param) for i in range(4)]


@pytest.fixture(params=('%M', '%H:%M'))
def string_delta_format_parametrized(request):
    """Provide all possible format option for ``Fact().get_string_delta()``."""
    return request.param

#

@pytest.fixture
def today_fact(fact_factory):
    start = datetime.datetime.now()
    end = start + datetime.timedelta(minutes=30)
    return fact_factory(start=start, end=end)


@pytest.fixture
def not_today_fact(fact_factory):
    start = datetime.datetime.now() - datetime.timedelta(days=2)
    end = start + datetime.timedelta(minutes=30)
    return fact_factory(start=start, end=end)


@pytest.fixture
def current_fact(fact_factory):
    """Provide a ``ongoing fact``. That is a fact that has started but not ended yet."""
    return fact_factory(start=datetime.datetime.now(), end=None)


@pytest.fixture
def new_fact_values():
    """Provide guaranteed different Fact-values for a given Fact-instance."""
    def modify(fact):
        return {
            'start': fact.start - datetime.timedelta(days=10),
            'end': fact.end - datetime.timedelta(days=10),
            'description': fact.description + 'foobar',
        }
    return modify


@pytest.fixture(params=[
    ('foobar', {
        'start': None,
        'end': None,
        'activity': 'foobar',
        'category': None,
        'description': None,
    }),
    ('foo@bar', {
        'start': None,
        'end': None,
        'activity': 'foo',
        'category': 'bar',
        'description': None,
    }),
    ('foo@bar, palimpalum', {
        'start': None,
        'end': None,
        'activity': 'foo',
        'category': 'bar',
        'description': 'palimpalum',
    }),
    ('12:00 foo@bar, palimpalum', {
        'start': convert_time_to_datetime('12:00'),
        'end': None, 'activity': 'foo',
        'category': 'bar',
        'description': 'palimpalum',
    }),
    ('12:00 foo@, palimpalum', {
        'start': convert_time_to_datetime('12:00'),
        'end': None, 'activity': 'foo',
        'activity': 'foo',
        'category': None,
        'description': 'palimpalum',
    }),
    ('12:00-14:14 foo@bar, palimpalum', {
        'start': convert_time_to_datetime('12:00'),
        'end': convert_time_to_datetime('14:14'),
        'activity': 'foo',
        'category': 'bar',
        'description': 'palimpalum',
    }),
])
def raw_fact_parametrized(request):
    """Provide a variety of valid raw facts as well as a dict of its proper components."""
    return request.param


@pytest.fixture(params=[
    '',
    '11:00 12:00 foo@bar',
    'rumpelratz foo@bar',
])
def invalid_raw_fact_parametrized(request):
    return request.param


@pytest.fixture
def raw_fact_with_persistent_activity(persistent_activity):
    """A raw fact whichs 'activity' is already present in the db."""
    return (
        '12:00-14:14 {a.name}@{a.category.name}'.format(a=persistent_activity), {
            'start': convert_time_to_datetime('12:00'),
            'end': convert_time_to_datetime('14:14'),
            'activity': persistent_activity.name,
            'category': persistent_activity.category.name,
            'description': None,
        },
    )

# Refactor end


#    @pytest.fixture
#    def modified_category(category):
#        """
#        Return an existing category with garanteed changes vales from its
#        stored DB-instance.
#        """
#        category.name = category.name + 'foobar'
#        return category

#    @pytest.fixture
#    def existing_activities_factory(alchemy_activity_factory):
#        def generate(amount=5, category=True):
#            """
#            Category True will cause a default factory run, using SubFactory
#            to create new categories associated with each activity.
#            If Category is False, activities will be created without a category.
#            """
#
#            result = []
#            for i in range(amount):
#                if category is False:
#                    activity = alchemy_activity_factory.create(category=None)
#                else:
#                    activity = alchemy_activity_factory()
#                result.append(activity.as_hamster())
#            return result
#        return generate
