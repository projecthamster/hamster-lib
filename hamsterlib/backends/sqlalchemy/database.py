from sqlalchemy import Table, Column, ForeignKey, Integer, Unicode, DateTime, Boolean, MetaData
from sqlalchemy.orm import relationship, mapper
from sqlalchemy import UniqueConstraint
from hamsterlib import Category, Activity, Fact

DEFAULT_STRING_LENGTH = 254

metadata = MetaData()

categories = Table(
    'categories', metadata,
    Column('id', Integer, primary_key=True),
    Column('name', Unicode(DEFAULT_STRING_LENGTH), unique=True)
)

activities = Table(
    'activities', metadata,
    Column('id', Integer, primary_key=True),
    Column('name', Unicode(500)),
    Column('deleted', Boolean),
    Column('category_id', Integer, ForeignKey(categories.c.id)),
    UniqueConstraint('name', 'category_id')
)

facts = Table(
    'facts', metadata,
    Column('id', Integer, primary_key=True),
    Column('start', DateTime),
    Column('end', DateTime),
    Column('activity_id', Integer, ForeignKey(activities.c.id)),
    Column('description', Unicode(500)),
)

mapper(Category, categories, properties={
    'pk': categories.c.id,
})

mapper(Activity, activities, properties={
    'pk': activities.c.id,
    'category': relationship(Category, backref='activities'),
})

mapper(Fact, facts, properties={
    'pk': facts.c.id,
    'activity': relationship(Activity, backref='facts'),
})
