# -*- encoding: utf-8 -*-

"""Factories providing randomized object instances."""

from __future__ import unicode_literals

import datetime

import factory
import faker
import fauxfactory
from future.utils import python_2_unicode_compatible
from hamster_lib import objects


@python_2_unicode_compatible
class CategoryFactory(factory.Factory):
    """Factory providing randomized ``hamster_lib.Category`` instances."""

    pk = None
    name = fauxfactory.gen_string('utf8')

    class Meta:
        model = objects.Category


@python_2_unicode_compatible
class ActivityFactory(factory.Factory):
    """Factory providing randomized ``hamster_lib.Activity`` instances."""

    pk = None
    name = factory.Faker('word')
    category = factory.SubFactory(CategoryFactory)
    deleted = False

    class Meta:
        model = objects.Activity


@python_2_unicode_compatible
class FactFactory(factory.Factory):
    """
    Factory providing randomized ``hamster_lib.Category`` instances.

    Instances have a duration of 3 hours.
    """

    pk = None
    activity = factory.SubFactory(ActivityFactory)
    start = faker.Faker().date_time()
    end = start + datetime.timedelta(hours=3)
    description = factory.Faker('paragraph')

    class Meta:
        model = objects.Fact
