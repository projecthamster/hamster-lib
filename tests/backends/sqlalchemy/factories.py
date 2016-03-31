# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

import datetime

import factory
import faker
from . import common
from hamsterlib import Category, Activity, Fact


class CategoryFactory(factory.alchemy.SQLAlchemyModelFactory):
    id = factory.Sequence(lambda n: n)
    name = factory.Faker('word')

    class Meta:
        model = Category
        sqlalchemy_session = common.Session


class ActivityFactory(factory.alchemy.SQLAlchemyModelFactory):
    pk = factory.Sequence(lambda n: n)
    name = factory.Faker('sentence')
    category = factory.SubFactory(CategoryFactory)
    deleted = False

    class Meta:
        model = Activity
        sqlalchemy_session = common.Session


class FactFactory(factory.alchemy.SQLAlchemyModelFactory):
    pk = factory.Sequence(lambda n: n)
    activity = factory.SubFactory(ActivityFactory)
    start = faker.Faker().date_time()
    end = start + datetime.timedelta(hours=3)
    description = factory.Faker('paragraph')

    class Meta:
        model = Fact
        sqlalchemy_session = common.Session
