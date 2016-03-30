# -*- encoding: utf-8 -*-

from __future__ import unicode_literals
from builtins import str

import pytest

# from sqlalchemy import orm, create_engine
import datetime

# from . import factories

from ... import factories

from hamsterlib.backends.sqlalchemy import (AlchemyCategory, AlchemyActivity, AlchemyFact,
    SQLAlchemyStore)


@pytest.fixture#(scope='function')
def alchemy_store(request):
    return SQLAlchemyStore('sqlite:///:memory:')


@pytest.fixture
def existing_category_factory(request, alchemy_store):
    def generate(*args, **kwargs):
        category = factories.CategoryFactory.build(*args, **kwargs)
        alchemy_category = AlchemyCategory(category)
        alchemy_store.session.add(alchemy_category)
        alchemy_store.session.commit()
        return alchemy_category
    return generate


@pytest.fixture(params=[True, False])
def existing_category_valid_parametrized(request, existing_category_factory,
        name_string_valid_parametrized):
    """
    Provide a parametrized persisent category fixture.

    This fixuture will represent a wide array of potential name charsets as well
    as a ``category=None`` version.
    """

    if request.param:
        result = existing_category_factory(name=name_string_valid_parametrized)
    else:
        result = None
    return result


@pytest.fixture
def existing_category_valid_without_none_parametrized(request, existing_category_factory,
        name_string_valid_parametrized):
    """
    Provide a parametrized persisent category fixture.

    This fixuture will represent a wide array of potential name charsets as well
    but not ``category=None``.
    """
    return existing_category_factory(name=name_string_valid_parametrized)


@pytest.fixture
def existing_category(existing_category_factory):
    return existing_category_factory()


@pytest.fixture
def set_of_existing_categories(existing_category_factory):
    return [existing_category_factory() for i in range(5)]


@pytest.fixture
def existing_activity_factory(request, alchemy_store, category_factory):
    """
    Custom factory to provide a new persistent activity.

    You may pass additional ``args`` or ``kwargs`` just like you would with a regular
    factory-boy factory in order to fine tune instance parameters.

    Note:
        We use this a more transparent workaround to make sure that the new
        instance is attached to the right session until we are confident we know
        how to use factory boys own session assignment.
    """
    def generate(*args, **kwargs):
        activity = factories.ActivityFactory.build(*args, **kwargs)
        alchemy_activity = AlchemyActivity(activity)
        alchemy_activity.category = AlchemyCategory(category_factory())
        alchemy_store.session.add(alchemy_activity)
        alchemy_store.session.commit()
        return alchemy_activity
    return generate


@pytest.fixture
def existing_activity(existing_activity_factory, existing_category_factory):
    """
    Provide a singe persisent activity.

    Note:
        Refer to factory docstring for details about why we implement this ourself.
    """
    return existing_activity_factory()


@pytest.fixture
def existing_activity_valid_parametrized(existing_activity_factory, existing_category_factory,
        name_string_valid_parametrized, deleted_valid_parametrized):
    """
    Provide a parametrized persistent activity fixture.

    We make heavy usage of parametrized sub fixtures to generate a wide variation of
    possible persistent activities. Please refer to each used fixtures docstring
    for details on what is covered.
    """

    # [TODO]
    # Parametrize category. In particular cover cases where category=None

    return existing_activity_factory(name=name_string_valid_parametrized,
        deleted=deleted_valid_parametrized)


@pytest.fixture
def existing_fact_factory(request, alchemy_store, existing_activity_factory):
    def generate(*args, **kwargs):
        fact = factories.FactFactory.build(*args, **kwargs)
        alchemy_fact = AlchemyFact(fact)
        alchemy_fact.activity = existing_activity_factory()
        alchemy_store.session.add(alchemy_fact)
        alchemy_store.session.commit()
        return alchemy_fact
    return generate


@pytest.fixture
def existing_fact(existing_fact_factory):
    return existing_fact_factory()


@pytest.fixture
def existing_fact_valid_parametrized(alchemy_store, existing_fact_factory,
        existing_activity_valid_parametrized, description_valid_parametrized,
        tag_list_valid_parametrized):
    fact = existing_fact_factory(description=description_valid_parametrized,
        tags=tag_list_valid_parametrized)
    alchemy_store.session.commit()
    return fact



@pytest.fixture
def start_datetime():
    return datetime.datetime.now()


@pytest.fixture
def set_of_existing_facts(start_datetime, existing_fact_factory):
    start = start_datetime
    result = []
    for i in range(5):
        end = start + datetime.timedelta(minutes=20)
        fact = existing_fact_factory(start=start, end=end)
        result.append(fact)
        start = start + datetime.timedelta(days=1)
    return result


# @pytest.fixture
# def set_of_existing_facts(existing_fact_factory):
#     return [existing_fact_factory() for i in range(5)]
