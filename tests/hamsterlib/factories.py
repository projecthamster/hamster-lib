# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

import datetime

import factory
import faker
import fauxfactory
from future.utils import python_2_unicode_compatible
from hamsterlib import objects


@python_2_unicode_compatible
class CategoryFactory(factory.Factory):

    class Meta:
        model = objects.Category

    pk = None
    name = fauxfactory.gen_string('utf8')


@python_2_unicode_compatible
class ActivityFactory(factory.Factory):

    class Meta:
        model = objects.Activity

    pk = None
    name = factory.Faker('word')
    category = factory.SubFactory(CategoryFactory)
    deleted = False


@python_2_unicode_compatible
class FactFactory(factory.Factory):
    pk = None
    activity = factory.SubFactory(ActivityFactory)
    start = faker.Faker().date_time()
    end = start + datetime.timedelta(hours=3)
    description = factory.Faker('paragraph')

    class Meta:
        model = objects.Fact
