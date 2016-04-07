# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from future.utils import python_2_unicode_compatible
from hamsterlib import Activity, Category, Fact
from sqlalchemy import (Boolean, Column, DateTime, ForeignKey, Integer,
                        MetaData, Table, Unicode, UniqueConstraint)
from sqlalchemy.orm import mapper, relationship

DEFAULT_STRING_LENGTH = 254


"""
This module provides the database layout.

We inherit from our hamster objects in order to use the custom methods, making insstance
comparissions so much easier.

The reason we are not mapping our native hamster objects directly is that this seems
to break the flexible plugable backend architecture as SQLAlchemy establishes the mapping
right away. This may be avoidable and should be investigates later on.

If those classes are instanciated manually any nested related instance needs to be added
manually.

Note:
    Our dedicated SQLAlchemy objects do not perform any general data validation
    as not to duplicate code. This is expected to be handled by the generic
    ``hamsterlib`` objects.
    If need for backend specific validation should arise, it could of cause be added
    here.
"""


@python_2_unicode_compatible
class AlchemyCategory(Category):
    def __init__(self, pk, name):
        """
        Initiate a new sqlalchemy activity instance.

        Args:
            category (hamsterlib.Category): A hamster category that is to
                be represented as a backend object.

        Raises:
            TypeError: If ``category`` is not a ``Category`` instance.
        """

        self.pk = pk
        self.name = name

    def as_hamster(self):
        """Provide an convinient way to return it as a ``hamsterlib.Category`` instance."""
        return Category(
            pk=self.pk,
            name=self.name
        )


@python_2_unicode_compatible
class AlchemyActivity(Activity):
    def __init__(self, pk, name, category, deleted):
        """
        Initiate a new instance.

        Args:
            activity (hamsterlib.Activity): An activity that is to be represented
                as a backend instance.

        Raises:
            TypeError: If ``activity`` is not an ``Activity`` instance.
        """

        self.pk = pk
        self.name = name
        self.category = category
        self.deleted = deleted

    def as_hamster(self):
        """Provide an convinient way to return it as a ``hamsterlib.Activity`` instance."""
        if self.category:
            category = self.category.as_hamster()
        else:
            category = None
        return Activity(
            pk=self.pk,
            name=self.name,
            category=category,
            deleted=self.deleted
        )


@python_2_unicode_compatible
class AlchemyFact(Fact):
    def __init__(self, pk, activity, start, end, description, tags):
        """
        Initiate a new instance.

        Args:
            fact (hamsterlib.Fact): A fact that is to be represented
                as a backend instance.

        Raises:
            TypeError: If ``fact`` is not an ``Fact`` instance.
        """

        self.pk = pk
        self.activity = activity
        self.start = start
        self.end = end
        self.description = description
        # [FIXME]
        # We currently don't support tags on the actual db level!
        self.tags = tags

    def as_hamster(self):
        """Provide an convinient way to return it as a ``hamsterlib.Fact`` instance."""
        return Fact(
            pk=self.pk,
            activity=self.activity.as_hamster(),
            start=self.start,
            end=self.end,
            description=self.description,
        )


metadata = MetaData()

categories = Table(
    'categories', metadata,
    Column('id', Integer, primary_key=True),
    Column('name', Unicode(DEFAULT_STRING_LENGTH), unique=True)
)

mapper(AlchemyCategory, categories, properties={
    'pk': categories.c.id,
})

activities = Table(
    'activities', metadata,
    Column('id', Integer, primary_key=True),
    Column('name', Unicode(500)),
    Column('deleted', Boolean),
    Column('category_id', Integer, ForeignKey(categories.c.id)),
    UniqueConstraint('name', 'category_id')
)

mapper(AlchemyActivity, activities, properties={
    'pk': activities.c.id,
    'category': relationship(AlchemyCategory, backref='activities'),
})

facts = Table(
    'facts', metadata,
    Column('id', Integer, primary_key=True),
    Column('start', DateTime),
    Column('end', DateTime),
    Column('activity_id', Integer, ForeignKey(activities.c.id)),
    Column('description', Unicode(500)),
)

mapper(AlchemyFact, facts, properties={
    'pk': facts.c.id,
    'activity': relationship(AlchemyActivity, backref='facts'),
})
