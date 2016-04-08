# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

import datetime

import factory
import faker
from hamsterlib.backends.sqlalchemy.objects import (AlchemyActivity,
                                                    AlchemyCategory,
                                                    AlchemyFact)

from . import common


class AlchemyCategoryFactory(factory.alchemy.SQLAlchemyModelFactory):
    pk = factory.Sequence(lambda n: n)

    @factory.sequence
    def name(n):  # NOQA
        return '{name} - {key}'.format(name=factory.Faker('word'), key=n)

    class Meta:
        model = AlchemyCategory
        sqlalchemy_session = common.Session
        force_flush = True


class AlchemyActivityFactory(factory.alchemy.SQLAlchemyModelFactory):
    pk = factory.Sequence(lambda n: n)
    name = factory.Faker('sentence')
    category = factory.SubFactory(AlchemyCategoryFactory)
    deleted = False

    class Meta:
        model = AlchemyActivity
        sqlalchemy_session = common.Session
        force_flush = True


class AlchemyFactFactory(factory.alchemy.SQLAlchemyModelFactory):
    pk = factory.Sequence(lambda n: n)
    activity = factory.SubFactory(AlchemyActivityFactory)
    start = faker.Faker().date_time()
    end = start + datetime.timedelta(hours=3)
    description = factory.Faker('paragraph')
    tags = []

    class Meta:
        model = AlchemyFact
        sqlalchemy_session = common.Session
        force_flush = True
