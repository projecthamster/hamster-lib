# -*- encoding: utf-8 -*-
from __future__ import unicode_literals

import datetime
import calendar
from gettext import gettext as _
import re
import logging


from . import objects


"""
NOTE:
    * names are case sensitive. this should be documentend for search/filter.
    * It looks like the dbus client assume PKs to be > 0 and uses 0 as marker
    for failure. Would be great if we can change that on the frontend instead
    of working around that.
"""

class HamsterControl(object):
    """
    All mandatory config options are set as part of the contoler setup.
    Any client may overwrite those values. but we can always asume that the
    controler does have a value set.

    We will try hard to get thorugh with at least always returning the object.
    We should be able to change only the internal service code to then
    decompose it into its required weired format.

    We were compelled to make attach CRUD-methods to our activity, category
    and fact objects. But as all of those depend on access to the store
    anyway they seem to be best be placed here as a central hub.

    Generic CRUD-actions is to be delegated to our store. The Controler itself
    provides general timetracking functions so that our clients do not have to.
    """

    def __init__(self, config):
        self.config = config
        self.lib_logger = self.__get_logger()
        self.lib_logger.debug(_("HamsterControl initialized"))
        self.unsorted_localized = self.config['unsorted_localized']
        self.store = self.__get_store(self.config['store'])
        # convinience attributes
        self.categories = self.store.categories
        self.activities = self.store.activities
        self.facts = self.store.facts

    def __get_store(self, storetype):
        if storetype == 'sqlalchemy':
            from .backends.sqlalchemy import store
            result = store.SQLAlchemyStore(self.config['db-path'])
        else:
            raise KeyError(_("No valid storetype found."))
        return result

    def __get_logger(self):
        lib_logger = logging.getLogger(__name__)
        lib_logger.addHandler(logging.NullHandler())
        lib_logger.addHandler(logging.NullHandler())
        return lib_logger


    def parse_time_info(self, time_info):
        """
        Generic parser for time(-range) information.

        Note:
            * We assume that timedeltas are relative to ``now``.
            * Relative times always return just ``(start, None)``.
            * It seems that the original implementation behaves rather weired
              with regards to the end-datetime fallback. When there is no
              end-date we try using the start date. If there is no start date
              we use today. However, at this point it is not quite clear
              what an enddate without an start date is supposed to mean.
              Should we rather throw an exception?

        Args:
            time_info (str): Time(-range) information. Space seperated list of
                [start-date] [start-time] [end-date] [end-time].

        Returns:
            tuple(): Tuple of (start, end) datetime objects. Each may be
                ``None``.
        """
        def get_time(time, fallback):
            """
            Convert a time string to a ``datetime.time`` instance.

            Note:
                Besides the regular builtin functionality this also handeles
                our fallback behaviour for empty strings.

            Args:
                time (str): Date in the format "hh:mm".
                fallback (datetime.time()): Fallback, if no time is specified.

            Returns:
                datetime.time(): ``time`` instance or ``None``.
            """
            result = fallback
            if time:
                result = datetime.datetime.strptime(time.strip(), "%H:%M").time()
            return result

        def get_date(date, fallback):
            """
            Convert a date string to a ``datetime.date`` instance.

            In addition to the builtin method we this also handles empty
            strings.

            Args:
                date (str): Date in the format "yyyy-mm-dd"
                fallback (datetime.date()): Fallback, if no date is specified.

            Returns:
                datetime.date(): ``date`` instance or ``None``.
            """
            result = fallback
            if date:
                result = datetime.datetime.strptime(date.strip(), "%Y-%m-%d").date()
            return result

        patterns = (
            '^((?P<relative>-\d.+)?|('
            '(?P<date1>\d{4}-\d{2}-\d{2})?'
            '(?P<time1> ?\d{2}:\d{2})?'
            '(?P<dash> ?-)?'
            '(?P<date2> ?\d{4}-\d{2}-\d{2})?'
            '(?P<time2> ?\d{2}:\d{2})?)?)'
            '(?P<rest>\D.+)?$'
        )
        match = re.compile(patterns).match(time_info)

        if not match:
            result = (None, None)
        else:
            fragments = match.groupdict()
            rest = (fragments['rest'] or '').strip()

            # Bail out early on relative minutes
            if fragments['relative']:
                delta = datetime.timedelta(minutes=int(fragments['relative']))
                result = (datetime.datetime.now() - delta, None)
            else:
                start, end = None, None

                start_date = fragments.get('date1', None)
                start_time = fragments.get('time1', None)

                end_date = fragments.get('date2', None)
                end_time = fragments.get('time2', None)

                if start_date or start_time:
                    # Only  one of the two fallbacks should trigger at max!
                    start_date = get_date(start_date, datetime.date.today())
                    start = datetime.datetime.combine(
                        start_date,
                        get_time(start_time, datetime.time())
                    )

                if end_date or end_time:
                    # Only  one of the two fallbacks should trigger at max!
                    end = datetime.datetime.combine(
                        get_date(end_date, start_date),
                        get_time(end_time, datetime.time())
                    )
                result = (start, end)
        return result


    def parse_raw_fact(self, raw_fact):
        """
        Take a raw fact string and turn it into a proper Fact-instance.
        We need to handle this within the controler as we need access to a
        store in order to resolve any relationships (activities/categories).


        See serialiazed_name for details on the raw_fact format.
        As far as we can tell right now ther are a couple of clear seperatiors
        for our raw-string.
        '@' --> [time-info] activity @ remains
        ',' --> @category',' description remains

        As a consequence extra care has to be taken to mask/escape them.

        :param str raw_fact: Raw fact.

        :return: Fact object with data taken from raw fact.
        :rtype: object.Fact
        """

        def at_split(string):
            """
            Return everything in front of the '@'-symbol, if it was used.
            """
            result = string.split('@')
            length = len(result)
            if length == 1:
                front = result[0].strip()
                back = None
            elif length == 2:
                front, back = tuple(result)
                front = front.strip()
                back = back.strip()
            else:
                raise ValueError(
                    _("Our raw_fact may not allow more than one '@'-symbol.")
                )
            return (front, back)

        def time_activity_split(string):
            """
            If there is any time information, it will be seperated from
            the activity-name by a whitespace. We use that to split those
            with confidence.

            Return (time, activity).
            """

            # [FIXME]
            # Right now we do only allow for words as activity, we want
            # this to be more flexible!
            result = string.rsplit(' ', 1)
            length = len(result)
            if length == 1:
                time = None
                activity = result[0].strip()
            else:
                time, activity = tuple(result)
                time = time.strip()
                activity = activity.strip()
            return (time, activity)

        def parse_time_info(string):
            """
            Eventually all parsing should happen by hamsterlib, so that this
            functionality does not have to be replicated by all frontends
            (originaly I was/am a great fan of 'parsing and handing over
            valid/typed input is a frontend job').

            Returns (start_time, end_time) as datetime.datetime objects,
            where end_time may be None.
            """

            now = datetime.datetime.now()

            delta_re = re.compile("^-[0-9]{1,3}$")
            time_re = re.compile("^([0-1]?[0-9]|[2][0-3]):([0-5][0-9])$")
            time_range_re = re.compile("^([0-1]?[0-9]|[2][0-3]):([0-5][0-9])-([0-1]?[0-9]|[2][0-3]):([0-5][0-9])$")

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
            Return the caregory-fragment.
            The remains may include more ','s which seems to be alright with
            the specs. :(

            Return (category, description)
            """

            result = tuple(string.split(',', 1))
            length = len(result)

            if length == 1:
                category = result[0]
                category = category.strip()
                description = None
            else:
                category, description = tuple(result)
                category = category.strip()
                description = description.strip()
            return (category.strip(), description)


        front, back = at_split(raw_fact)

        time_info, activity_name = time_activity_split(front)
        if time_info:
            start, end = parse_time_info(time_info)
        else:
            start = None
            end = None

        if back:
            category_name, description = comma_split(back)
            if category_name:
                category = objects.Category(category_name)
            else:
                category = None
        else:
            category = None
            description = None

        activity = objects.Activity(activity_name, category=category)
        if not activity:
            activity = objects.Activity(activity_name, category=category)
            activity = self.activities.save(activity)


        return objects.Fact(activity, start, end=end, description=description)

    def get_today_facts(self):
        """Return all facts for today, while respecting midnight settings.

        Because we want to refer to our settings about start/end time of a day
        we can not merely delegate this to the frontend.

        This used to be delegated to the store class, which is nuts, as this
        is just a specialized version of get_facts.

        :return: List of facts
        :rtype: list
        """
        today = datetime.date.today()

        return self.facts.get_all(
            start=datetime.datetime(today.year, today.month, today.day, 0, 0, 1),
            end=datetime.datetime(today.year, today.month, today.day, 23, 59, 59)
        )
