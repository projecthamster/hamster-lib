# -*- encoding: utf-8 -*-

from __future__ import unicode_literals
from builtins import str
from future.utils import python_2_unicode_compatible

from sqlalchemy import Table, Column, ForeignKey, Integer, String, DateTime, Boolean, MetaData
# from sqlalchemy.sql.expression import and_
from sqlalchemy.orm import relationship, mapper  # , sessionmaker
from sqlalchemy import UniqueConstraint
from gettext import gettext as _

from hamsterlib import Category, Activity, Fact
from hamsterlib import objects


DEFAULT_STRING_LENGTH = 254


"""
This module provides the database layout.

Note:
    Our dedicated SQLAlchemy objects do not perform any general data validation
    as not to duplicate code. This is expected to be handled by the generic
    ``hamsterlib`` objects.
    If need for backend specific validation should arise, it could of cause be added
    here.
"""


@python_2_unicode_compatible
class AlchemyCategory(object):
    def __init__(self, hamster_category):
        """
        Initiate a new sqlalchemy activity instance.

        Args:
            hamster_category (hamsterlib.Category): A hamster category that is to
            be represented as a backend object.
        """
        if not isinstance(hamster_category, Category):
            raise TypeError(_(
                "hamsterlib.Category instance expected. Got {} instead".format(
                    type(hamster_category))
            ))
        self.pk = hamster_category.pk
        self.name = hamster_category.name

    def as_hamster(self):
        """Provide an convinient way to return it as a ``hamsterlib.Category`` instance."""
        return Category(
            pk=self.pk,
            name=self.name
        )

    def as_tuple(self, include_pk=True):
        """
        Provide a tuple representation of this categories relevant 'fields'.

        Args:
            include_pk (bool): Wether to include the instances pk or not. Note that if
            ``False`` ``tuple.pk = False``!

        Returns:
            CategoryTuple: Representing this categories values.
        """
        pk = self.pk
        if not include_pk:
            pk = False
        return objects.CategoryTuple(pk=pk, name=self.name)


@python_2_unicode_compatible
class AlchemyActivity(object):
    def __init__(self, hamster_activity):
        if not isinstance(hamster_activity, Activity):
            raise TypeError(_("Activity instance expected."))
        self.pk = hamster_activity.pk
        self.name = hamster_activity.name
        if hamster_activity.category:
            self.category = AlchemyCategory(hamster_activity.category)
        else:
            self.category = None
        self.deleted = hamster_activity.deleted

    def as_hamster(self):
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

    def as_tuple(self, include_pk=True):
        """
        Provide a tuple representation of this activities relevant 'fields'.

        Args:
            include_pk (bool): Wether to include the instances pk or not. Note that if
            ``False`` ``tuple.pk = False``!

        Returns:
            ActvityTuple: Representing this categories values.
        """
        pk = self.pk
        if not include_pk:
            pk = False
        return objects.ActivityTuple(pk, self.name, self.category, self.deleted)


@python_2_unicode_compatible
class AlchemyFact(object):
    def __init__(self, hamster_fact):
        if not isinstance(hamster_fact, Fact):
            raise TypeError(_("Fact instance expected."))
        self.pk = hamster_fact.pk
        self.activity = AlchemyActivity(hamster_fact.activity)
        self.start = hamster_fact.start
        self.end = hamster_fact.end
        self.description = hamster_fact.description
        # [FIXME]
        # We currently don't support tags on the actual db level, but for
        # compatibility we make believe here.
        self.tags = []

    def as_hamster(self):
        return Fact(
            pk=self.pk,
            activity=self.activity.as_hamster(),
            start=self.start,
            end=self.end,
            description=self.description
        )

    def as_dict(self):
        return {
            'pk': self.pk,
            'activity': self.activity,
            'start': self.start,
            'end': self.end,
            'description': self.description,
        }

    def as_tuple(self, include_pk=True):
        """
        Provide a tuple representation of this facts relevant 'fields'.

        Args:
            include_pk (bool): Wether to include the instances pk or not. Note that if
            ``False`` ``tuple.pk = False``!

        Returns:
            ActvityTuple: Representing this categories values.
        """
        pk = self.pk
        if not include_pk:
            pk = False
        return objects.FactTuple(pk, self.activity, self.start, self.end, self.description,
            self.tags)


metadata = MetaData()

categories = Table(
    'categories', metadata,
    Column('id', Integer, primary_key=True),
    Column('name', String(DEFAULT_STRING_LENGTH), unique=True)
)

mapper(AlchemyCategory, categories, properties={
    'pk': categories.c.id,
})

activities = Table(
    'activities', metadata,
    Column('id', Integer, primary_key=True),
    Column('name', String(500)),
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
    Column('description', String(500)),
)

mapper(AlchemyFact, facts, properties={
    'pk': facts.c.id,
    'activity': relationship(AlchemyActivity, backref='facts'),
})
