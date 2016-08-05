# -*- encoding: utf-8 -*-

"""Fixtures in order to test the SQLAlchemy backend."""

from __future__ import unicode_literals

import datetime
import os

import fauxfactory
import pytest
from hamster_lib import Activity, Category, Fact, Tag
from hamster_lib.backends.sqlalchemy import objects
from hamster_lib.backends.sqlalchemy.storage import SQLAlchemyStore
from pytest_factoryboy import register
from sqlalchemy import create_engine

from . import common, factories

register(factories.AlchemyCategoryFactory)
register(factories.AlchemyActivityFactory)
register(factories.AlchemyTagFactory)
register(factories.AlchemyFactFactory)


# SQLAlchemy fixtures
@pytest.fixture
def alchemy_runner(request):
    """
    Provide a dedicated mock-db bound to a session object.

    The session object we refer to here is loaded at global test start as import
    and is also used by our ``AlchemyFactories``.

    After each testrun the ``Session.remove()`` makes sure that each test gets a new
    session and there is only one at a time.

    We do not actually clear any tables (for example with ``self.session.rollback()``
    but simply provide a all new database as part of this fixture. This is surely
    wasteful but does for now.

    Note:
        [Reference](http://factoryboy.readthedocs.org/en/latest/orms.html#sqlalchemy)
    """
    engine = create_engine('sqlite:///:memory:')
    objects.metadata.bind = engine
    objects.metadata.create_all(engine)
    common.Session.configure(bind=engine)

    def fin():
        common.Session.remove()

    request.addfinalizer(fin)


@pytest.fixture(params=[
    fauxfactory.gen_utf8(),
    fauxfactory.gen_alphanumeric(),
    ':memory:',
])
def db_path_parametrized(request, tmpdir):
    """Parametrized database paths."""
    if request.param == ':memory:':
        path = request.param
    else:
        path = os.path.join(tmpdir.strpath, request.param)
    return path


@pytest.fixture
def alchemy_config(request, base_config):
    """Provide a config that is suitable for sqlalchemy stores."""
    config = base_config.copy()
    config.update({
        'store': 'sqlalchemy',
        'db_engine': 'sqlite',
        'db_path': ':memory:',
    })
    return config


@pytest.fixture(params=(
    # sqlite
    {'db_engine': 'sqlite',
     'db_path': ':memory:'},
    # Non-sqlite
    {'db_engine': 'postgres',
     'db_host': fauxfactory.gen_ipaddr(),
     'db_port': fauxfactory.gen_integer(),
     'db_name': fauxfactory.gen_utf8(),
     'db_user': fauxfactory.gen_utf8(),
     'db_password': fauxfactory.gen_utf8()},
    {'db_engine': 'postgres',
     'db_host': fauxfactory.gen_ipaddr(),
     'db_name': fauxfactory.gen_utf8(),
     'db_user': fauxfactory.gen_utf8(),
     'db_password': fauxfactory.gen_utf8()},
))
def alchemy_config_parametrized(request, alchemy_config):
    """
    Provide a parametrized config that is suitable for sqlalchemy stores.

    We need to build our expectation dynamically if we want to use faked config values.
    """
    config = alchemy_config.copy()
    config.update(request.param)
    if request.param['db_engine'] == 'sqlite':
        expectation = '{engine}:///{path}'.format(
            engine=request.param['db_engine'], path=request.param['db_path'])
    else:
        port = request.param.get('db_port', '')
        if port:
            port = ':{}'.format(port)
        expectation = '{engine}://{user}:{password}@{host}{port}/{name}'.format(
            engine=request.param['db_engine'], user=request.param['db_user'],
            password=request.param['db_password'], host=request.param['db_host'],
            port=port, name=request.param['db_name'])
    return (config, expectation)


@pytest.fixture(params=(
    {'db_engine': None,
     'db_path': None},
    # sqlite
    {'db_engine': 'sqlite',
     'db_path': None},
    {'db_engine': 'sqlite',
     'db_path': ''},
    # Non-sqlite
    {'db_engine': 'postgres',
     'db_host': None,
     'db_name': fauxfactory.gen_utf8(),
     'db_user': fauxfactory.gen_utf8(),
     'db_password': fauxfactory.gen_alphanumeric()},
    {'db_engine': 'postgres',
     'db_host': fauxfactory.gen_ipaddr(),
     'db_name': '',
     'db_user': fauxfactory.gen_utf8(),
     'db_password': fauxfactory.gen_alphanumeric()},
    {'db_engine': 'postgres',
     'db_host': fauxfactory.gen_ipaddr(),
     'db_name': fauxfactory.gen_utf8(),
     'db_user': '',
     'db_password': fauxfactory.gen_alphanumeric()},
    {'db_engine': 'postgres',
     'db_host': fauxfactory.gen_ipaddr(),
     'db_name': fauxfactory.gen_utf8(),
     'db_user': fauxfactory.gen_utf8(),
     'db_password': ''}
))
def alchemy_config_missing_store_config_parametrized(request, alchemy_config):
    """Provide an alchemy config containing invalid key/value pairs for store initialization."""
    config = alchemy_config.copy()
    config.update(request.param)
    return config


@pytest.fixture
# [TODO] We probably want this to autouse=True
def alchemy_store(request, alchemy_runner, alchemy_config):
    """
    Provide a SQLAlchemyStore that uses our test-session.

    Note:
        The engine created as part of the store.__init__() goes simply unused.
    """
    return SQLAlchemyStore(alchemy_config, common.Session)


# We are sometimes tempted not using hamster-lib.objects at all. but as our tests
# expect them as input we need them!

# Instance sets
# Convenience fixtures that provide multitudes of certain alchemy instances.
@pytest.fixture
def set_of_categories(alchemy_category_factory):
    """Provide a number of perstent facts at once."""
    return [alchemy_category_factory() for i in range(5)]


@pytest.fixture
def set_of_tags(alchemy_tag_factory):
    """Provide a number of perstent facts at once."""
    return [alchemy_tag_factory() for i in range(5)]


@pytest.fixture
def set_of_alchemy_facts(start_datetime, alchemy_fact_factory):
    """
    Provide a multitude of generic persistent facts.

    Facts have one day offset from each other and last 20 minutes each.
    """
    start = start_datetime
    result = []
    for i in range(5):
        end = start + datetime.timedelta(minutes=20)
        fact = alchemy_fact_factory(start=start, end=end)
        result.append(fact)
        start = start + datetime.timedelta(days=1)
    return result


# Fallback hamster object and factory fixtures. Unless we know how factories
# interact.
@pytest.fixture
def category_factory(request, name):
    """Provide a ``hamster_lib.Category`` factory."""
    def generate():
        return Category(name, None)
    return generate


@pytest.fixture
def category(request, category_factory):
    """Provide a randomized ``hamster_lib.Category`` instance."""
    return category_factory()


@pytest.fixture
def tag_factory(request, name):
    """Provide a ``hamster_lib.Tag`` factory."""
    def generate():
        return Tag(name, None)
    return generate


@pytest.fixture
def tag(request, tag_factory):
    """Provide a randomized ``hamster_lib.Tag`` instance."""
    return tag_factory()


@pytest.fixture
def activity_factory(request, name, category_factory):
    """
    Provide a ``hamster_lib.Activity`` factory.

    Note:
        * The returned activity will have a *new* category associated as well.
        * Values are randomized but *not parametrized*.
    """
    def generate():
        category = category_factory()
        return Activity(name, pk=None, category=category, deleted=False)
    return generate


@pytest.fixture
def activity(request, activity_factory):
    """Provide a randomized ``hamster_lib.Activity`` instance."""
    return activity_factory()


@pytest.fixture
def fact_factory(request, activity_factory, tag_factory, start_end_datetimes, description):
    """
    Provide a ``hamster_lib.Fact`` factory.

    Note:
        * The returned fact will have a *new* activity (and by consequence category)
          associated as well.
        * Values are randomized but *not parametrized*.
    """
    def generate():
        activity = activity_factory()
        tags = set([tag_factory() for i in range(1)])
        start, end = start_end_datetimes
        fact = Fact(activity, start, end, pk=None, description=description, tags=tags)
        return fact
    return generate


@pytest.fixture
def fact(request, fact_factory):
    """Return a randomized ``hamster_lib.Fact`` instance."""
    return fact_factory()
