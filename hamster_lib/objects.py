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


from __future__ import unicode_literals

import datetime
from collections import namedtuple
from operator import attrgetter

from future.utils import python_2_unicode_compatible
from hamster_lib.helpers import time as time_helpers
from hamster_lib.helpers.helpers import parse_raw_fact
from six import text_type

# Named tuples used  to 'serialize' our object instances.
CategoryTuple = namedtuple('CategoryTuple', ('pk', 'name'))
TagTuple = namedtuple('TagTuple', ('pk', 'name'))
ActivityTuple = namedtuple('ActivityTuple', ('pk', 'name', 'category', 'deleted'))
FactTuple = namedtuple('FactTuple', ('pk', 'activity', 'start', 'end', 'description', 'tags'))


@python_2_unicode_compatible
class Category(object):
    """Storage agnostic class for categories."""

    def __init__(self, name, pk=None):
        """
        Initialize this instance.

        Args:
            name (str): The name of the category. May contain whitespace!
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
        self._name = text_type(name)

    def as_tuple(self, include_pk=True):
        """
        Provide a tuple representation of this categories relevant 'fields'.

        Args:
            include_pk (bool): Whether to include the instances pk or not. Note that if
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
            This is particularly useful if you want to compare a new ``Category`` instance
            with a freshly created backend instance. As the latter will probably have a
            primary key assigned now and so ``__eq__`` would fail.
        """
        if other:
            other = other.as_tuple(include_pk=False)
        else:
            other = None

        return self.as_tuple(include_pk=False) == other

    def __eq__(self, other):
        if other:
            if isinstance(other, CategoryTuple):
                pass
            else:
                other = other.as_tuple()
        else:
            other = None
        return self.as_tuple() == other

    def __hash__(self):
        """Naive hashing method."""
        return hash(self.as_tuple())

    def __str__(self):
        return text_type('{name}'.format(name=self.name))

    def __repr__(self):
        """Return an instance representation containing additional information."""
        return str('[{pk}] {name}'.format(pk=repr(self.pk), name=repr(self.name)))


@python_2_unicode_compatible
class Activity(object):
    """Storage agnostic class for activities."""

    def __init__(self, name, pk=None, category=None, deleted=False):
        """
        Initialize this instance.

        Args:
            name (str): This is the name of the activity. May contain whitespace!
            pk: The unique primary key used by the backend.
            category (Category): ``Category`` instance associated with this ``Activity``.
            deleted (bool): True if this ``Activity`` has been marked as deleted.

        Note:
            *Legacy hamster* basically treated ``(Activity.name, Category.name)`` as
            *composite keys*. As a consequence ``Activity.names`` themselves are not
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
        self._name = text_type(name)

    @classmethod
    def create_from_composite(cls, name, category_name, deleted=False):
        """
        Convenience method that allows creating a new instance providing the 'natural key'.

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
            include_pk (bool): Whether to include the instances pk or not. Note that if
            ``False`` ``tuple.pk = False``!

        Returns:
            ActivityTuple: Representing this activities values.
        """
        pk = self.pk
        if not include_pk:
            pk = False
        if self.category:
            category = self.category.as_tuple(include_pk=include_pk)
        else:
            category = None
        return ActivityTuple(pk=pk, name=self.name, category=category, deleted=self.deleted)

    def equal_fields(self, other):
        """
        Compare this instances fields with another activity. This excludes comparing the PK.

        Args:
            other (Activity): Activity to compare this instance with.

        Returns:
            bool: ``True`` if all fields but ``pk`` are equal, ``False`` if not.

        Note:
            This is particularly useful if you want to compare a new ``Activity`` instance
            with a freshly created backend instance. As the latter will probably have a
            primary key assigned now and so ``__eq__`` would fail.
        """
        return self.as_tuple(include_pk=False) == other.as_tuple(include_pk=False)

    def __eq__(self, other):
        if not isinstance(other, ActivityTuple):
            other = other.as_tuple()
        return self.as_tuple() == other

    def __hash__(self):
        """Naive hashing method."""
        return hash(self.as_tuple())

    def __str__(self):
        if self.category is None:
            string = '{name}'.format(name=self.name)
        else:
            string = '{name} ({category})'.format(
                name=self.name, category=self.category.name)
        return text_type(string)

    def __repr__(self):
        """Return an instance representation containing additional information."""
        if self.category is None:
            string = '[{pk}] {name}'.format(pk=repr(self.pk), name=repr(self.name))
        else:
            string = '[{pk}] {name} ({category})'.format(
                pk=repr(self.pk), name=repr(self.name), category=repr(self.category.name))
        return str(string)


@python_2_unicode_compatible
class Tag(object):
    """Storage agnostic class for tags."""

    def __init__(self, name, pk=None):
        """
        Initialize this instance.

        Args:
            name (str): The name of the tag. May contain whitespace!
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
        self._name = text_type(name)

    def as_tuple(self, include_pk=True):
        """
        Provide a tuple representation of this tags relevant 'fields'.

        Args:
            include_pk (bool): Whether to include the instances pk or not.
            Note that if ``False`` ``tuple.pk = False``!

        Returns:
            TagTuple: Representing this tags values.
        """
        pk = self.pk
        if not include_pk:
            pk = False
        return TagTuple(pk=pk, name=self.name)

    def equal_fields(self, other):
        """
        Compare this instances fields with another tag. This excludes comparing the PK.

        Args:
            other (Tag): Tag to compare this instance with.

        Returns:
            bool: ``True`` if all fields but ``pk`` are equal, ``False`` if not.

        Note:
            This is particularly useful if you want to compare a new ``Tag`` instance
            with a freshly created backend instance. As the latter will probably have a
            primary key assigned now and so ``__eq__`` would fail.
        """
        if other:
            other = other.as_tuple(include_pk=False)
        else:
            other = None

        return self.as_tuple(include_pk=False) == other

    def __eq__(self, other):
        if other:
            if isinstance(other, TagTuple):
                pass
            else:
                other = other.as_tuple()
        else:
            other = None
        return self.as_tuple() == other

    def __hash__(self):
        """Naive hashing method."""
        return hash(self.as_tuple())

    def __str__(self):
        return text_type('{name}'.format(name=self.name))

    def __repr__(self):
        """Return an instance representation containing additional information."""
        return str('[{pk}] {name}'.format(pk=repr(self.pk), name=repr(self.name)))


@python_2_unicode_compatible
class Fact(object):
    """Storage agnostic class for facts."""
    # [TODO]
    # There is some weird black magic still to be integrated from
    # ``store.db.Storage``. Among it ``__get_facts()``.
    #

    def __init__(self, activity, start, end=None, pk=None, description=None, tags=None):
        """
        Initiate our new instance.

        Args:
            activity (hamster_lib.Activity): Activity associated with this fact.
            start (datetime.datetime): Start datetime of this fact.
            end (datetime.datetime, optional): End datetime of this fact. Defaults to ``None``.
            pk (optional): Primary key used by the backend to identify this instance. Defaults
                to ``None``.
            description (str, optional): Additional information relevant to this singular fact.
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
        self.tags = set()
        if tags:
            self.tags = set(tags)

    @classmethod
    def create_from_raw_fact(cls, raw_fact, config=None):
        """
        Construct a new ``hamster_lib.Fact`` from a ``raw fact`` string.

        Please note that this just handles the parsing and construction of a new
        Fact including *new* ``Category`` and ``Activity`` instances.
        It will require a separate step to check this against the backend in order
        to figure out if those probably already exist!

        This approach has the benefit of providing this one single point of entry.
        Once any such raw fact has been turned in to a proper ``hamster_lib.Fact``
        we can rely on it having encapsulated all.

        As a consequence extra care has to be taken to mask/escape them.

        Args:
            raw_fact (str): Raw fact to be parsed.
            config (dict, optional): Controller config provided additional settings
                relevant for timeframe completion.

        Returns:
            hamster_lib.Fact: ``Fact`` object with data parsed from raw fact.

        Raises:
            ValueError: If we fail to extract at least ``start`` or ``activity.name``.
            ValueError: If ``end <= start``.

        """

        if not config:
            config = {'day_start': datetime.time(0, 0, 0)}

        extracted_components = parse_raw_fact(raw_fact)

        start, end = time_helpers.complete_timeframe(extracted_components['timeinfo'],
            config, partial=True)
        start, end = time_helpers.validate_start_end_range((start, end))

        activity_name = extracted_components.get('activity')
        if activity_name:
            activity = Activity(activity_name)
        else:
            raise ValueError(_("Unable to extract activity name"))

        category_name = extracted_components.get('category')
        if category_name:
            activity.category = Category(category_name)

        description = extracted_components['description']

        return cls(activity, start, end=end, description=description)

    @property
    def start(self):
        return self._start

    @start.setter
    def start(self, start):
        """
        Make sure that we receive a ``datetime.datetime`` instance.

        Args:
            start (datetime.datetime): Start datetime of this ``Fact``.

        Raises:
            TypeError: If we receive something other than a ``datetime.datetime`` (sub-)class
            or ``None``.
        """

        if start:
            if not isinstance(start, datetime.datetime):
                raise TypeError(_(
                    "You need to pass a ``datetime.datetime`` instance!"
                    " {type} instance received instead.".format(type=type(start))
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
        Make sure that we receive a ``datetime.datetime`` instance.

        Args:
            end (datetime.datetime): End datetime of this ``Fact``.

        Raises:
            TypeError: If we receive something other than a ``datetime.datetime`` (sub-)class
            or ``None``.
        """

        if end:
            if not isinstance(end, datetime.datetime):
                raise TypeError(_(
                    "You need to pass a ``datetime.datetime`` instance!"
                    " {type} instance received instead.".format(type=type(end))
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
            description = text_type(description)
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
            format (str): Specifies the output format. Valid choices are:
                * ``'%M'``: As minutes, rounded down.
                * ``'%H:%M'``: As 'hours:minutes'. rounded down.

        Returns:
            str: String representing this facts *duration* in the given format.capitalize

        Raises:
            ValueError: If a unrecognized format specifier is received.
        """
        seconds = int(self.delta.total_seconds())
        if format == '%M':
            result = text_type(int(seconds / 60))
        elif format == '%H:%M':
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
            This is merely a convenience / legacy property to stay in line with
            *legacy hamster*.
        """
        return self.start.date()

    @property
    def category(self):
        """For convenience only."""
        return self.activity.category

    def get_serialized_string(self):
        """
        Provide a canonical 'stringified' version of the fact.

        This is different from ``__str__`` as we may change what information is
        to be included in ``__str__`` anytime (and we may use localization
        etc ..) but this property guarantees that all relevant values will be
        encoded in the returned string in a canonical way. In that regard it
        is in a way a counterpart to ``Fact.create_from_raw_fact``.
        This also serves as a go-to reference implementation for 'what does a
        complete ``raw fact`` looks like'.

        Please be advised though that the ``raw_string`` used to create a
        ``Fact`` instance is not necessarily identical to this instance's
        ``serialized_string`` as the ``raw fact`` string may omit certain
        values which will be autocompleted while this property always returns
        a *complete* string.

        A complete serialized fact looks like this:
            ``2016-02-01 17:30 - 2016-02-01 18:10 making plans@world domination
            #tag 1 #tag 2, description``

            Please note that we are very liberal with allowing whitespace
            for ``Activity.name`` and ``Category.name``.

        Attention:
            ``Fact.tags`` is a set and hence unordered. In order to provide
            a deterministic canonical return string we will sort tags by name
            and list them alphabetically. This is purely cosmetic and does not
            imply any actual ordering of those facts on the instance level.

        Returns:
            text_type: Canonical string encoding all available fact info.
        """
        def get_times_string(fact):
            if fact.start:
                if fact.end:
                    result = '{start} - {end} '.format(
                        start=fact.start.strftime('%Y-%m-%d %H:%M'),
                        end=fact.end.strftime('%Y-%m-%d %H:%M')
                    )
                else:
                    result = '{} '.format(fact.start.strftime('%Y-%m-%d %H:%M'))
            else:
                result = ''
            return result

        def get_activity_string(fact):
            if fact.category:
                result = '{a.name}@{a.category.name}'.format(a=fact.activity)
            else:
                result = '{}'.format(fact.activity.name)
            return result

        tags = ''
        if self.tags:
            ordered_tags = sorted(list(self.tags), key=attrgetter('name'))
            tags = ' {}'.format(' '.join(['#{}'.format(tag.name) for tag in ordered_tags]))

        description = ''
        if self.description:
            description = ', {}'.format(self.description)

        result = '{times}{activity}{tags}{description}'.format(
            times=get_times_string(self),
            activity=get_activity_string(self),
            tags=tags,
            description=description
        )

        return text_type(result)

    def as_tuple(self, include_pk=True):
        """
        Provide a tuple representation of this facts relevant attributes.

        Args:
            include_pk (bool): Whether to include the instances pk or not. Note that if
            ``False`` ``tuple.pk = False``!

        Returns:
            hamster_lib.FactTuple: Representing this categories values.
        """
        pk = self.pk
        if not include_pk:
            pk = False
        return FactTuple(pk, self.activity.as_tuple(include_pk=include_pk), self.start,
            self.end, self.description,
            frozenset([tag.as_tuple(include_pk=include_pk) for tag in self.tags]))

    def equal_fields(self, other):
        """
        Compare this instances fields with another fact. This excludes comparing the PK.

        Args:
            other (Fact): Fact to compare this instance with.

        Returns:
            bool: ``True`` if all fields but ``pk`` are equal, ``False`` if not.

        Note:
            This is particularly useful if you want to compare a new ``Fact`` instance
            with a freshly created backend instance. As the latter will probably have a
            primary key assigned now and so ``__eq__`` would fail.
        """
        return self.as_tuple(include_pk=False) == other.as_tuple(include_pk=False)

    def __eq__(self, other):
        if not isinstance(other, FactTuple):
            other = other.as_tuple()

        return self.as_tuple() == other

    def __hash__(self):
        """Naive hashing method."""
        return hash(self.as_tuple())

    def __str__(self):
        result = text_type(self.activity.name)

        if self.category:
            result += "@%s" % text_type(self.category.name)

        if self.description or self.tags:
            # [FIXME]
            # Workaround until we address tags!
            result += ', {}'.format(text_type(self.description) or '')
            # result += "%s, %s" % (" ".join(["#%s" % tag for tag in self.tags]),
            #                    self.description or "")

        if self.start:
            start = self.start.strftime("%Y-%m-%d %H:%M")

        if self.end:
            end = self.end.strftime("%Y-%m-%d %H:%M")

        if self.start and self.end:
            result = '{} to {} {}'.format(start, end, result)
        elif self.start and not self.end:
            result = '{} {}'.format(start, result)

        return text_type(result)

    def __repr__(self):
        result = repr(self.activity.name)

        if self.category:
            result += "@%s" % repr(self.category.name)

        if self.description or self.tags:
            # [FIXME]
            # Workaround until we address tags!
            result += ', {}'.format(repr(self.description) or '')
            # result += "%s, %s" % (" ".join(["#%s" % tag for tag in self.tags]),
            #                    self.description or "")

        if self.start:
            start = repr(self.start.strftime("%Y-%m-%d %H:%M"))

        if self.end:
            end = repr(self.end.strftime("%Y-%m-%d %H:%M"))

        if self.start and self.end:
            result = '{} to {} {}'.format(start, end, result)
        elif self.start and not self.end:
            result = '{} {}'.format(start, result)

        return str(result)
