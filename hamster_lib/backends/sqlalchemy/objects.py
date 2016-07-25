# -*- encoding: utf-8 -*-

# Copyright (C) 2015-2016 Eric Goller <eric.goller@ninjaduck.solutions>

# This file is part of 'hamster-lib'.
#
# 'hamster-lib' is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# 'hamster-lib' is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with 'hamster-lib'.  If not, see <http://www.gnu.org/licenses/>.


"""
This module provides the database layout.

We inherit from our hamster objects in order to use the custom methods, making instance
comparisons so much easier.

The reason we are not mapping our native hamster objects directly is that this seems
to break the flexible plugable backend architecture as SQLAlchemy establishes the mapping
right away. This may be avoidable and should be investigates later on.

If those classes are instantiated manually any nested related instance needs to be added
manually.

Note:
    Our dedicated SQLAlchemy objects do not perform any general data validation
    as not to duplicate code. This is expected to be handled by the generic
    ``hamster_lib`` objects.
    If need for backend specific validation should arise, it could of cause be added
    here.
"""


from __future__ import unicode_literals

from future.utils import python_2_unicode_compatible
from hamster_lib import Activity, Category, Fact, Tag
from sqlalchemy import (Boolean, Column, DateTime, ForeignKey, Integer,
                        MetaData, Table, Unicode, UniqueConstraint)
from sqlalchemy.orm import mapper, relationship

DEFAULT_STRING_LENGTH = 254


@python_2_unicode_compatible
class AlchemyCategory(Category):
    def __init__(self, pk, name):
        """
        Initiate a new SQLAlchemy category instance.

        Raises:
            TypeError: If ``category`` is not a ``Category`` instance.
        """

        self.pk = pk
        self.name = name

    def as_hamster(self):
        """Provide an convenient way to return it as a ``hamster_lib.Category`` instance."""
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
            activity (hamster_lib.Activity): An activity that is to be represented
                as a backend instance.

        Raises:
            TypeError: If ``activity`` is not an ``Activity`` instance.
        """

        self.pk = pk
        self.name = name
        self.category = category
        self.deleted = deleted

    def as_hamster(self):
        """Provide an convenient way to return it as a ``hamster_lib.Activity`` instance."""
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
class AlchemyTag(Tag):
    def __init__(self, pk, name):
        """
        Initiate a new SQLAlchemy tag instance.

        Raises:
            TypeError: If ``category`` is not a ``Category`` instance.
        """

        self.pk = pk
        self.name = name

    def as_hamster(self):
        """Provide an convenient way to return it as a ``hamster_lib.Tag`` instance."""
        return Tag(
            pk=self.pk,
            name=self.name
        )


@python_2_unicode_compatible
class AlchemyFact(Fact):
    def __init__(self, pk, activity, start, end, description):
        """
        Initiate a new instance.

        Args:
            fact (hamster_lib.Fact): A fact that is to be represented
                as a backend instance.

        Raises:
            TypeError: If ``fact`` is not an ``Fact`` instance.
        """

        self.pk = pk
        self.activity = activity
        self.start = start
        self.end = end
        self.description = description
        # Tags can only be assigned after the fact has been created.
        self.tags = list()

    def as_hamster(self):
        """Provide an convenient way to return it as a ``hamster_lib.Fact`` instance."""
        return Fact(
            pk=self.pk,
            activity=self.activity.as_hamster(),
            start=self.start,
            end=self.end,
            description=self.description,
            tags=set([tag.as_hamster() for tag in self.tags]),
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

tags = Table(
    'tags', metadata,
    Column('id', Integer, primary_key=True),
    Column('name', Unicode(DEFAULT_STRING_LENGTH), unique=True)
)

mapper(AlchemyTag, tags, properties={
    'pk': tags.c.id,
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
    'tags': relationship(AlchemyTag, backref='facts', secondary=lambda: facttags),
})

facttags = Table(
    'facttags', metadata,
    Column('fact_id', Integer, ForeignKey(facts.c.id)),
    Column('tag_id', Integer, ForeignKey(tags.c.id)),
)
