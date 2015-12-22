# -*- encoding: utf-8 -*-
from __future__ import unicode_literals

import pytest
import operator
import datetime
import faker as faker_
from pytest_factoryboy import register
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from hamsterlib.lib import HamsterControl
from hamsterlib import objects
#from hamsterlib.backends.sqlalchemy import alchemy, store
#from hamsterlib.backends.storage import BaseStore

#from hamsterlib import hamster_dbus_service

from . import factories
#from . import common

faker = faker_.Faker()

# Refactored fixtures

def convert_time_to_datetime(time_string):
        """
        Helper method.

        If given a %H:%M string, return a datetime.datetime object with todays
        date.
        """
        now = datetime.datetime.now()
        return datetime.datetime.combine(
            now.date(), datetime.datetime.strptime(time_string, "%H:%M").time()
        )


# Controler
@pytest.fixture
def base_config():
    """Privide a generic baseline configutation."""
    return {
        'unsorted_localized': 'Unsorted',
        'store': 'sqlalchemy',
        'daystart': datetime.time(hour=0, minute=0, second=0),
        'dayend': datetime.time(hour=23, minute=59, second=59),
        'db-path': 'sqlite:///:memory:',
    }


# [TODO] Parametrize over all available stores.
@pytest.yield_fixture
def controler(base_config):
    controler = HamsterControl(base_config)
    yield controler
    controler.store.cleanup()

# Categories
@pytest.fixture
def category_factory():
    return factories.CategoryFactory.build

@pytest.fixture
def category():
    """A random Category-instance."""
    return factories.CategoryFactory.build()

def persistent_category(controler, category):
    return controler.categories._add(category)

def persistent_category_factory(controler, category_factory):
    def generate(**kwargs):
        return controler.categories._add(category_factory(**kwargs))
    return generate


@pytest.fixture
def category_name():
    """Provide a randomized category-name."""
    return faker.name()


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
def activity_factory():
    activity = factories.ActivityFactory.build
    activity.category = factories.CategoryFactory.build()
    return activity

@pytest.fixture
def activity():
    """Return a randomized Activity-instance."""
    activity = factories.ActivityFactory.build()
    activity.category = factories.CategoryFactory.build()
    return activity


@pytest.fixture
def persistent_activity(activity, controler):
    return controler.activities._add(activity)

@pytest.fixture
def persistent_activity_factory(controler, activity_factory):
    def generate(**kwargs):
        return controler.activities._add(activity_factory(**kwargs))
    return generate

@pytest.fixture
def new_activity_values(category):
    """Return garanteed modified values for a given activity."""
    def modify(activity):
        return {
            'name': activity.name + 'foobar',
        }
    return modify


@pytest.fixture(params=[
    {'name': faker.name(),
     'pk': 1,
     'category': category(),
     'deleted': True
     },
    {'name': faker.name(),
     'pk': None,
     'category': category(),
     'deleted': True
     },
    {'name': faker.name(),
     'pk': 1,
     'category': None,
     'deleted': True
     },
    {'name': faker.name(),
     'pk': 1,
     'category': category(),
     'deleted': False
     },
])
def activity_init_valid_values(request):
    """A range of valid values for creating an activity."""
    return request.param


@pytest.fixture(params=[
    {'name': None,
     'pk': 1,
     'category': category(),
     'deleted': True
     },
    {'name': '',
     'pk': None,
     'category': category(),
     'deleted': False
     },
])
def activity_init_invalid_values(request):
    """A range of invalid values for creating an activity."""
    return request.param


# Facts

@pytest.fixture
def fact_factory():
    return factories.FactFactory.build

@pytest.fixture
def fact():
    """Provides a randomized Fact-instance."""
    return factories.FactFactory.build()


@pytest.fixture
def persistent_fact(fact, controler):
    return controler.facts._add(fact)

@pytest.fixture
def persistent_fact_factory(controler, fact_factory):
    def generate(**kwargs):
        return controler.facts._add(fact_factory(**kwargs))
    return generate

@pytest.fixture
def today_fact(fact_factory):
    start = datetime.datetime.now()
    end = start + datetime.timedelta(minutes=30)
    return fact_factory(start=start, end=end)

@pytest.fixture
def persistent_today_fact(controler, today_fact):
    return controler.facts._add(today_fact)

@pytest.fixture
def not_today_fact(fact_factory):
    start = datetime.datetime.now() - datetime.timedelta(days=2)
    end = start + datetime.timedelta(minutes=30)
    return fact_factory(start=start, end=end)


@pytest.fixture
def persistent_not_today_fact(controler, not_today_fact):
    return controler.facts._add(not_today_fact)

@pytest.fixture
def current_fact(fact_factory):
    return fact_factory(start=datetime.datetime.now(), end=None)

@pytest.fixture
def persistent_current_fact(controler, current_fact):
    return controler.facts._add(current_fact)


@pytest.fixture(params=[
        {'start': datetime.datetime(2015, 11, 5, 14, 30, 0),
         'end': datetime.datetime(2015, 11, 5, 15, 23, 0),
         'activity': activity(),
         'description': None,
         },
])
def fact_init_valid_values(request):
    """Provide valid values for creating a new Fact-instance."""
    return request.param


@pytest.fixture(params=[
])
def fact_init_invalid_values(request):
    """Provide invalid values for creating a new Fact-instance."""
    return request.param

@pytest.fixture
def new_fact_values():
    """Provice guaranteed different Fact-values for a given Fact-instance."""
    def modify(fact):
        return {
            'start': fact.start - datetime.timedelta(days=1),
            'end': fact.end - datetime.timedelta(days=1),
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
        }
    ),
])
def fact_various_raw_facts(request):
    return request.param


@pytest.fixture(params=[
    '',
    'foo@bar@boobaz',
    '11:00 12:00 foo@bar',
    'rumpelratz foo@bar',
])
def invalid_raw_fact(request):
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




@pytest.fixture
def start_end_times():
    """Return a start/end-datetime-tuple."""
    end = datetime.datetime.now().time()
    start = end - datetime.timedelta(minutes=15)
    return (start, end)



# Refactor end


#@pytest.fixture
#def modified_category(category):
#    """
#    Return an existing category with garanteed changes vales from its
#    stored DB-instance.
#    """
#    category.name = category.name + 'foobar'
#    return category
#@pytest.fixture
#def set_of_existing_categories():
#    return [factories.AlchemyActivityFactory.create() for i in range(5)]
#@pytest.fixture
#def existing_activity():
#    return factories.AlchemyActivityFactory.create()

#@pytest.fixture
#def existing_activities_factory(alchemy_activity_factory):
#    def generate(amount=5, category=True):
#        """
#        Category True will cause a default factory run, using SubFactory
#        to create new categories associated with each activity.
#        If Category is False, activities will be created without a category.
#        """
#
#        result = []
#        for i in range(amount):
#            if category is False:
#                activity = alchemy_activity_factory.create(category=None)
#            else:
#                activity = alchemy_activity_factory()
#            result.append(activity.as_hamster())
#        return result
#    return generate

#@pytest.fixture
#def set_of_existing_activities(existing_activities_factory):
#    return existing_activities_factory(category=False)
#@pytest.fixture
#def existing_fact():
#    return factories.AlchemyFactFactory.create()

#@pytest.fixture
#def set_of_existing_facts():
#    return [factories.AlchemyFactFactory.create() for i in range(5)]

#@pytest.fixture
#def existing_fact_today():
#    now = datetime.datetime.now()
#    fact = factories.AlchemyFactFactory.create(
#        start=now - datetime.timedelta(hours=3),
#        end=now,
#    )
#    return fact
#
#
#@pytest.fixture
#def existing_fact_not_today(alchemy_fact_factory):
#    now = datetime.datetime.now()
#    fact = alchemy_fact_factory.create(
#        start=now - datetime.timedelta(days=2, hours=3),
#        end=now -datetime.timedelta(days=2)
#    )
#    return fact.as_hamster()
#



#@pytest.fixture(params=[
#    (None, False),
#    ('', False),
#    (category_name(), True),
#])
#def various_category_names(request):
#    return request.param


#@pytest.fixture(params=[None, category()])
#def various_categories(request):
#    return request.param


# Dbus-service

#@pytest.fixture(scope='session')
#@pytest.fixture(scope='class')
#def dbus_loop(request):
#    from gi.repository import GObject as gobject
#    request.cls.loop = gobject.MainLoop()
#
##@pytest.fixture(scope='session')
#@pytest.fixture
#def dbus_service(dbus_loop, controler):
#    service = hamster_dbus_service.HamsterDBusService(dbus_loop)
#    service.controler = controler
#    return service
#
#@pytest.fixture
#def category_name():
#    return faker.name()
#
#@pytest.fixture(scope='class', params=[
#    (None, False),
#    ('', False),
#    (category_name(), True),
#])
#def various_category_names(request):
#    request.cls.names = param
#
#@pytest.fixture(params=[None, category()])
#def various_categories(request):
#    return request.param
