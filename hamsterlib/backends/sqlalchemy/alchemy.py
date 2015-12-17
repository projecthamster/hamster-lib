# -*- encoding: utf-8 -*-

from sqlalchemy import Table, Column, ForeignKey, Integer, String, DateTime, Boolean, MetaData
from sqlalchemy.sql.expression import and_
from sqlalchemy.orm import relationship, sessionmaker, mapper
from gettext import gettext as _
from hamsterlib import Category, Activity, Fact


DEFAULT_STRING_LENGTH = 254


class AlchemyCategory(Category):
    def __init__(self, hamster_category):
        if not isinstance(hamster_category, Category):
            raise TypeError(_("Category instance expected."))
        self.pk = hamster_category.pk
        self.name = hamster_category.name

    def as_hamster(self):
        return Category(
            pk=self.pk,
            name=self.name
        )

class AlchemyActivity(Activity):
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

    def as_dict(self):
        return {
            'pk': self.pk,
            'name': self.name,
            'category': self.category.pk,
            'deleted': self.deleted,
        }


class AlchemyFact(Fact):
    def __init__(self, hamster_fact):
        if not isinstance(hamster_fact, Fact):
            raise TypeError(_("Fact instance expected."))
        self.pk = hamster_fact.pk
        self.activity = AlchemyActivity(hamster_fact.activity)
        self.start = hamster_fact.start
        self.end = hamster_fact.end
        self.description = hamster_fact.description

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


metadata = MetaData()

categories = Table(
    'categories', metadata,
    Column('id', Integer, primary_key=True),
    Column('name', String(DEFAULT_STRING_LENGTH))
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
)

mapper(AlchemyActivity, activities, properties = {
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
