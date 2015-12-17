# -*- encoding: utf-8 -*-
from __future__ import unicode_literals

import factory
import faker
import datetime

from hamsterlib import objects
from hamsterlib import backends

#from . import common


class CategoryFactory(factory.Factory):
    pk = None
    name = factory.Faker('word')

    class Meta:
        model = objects.Category


class ActivityFactory(factory.Factory):
    pk = None
    name = factory.Faker('word')
    category = factory.SubFactory(CategoryFactory)
    deleted = False

    class Meta:
        model = objects.Activity


class FactFactory(factory.Factory):
    pk = None
    activity = factory.SubFactory(ActivityFactory)
    start = faker.Faker().date_time()
    end = start + datetime.timedelta(hours=3)
    description = factory.Faker('paragraph')

    class Meta:
        model = objects.Fact


