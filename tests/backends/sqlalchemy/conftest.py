import pytest

#from sqlalchemy import orm, create_engine
import datetime

from . import factories

from ... import factories

from hamsterlib.backends.sqlalchemy import (AlchemyCategory, AlchemyActivity,
                                            AlchemyFact, SQLAlchemyStore)


@pytest.fixture
def alchemy_store(request):
    return SQLAlchemyStore('sqlite:///:memory:')

@pytest.fixture
def existing_category_factory(request, alchemy_store):
    def generate():
        category = factories.CategoryFactory.build()
        alchemy_category = AlchemyCategory(category)
        alchemy_store.session.add(alchemy_category)
        alchemy_store.session.commit()
        return alchemy_category
    return generate


@pytest.fixture
def existing_category(existing_category_factory):
    return existing_category_factory()


@pytest.fixture
def set_of_existing_categories(existing_category_factory):
    return [existing_category_factory() for i in range(5)]


@pytest.fixture
def existing_activity_factory(request, alchemy_store):
    def generate():
        activity = factories.ActivityFactory.build()
        alchemy_activity = AlchemyActivity(activity)
        alchemy_store.session.add(alchemy_activity)
        alchemy_store.session.commit()
        return alchemy_activity
    return generate


@pytest.fixture
def existing_activity(existing_activity_factory):
    return existing_activity_factory()


@pytest.fixture
def existing_fact_factory(request, alchemy_store):
    def generate(**kwargs):
        fact = factories.FactFactory.build(**kwargs)
        alchemy_fact = AlchemyFact(fact)
        alchemy_store.session.add(alchemy_fact)
        alchemy_store.session.commit()
        return alchemy_fact
    return generate


@pytest.fixture
def existing_fact(existing_fact_factory):
    return existing_fact_factory()

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



#@pytest.fixture
#def set_of_existing_facts(existing_fact_factory):
#    return [existing_fact_factory() for i in range(5)]
