# -*- encoding: utf-8 -*-
from __future__ import unicode_literals

import datetime

import factory
import faker
# from sqlalchemy import create_engine
# from . import common
from hamsterlib.backends.sqlalchemy import (AlchemyCategory, AlchemyActivity,
                                            AlchemyFact)
# from sqlalchemy.orm import sessionmaker, scoped_session


class AlchemyCategoryFactory(factory.alchemy.SQLAlchemyModelFactory):
    id = factory.Sequence(lambda n: n)
    name = factory.Faker('word')

    class Meta:
        model = AlchemyCategory
        # sqlalchemy_session = common.Session


class AlchemyActivityFactory(factory.alchemy.SQLAlchemyModelFactory):
    pk = factory.Sequence(lambda n: n)
    name = factory.Faker('sentence')
    category = factory.SubFactory(AlchemyCategoryFactory)
    deleted = False

    class Meta:
        model = AlchemyActivity
        # sqlalchemy_session = common.Session


class AlchemyFactFactory(factory.alchemy.SQLAlchemyModelFactory):
    pk = factory.Sequence(lambda n: n)
    activity = factory.SubFactory(AlchemyActivityFactory)
    start = faker.Faker().date_time()
    end = start + datetime.timedelta(hours=3)
    description = factory.Faker('paragraph')

    class Meta:
        model = AlchemyFact
        # sqlalchemy_session = common.Session
