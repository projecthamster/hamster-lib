# -*- encoding: utf-8 -*-
from __future__ import unicode_literals

import datetime
# import calendar
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
        return lib_logger

    def parse_raw_fact(self, raw_fact):
        """
        Take a raw fact string and turn it into a proper Fact-instance.

        We need to handle this within the controler as we need access to a
        store in order to resolve any relationships (activities/categories).

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
