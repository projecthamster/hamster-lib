# -*- encoding: utf-8 -*-

from __future__ import unicode_literals
from builtins import str
from future.utils import python_2_unicode_compatible
import datetime
from gettext import gettext as _
import re
import logging

from . import objects


@python_2_unicode_compatible
class HamsterControl(object):
    """
    All mandatory config options are set as part of the contoler setup.
    Any client may overwrite those values. but we can always asume that the
    controler does have a value set.

    We will try hard to get through with at least always returning the object.
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
        self.lib_logger = self._get_logger()
        self.lib_logger.debug(_("HamsterControl initialized."))
        self.store = self._get_store()
        self.lib_logger.debug(_("Store ({}) initialized.".format(self.store)))
        # convinience attributes
        self.categories = self.store.categories
        self.activities = self.store.activities
        self.facts = self.store.facts

    def _get_store(self):
        """
        Setup the store used by this controler.

        This method is in charge off figuring out the store type, its instantiation
        as well as all additional configuration.
        """

        # [TODO]
        # Once proper backend-registration is available this should be streamlined.
        storetype = self.config['store']
        if storetype == 'sqlalchemy':
            from .backends.sqlalchemy import store
            result = store.SQLAlchemyStore(self.config['db-path'])
        else:
            raise KeyError(_("No valid storetype found."))
        return result

    def _get_logger(self):
        """
        Setup and configure the main logger.

        As the docs suggest we setup just a pseudo handler. Any client that actually
        wants to use logging needs to setup its required handlers itself.
        """

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
                category = objects.Category(category_name)
            else:
                category = None
        else:
            category, description = None, None

        activity = objects.Activity(activity_name, category=category)
        if not activity:
            activity = objects.Activity(activity_name, category=category)
            activity = self.activities.save(activity)

        return objects.Fact(activity, start, end=end, description=description)
