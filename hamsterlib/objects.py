# -*- encoding: utf-8 -*-

from __future__ import unicode_literals
from future.utils import python_2_unicode_compatible
from builtins import str
from collections import namedtuple

from gettext import gettext as _
import datetime
# from calendar import timegm
# import re


CategoryTuple = namedtuple('CategoryTuple', ('pk', 'name'))
ActivityTuple = namedtuple('CategoryTuple', ('pk', 'name', 'category', 'deleted'))
FactTuple = namedtuple('FactTuple', ('pk', 'activity', 'start', 'end', 'description', 'tags'))


@python_2_unicode_compatible
class Category(object):
    """Storage agnostic class for categories."""

    def __init__(self, name, pk=None):
        """
        Initialize this instance.

        Args:
            name (str): This categories name.
            pk: The unique primary key used by the backend.
        """

        self.pk = pk
        self.name = name

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        if not name:
            # Catching ``None`` and ``empty string``.
            raise ValueError(_("You need to specify a name."))
        self._name = str(name)

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
        return CategoryTuple(pk=pk, name=self.name)

    def equal_fields(self, other):
        """
        Compare this instances fields with another category. This excludes comparing the PK.

        Args:
            other (Category): Category to compare this instance with.

        Returns:
            bool: ``True`` if all fields but ``pk`` are equal, ``False`` if not.

        Note:
            This is particulary usefull if you want to compare a new ``Category`` instance
            with a freshly created backend instance. As the latter will propably have a
            primary key assigned now and so ``__eq__`` would fail.
        """
        return self.as_tuple(include_pk=False) == other.as_tuple(include_pk=False)

    def __eq__(self, other):
        return self.as_tuple() == other.as_tuple()

    def __str__(self):
        return '{name}'.format(name=self.name)

    def __repr__(self):
        return '[{pk}] {name}'.format(pk=self.pk, name=self.name)


@python_2_unicode_compatible
class Activity(object):
    """Storage agnostic class for activities."""

    def __init__(self, name, pk=None, category=None, deleted=False):
        """
        Initialite this instance.

        Args:
            name (str): This activities name.
            pk: The unique primary key used by the backend.
            category (Category): ``Category`` instance associated with this ``Activity``.
            deleted (bool): True if this ``Activity`` has been marked as deleted.

        Note:
            *Legacy hamster* basicly treated ``(Activity.name, Category.name)`` as
            *composite keys*. As a consequene ``Activity.names`` themselfs are not
            unique. They are only in combination with their associated categories name.
        """
        # [TODO]
        # Elaborate on the consequences of the deleted flag.

        self.pk = pk
        self.name = name
        self.category = category
        self.deleted = bool(deleted)

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        if not name:
            # Catching ``None``
            raise ValueError(_("You need to specify a name."))
        self._name = str(name)

    @classmethod
    def create_from_composite(cls, name, category_name, deleted=False):
        """
        Convinience method that allows creating a new instance providing the 'natural key'.

        Args:
            name (str): This activities name.
            category_name (str): Name of the associated category.
            deleted (bool): True if this ``Activity`` has been marked as deleted.

        Returns:
            Activity: A new ``Activity`` instance.

        Note:
            * Should future iterations extend ``Category`` this may turn problematic.
            * This method does not allow to specify a primary key as it is intended only
            for new instances, not ones retrieved by the backend.
        """
        category = Category(category_name)
        return cls(name, category=category, deleted=deleted)

    def as_tuple(self, include_pk=True):
        """
        Provide a tuple representation of this activities relevant 'fields'.

        Args:
            include_pk (bool): Wether to include the instances pk or not. Note that if
            ``False`` ``tuple.pk = False``!

        Returns:
            ActivityTuple: Representing this activities values.
        """
        pk = self.pk
        if not include_pk:
            pk = False
        return ActivityTuple(pk=pk, name=self.name, category=self.category,
            deleted=self.deleted)

    def equal_fields(self, other):
        """
        Compare this instances fields with another activity. This excludes comparing the PK.

        Args:
            other (Activity): Activity to compare this instance with.

        Returns:
            bool: ``True`` if all fields but ``pk`` are equal, ``False`` if not.

        Note:
            This is particulary usefull if you want to compare a new ``Activity`` instance
            with a freshly created backend instance. As the latter will propably have a
            primary key assigned now and so ``__eq__`` would fail.
        """
        return self.as_tuple(include_pk=False) == other.as_tuple(include_pk=False)

    def __eq__(self, other):
        return self.as_tuple() == other.as_tuple()

    def __str__(self):
        if self.category is None:
            string = '{name}'.format(name=self.name)
        else:
            string = '{name} ({category})'.format(name=self.name, category=self.category.name)
        return string

    def __repr__(self):
        if self.category is None:
            string = '[{pk}] {name}'.format(pk=self.pk, name=self.name)
        else:
            string = '[{pk}] {name} ({category})'.format(
                pk=self.pk, name=self.name, category=self.category.name)
        return string


@python_2_unicode_compatible
class Fact(object):
    """Storage agnostic class for facts.

    Note:
        There is some weired black magic still to be integrated from
        ``store.db.Storage``. Among it ``__get_facts()``.
    """

    def __init__(self, activity, start, end=None, pk=None, description=None, tags=None):
        """
        Initiate our new instance.

        Args:
            activity (hamsterlib.Activity): Activity associated with this fact.
            start (datetime.datetime): Start datetime of this fact.
            end (datetime.datetime, optional): End datetime of this fact. Defaults to ``None``.
            pk (optional): Primary key used by the packend to identify this instance. Defaults
                to ``None``.
            description (str, oprional): Additional information relevant to this singular fact.
                Defaults to ``None``.
            tags (Iterable, optional): Iterable of ``strings`` identifying *tags*. Defaults to
                ``None``.

        Note:
            * For ``start`` and ``end``: Seconds will be stored, but are ignored for all
            intends and purposes.
        """

        self.pk = pk
        self.activity = activity
        self.start = start
        self.end = end
        self.description = description
        if tags is None:
            tags = []
        self.tags = list(tags)

    @property
    def start(self):
        return self._start

    @start.setter
    def start(self, start):
        """
        Make sure that we recieve a ``datetime.datetime`` instance.

        Args:
            start (datetime.datetime): Start datetime of this ``Fact``.

        Raises:
            TypeError: If we recieve something other than a ``datetime.datetime`` (sub-)class
            or ``None``.
        """

        if start:
            if not isinstance(start, datetime.datetime):
                raise TypeError(_(
                    "You need to pass a ``datetime.datetime`` instance!"
                    " {type} instance recieved instead.".format(type=type(start))
                ))
        else:
            start = None
        self._start = start

    @property
    def end(self):
        return self._end

    @end.setter
    def end(self, end):
        """
        Make sure that we recieve a ``datetime.datetime`` instance.

        Args:
            end (datetime.datetime): End datetime of this ``Fact``.

        Raises:
            TypeError: If we recieve something other than a ``datetime.datetime`` (sub-)class
            or ``None``.
        """

        if end:
            if not isinstance(end, datetime.datetime):
                raise TypeError(_(
                    "You need to pass a ``datetime.datetime`` instance!"
                    " {type} instance recieved instead.".format(type=type(end))
                ))
        else:
            end = None
        self._end = end

    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, description):
        """"
        Normalize all descriptions that evaluate to ``False``. Store everything else as string.
        """
        if description:
            description = str(description)
        else:
            description = None
        self._description = description

    @property
    def delta(self):
        """
        Provide the offset of start to end for this fact.

        Returns:
            datetime.timedelta or None: Difference between start- and end datetime.
                If we only got a start datetime, return ``None``.
        """
        result = None
        if self.end:
            result = self.end - self.start
        return result

    def get_string_delta(self, format='%M'):
        """
        Return a string representation of ``Fact().delta``.

        Args:
            format (str): Specifies the output format. Valid choises are:
                * ``'%M'``: As minutes, rounded down.
                * ``'%H:%M'``: As 'hours:minutes'. rounded down.

        Returns:
            str: String representing this facts *duration* in the given format.capitalize

        Raises:
            ValueError: If a inrecognized format specifier is recieved.
        """
        seconds = int(self.delta.total_seconds())
        if format == '%M':
            result = str(int(seconds / 60))
        elif format == '%H:%M':
            print(seconds)
            result = '{hours:02d}:{minutes:02d}'.format(hours=int(seconds / 3600),
                minutes=int((seconds % 3600) / 60))
        else:
            raise ValueError(_("Got invalid format argument."))
        return result

    @property
    def date(self):
        """
        Return the date the fact has started.

        Returns:
            datetime.datetime: The date the fact has started.

        Note:
            This is merely a convinience / legacy property to stay in line with
            *legacy hamster*.
        """
        return self.start.date()

    @property
    def serialized_name(self):
        """
        Provide a string representation of this fact.

        Returns:
            str: String serializing all relevant fields of this fact.

        Note:
            * Pattern: [<start>-<end>] <activity_name>[@<category_name>, <description_text>]
            * Time format information from hamster-cli:
                * 'YYYY-MM-DD hh:mm:ss': If date is missing, it will default to today.
                    If time is missing, it will default to 00:00 for start time and 23:59 for
                    end time.
                * '-minutes': Relative time in minutes from the current date and time.
            * Our version of this method does not contain time information!
        """
        result = str(self.activity.name)

        if self.category:
            result += "@%s" % self.category.name

        if self.description or self.tags:
            result += "%s, %s" % (" ".join(["#%s" % tag for tag in self.tags]),
                               self.description or "")
        return result

    @property
    def category(self):
        """For convinience only."""
        return self.activity.category

    def as_tuple(self, include_pk=True):
        """
        Provide a tuple representation of this facts relevant 'fields'.

        Args:
            include_pk (bool): Wether to include the instances pk or not. Note that if
            ``False`` ``tuple.pk = False``!

        Returns:
            FactTuple: Representing this categories values.
        """
        pk = self.pk
        if not include_pk:
            pk = False
        return FactTuple(pk, self.activity, self.start, self.end, self.description, self.tags)

    def equal_fields(self, other):
        """
        Compare this instances fields with another fact. This excludes comparing the PK.

        Args:
            other (Fact): Fact to compare this instance with.

        Returns:
            bool: ``True`` if all fields but ``pk`` are equal, ``False`` if not.

        Note:
            This is particulary usefull if you want to compare a new ``Fact`` instance
            with a freshly created backend instance. As the latter will propably have a
            primary key assigned now and so ``__eq__`` would fail.
        """
        return self.as_tuple(include_pk=False) == other.as_tuple(include_pk=False)

    def __eq__(self, other):
        return self.as_tuple() == other.as_tuple()

    def __str__(self):
        time = self.start.strftime("%d-%m-%Y %H:%M")
        if self.end:
            time = "%s - %s" % (time, self.end.strftime("%H:%M"))
        return "%s %s" % (time, self.serialized_name)

    def __repr__(self):
        time = self.start.strftime("%d-%m-%Y %H:%M")
        if self.end:
            time = "%s - %s" % (time, self.end.strftime("%H:%M"))
        return "%s %s" % (time, self.serialized_name)
