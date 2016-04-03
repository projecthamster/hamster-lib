# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

import datetime
import re
from collections import namedtuple

from future.utils import python_2_unicode_compatible
from six import text_type

CategoryTuple = namedtuple('CategoryTuple', ('pk', 'name'))
ActivityTuple = namedtuple('ActivityTuple', ('pk', 'name', 'category', 'deleted'))
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
        self._name = text_type(name)

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

    def __str__(self):
        return '{name}'.format(name=self.name)

    def __repr__(self):
        return str('[{pk}] {name}'.format(pk=repr(self.pk), name=repr(self.name)))


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
        self._name = text_type(name)

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
            This is particulary usefull if you want to compare a new ``Activity`` instance
            with a freshly created backend instance. As the latter will propably have a
            primary key assigned now and so ``__eq__`` would fail.
        """
        return self.as_tuple(include_pk=False) == other.as_tuple(include_pk=False)

    def __eq__(self, other):
        if not isinstance(other, ActivityTuple):
            other = other.as_tuple()
        return self.as_tuple() == other

    def __str__(self):
        if self.category is None:
            string = '{name}'.format(name=self.name)
        else:
            string = '{name} ({category})'.format(name=self.name, category=self.category.name)
        return string

    def __repr__(self):
        if self.category is None:
            string = str('[{pk}] {name}').format(pk=repr(self.pk), name=repr(self.name))
        else:
            string = str('[{pk}] {name} ({category})').format(
                pk=repr(self.pk), name=repr(self.name), category=repr(self.category.name))
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

    @classmethod
    def create_from_raw_fact(cls, raw_fact):
        """
        Construct a new ``hamsterlib.Fact`` from a ``raw fact`` string.

        Please note that this just handles the parsing and construction of a new
        Fact including *new* ``Category`` and ``Activity`` instances.
        It will require a seperate step to check this against the backend in order
        to figure out if those propably already exist!

        This aproach has the benefit of providing this one single point of entry.
        Once any such raw fact has been turned in to a proper ``hamstserlib.Fact``
        we can rely on it having encapsulated all.

        See serialiazed_name for details on the raw_fact format.
        As far as we can tell right now ther are a couple of clear seperators
        for our raw-string.
        '@' --> [time-info] activity @ remains
        ',' --> @category',' description remains

        As a consequence extra care has to be taken to mask/escape them.

        Args:
            raw_fact (str): Raw fact to be parsed.

        Returns:
            hamsterlib.Fact: ``Fact`` object with data parsesd from raw fact.
        """

        def at_split(string):
            """
            Return everything in front of the (leftests) '@'-symbol, if it was used.

            Args:
                string (str):  The string to be parsed.

            Returns:
                touple: (front, back) representing the substings before and after the
                    most left ``@`` symbol. If no such symbol was present at all,
                    ``back=None``. Both substrings have been trimmed of any leading
                    and tailing whilespaces.

            Note:
                If our string contains multiple ``@`` symbols, all but the most left
                one will be treated as part of the regular ``back`` string.
                This allows for usage of the symbol in descriptions, categories and tags.
            """
            result = string.split('@', 1)
            length = len(result)
            if length == 1:
                front, back = result[0].strip(), None
            else:
                front, back = result
                front, back = front.strip(), back.strip()
            return (front, back)

        def time_activity_split(string):
            """
            Seperate time information from activity name.

            Args:
                string (str): Expects a string ``<timeinformation> <activity>``.

            Returns
                tuple: ``(time, activity)``. If no seperating whitespace was found,
                    ``time=None``. Both substrings will have their leading/tailing
                    whitespaces trimmed.

            Note:
                * We seperate at the most left whitespace. That means that our
                timeinformation substring may very well include additional
                whitespaces.
                * If no whitespace is found, we consider the entire string to be
                the activity name.
            """

            result = string.rsplit(' ', 1)
            length = len(result)
            if length == 1:
                time, activity = None, result[0].strip()
            else:
                time, activity = tuple(result)
                time, activity = time.strip(), activity.strip()
            return (time, activity)

        def parse_time_info(string):
            """
            Parse time info of a given raw fact.

            Args:
                string (str): String representing the timeinfo. The string is expected
                    to have one of the following three formats: ``-offset in minutes``,
                    ``HH:MM`` or ``HH:MM-HH:MM``.

            Returns:
                tuple: ``(start_time, end_time)`` tuple, where both elements are
                    ``datetime.dateime`` instances. If no end time was extracted
                    ``end_time=None``.

            Note:
                This parsing method is is informed by the legacy hamster
                ``hamster.lib.parse_fact``. It seems that here we only extract
                times that then are understood relative to today.
                This seems significanty less powerfull that our
                ``hamsterlib.helpers.parse_time_range`` method which itself has been
                taken from legacy hamsters ``hamster-cli``.
            """
            # [FIXME]
            # Check if ther is any rationale against using
            # ``hamsterlib.helpers.parse_time_range`` instead.

            now = datetime.datetime.now()

            delta_re = re.compile("^-[0-9]{1,3}$")
            time_re = re.compile("^([0-1]?[0-9]|[2][0-3]):([0-5][0-9])$")
            time_range_re = re.compile(
                "^([0-1]?[0-9]|[2][0-3]):([0-5][0-9])-([0-1]?[0-9]|[2][0-3]):([0-5][0-9])$")

            if delta_re.match(string):
                start = now + datetime.timedelta(minutes=int(string))
                result = (start, None)
            elif time_re.match(string):
                start = datetime.datetime.combine(
                    now.date(),
                    datetime.datetime.strptime(string, "%H:%M").time()
                )
                result = (start, None)
            elif time_range_re.match(string):
                start, end = string.split("-")
                start = datetime.datetime.combine(
                    now.date(),
                    datetime.datetime.strptime(start, "%H:%M").time()
                )
                end = datetime.datetime.combine(
                    now.date(),
                    datetime.datetime.strptime(end, "%H:%M").time()
                )
                result = (start, end)
            else:
                raise ValueError(_(
                    "You seem to have passed some time information, however"
                    " we were unable to identify the format it was given in."
                ))
            return result

        def comma_split(string):
            """
            Split string at the most left comma.

            Args:
                string (str): String to be processed. At this stage this should
                    look something like ``<Category>, <Description>


            Returns
                tuple: (category_and_tags, description). Both substrings have their
                    leading/tailing whitespaces removed.
                    ``category_and_tags`` may include >=0 tags indicated by a leading ``#``.
                    As we have used the most left ``,`` to seperate both substrings that
                    means that categories and tags can not contain any ``,`` but the
                    description text may contain as many as wished.
            """

            result = tuple(string.split(',', 1))
            length = len(result)
            if length == 1:
                category, description = result[0].strip(), None
            else:
                category, description = tuple(result)
                category, description = category.strip(), description.strip()
            return (category.strip(), description)

        front, back = at_split(raw_fact)

        time_info, activity_name = time_activity_split(front)
        if time_info:
            start, end = parse_time_info(time_info)
        else:
            start, end = None, None

        if back:
            category_name, description = comma_split(back)
            if category_name:
                category = Category(category_name)
            else:
                category = None
        else:
            category, description = None, None

        activity = Activity(activity_name, category=category)
        return cls(activity, start, end=end, description=description)

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
        result = text_type(self.activity.name)

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
        # [FIXME] Once tags are implemented, they need to be added here!
        return FactTuple(pk, self.activity.as_tuple(include_pk=include_pk), self.start,
            self.end, self.description, [])

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
        if not isinstance(other, FactTuple):
            other = other.as_tuple()

        return self.as_tuple() == other

    def __str__(self):
        time = self.start.strftime("%d-%m-%Y %H:%M")
        if self.end:
            time = "%s - %s" % (time, self.end.strftime("%H:%M"))
        return "%s %s" % (time, self.serialized_name)

    def __repr__(self):
        time = self.start.strftime("%d-%m-%Y %H:%M")
        if self.end:
            time = str('%s - %s') % (time, self.end.strftime("%H:%M"))
        return str('%s %s') % (time, repr(self.serialized_name))
