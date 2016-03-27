# -*- encoding: utf-8 -*-

from __future__ import unicode_literals
from future.utils import python_2_unicode_compatible
from builtins import str

import factory
import faker
import datetime

from hamsterlib import objects
# from hamsterlib import backends

# from . import common


@python_2_unicode_compatible
class CategoryFactory(factory.Factory):

    class Meta:
        model = objects.Category

    pk = None
    name = factory.Faker('word')

@python_2_unicode_compatible
class ActivityFactory(factory.Factory):
    pk = None
    name = factory.Faker('word')
    category = factory.SubFactory(CategoryFactory)
    deleted = False

    class Meta:
        model = objects.Activity


@python_2_unicode_compatible
class FactFactory(factory.Factory):
    pk = None
    activity = factory.SubFactory(ActivityFactory)
    start = faker.Faker().date_time()
    end = start + datetime.timedelta(hours=3)
    description = factory.Faker('paragraph')

    class Meta:
        model = objects.Fact

0
