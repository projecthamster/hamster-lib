# -*- encoding: utf-8 -*-

# Copyright (C) 2015-2016 Eric Goller <elbenfreund@DenkenInEchtzeit.net>

# This file is part of 'hamsterlib'.
#
# 'hamsterlib' is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# 'hamsterlib' is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with 'hamsterlib'.  If not, see <http://www.gnu.org/licenses/>.


"""
Module containing base classes intended to be inherited from when implementing storage backends.

Note:
    * This is propably going to be replaced by a ``ABC``-bases solution.
    * Basic sanity checks could be done here then. This would mean we just need to test
        them once and our actual backends focus on the CRUD implementation.
"""


from __future__ import unicode_literals

import datetime
import logging
import os
import pickle

import hamsterlib
import hamsterlib.helpers as helpers
from future.utils import python_2_unicode_compatible
from hamsterlib import objects


@python_2_unicode_compatible
class BaseStore(object):
    """
    A controller store provides unified interfaces to interact with our stored entities.

    ``self.logger`` provides a dedicated logger instance for any storage related logging.
    If you want to make use of it, just setup and attach your handlers and you are ready to go.
    Be advised though, ``self.logger`` will be very verbose as on ``debug`` it will log any
    method call and often even their returned instances.
    """

    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger('hamsterlib.storage')
        self.logger.addHandler(logging.NullHandler())
        self.categories = BaseCategoryManager(self)
        self.activities = BaseActivityManager(self)
        self.facts = BaseFactManager(self)

    def cleanup(self):
        """
        Any backend specific teardown code that needs to be executed before
        we shut down gracefully.
        """
        raise NotImplementedError


@python_2_unicode_compatible
class BaseManager(object):
    """Base class for all object managers."""

    def __init__(self, store):
        self.store = store


@python_2_unicode_compatible
class BaseCategoryManager(BaseManager):
    """Base class defining the minimal API for a CategoryManager implementation."""

    def save(self, category):
        """
        Save a Category to our selected backend.
        Internal code decides whether we need to add or update.

        Args:
            category (hamsterlib.Category): Category instance to be saved.

        Returns:
            hamsterlib.Category: Saved Category

        Raises:
            TypeError: If the ``category`` parameter is not a valid ``Category`` instance.
        """

        if not isinstance(category, objects.Category):
            message = _("You need to pass a hamster category")
            self.store.logger.debug(message)
            raise TypeError(message)

        self.store.logger.debug(_("'{}' has been received.".format(category)))

        # We don't check for just ``category.pk`` because we don't want to make
        # assumptions about the PK being an int or being >0.
        if category.pk or category.pk == 0:
            result = self._update(category)
        else:
            result = self._add(category)
        return result

    def get_or_create(self, category):
        """
        Check if we already got a category with that name, if not create one.

        This is a convenience method as it seems sensible to rather implement
        this once in our controller than having every client implementation
        deal with it anew.

        It is worth noting that the lookup completely ignores any PK contained in the
        passed category. This makes this suitable to just create the desired Category
        and pass it along. One way or the other one will end up with a persisted
        db-backed version.

        Args:
            category (hamsterlib.Category or None): The categories.

        Returns:
            hamsterlib.Category or None: The retrieved or created category. Either way,
                the returned Category will contain all data from the backend, including
                its primary key.
        """

        self.store.logger.debug(_("'{}' has been received.'.".format(category)))
        if category:
            try:
                category = self.get_by_name(category)
            except KeyError:
                category = objects.Category(category)
                category = self._add(category)
        else:
            # We want to allow passing ``category=None``, so we normalize here.
            category = None
        return category

    def _add(self, category):
        """
        Add a ``Category`` to our backend.

        Args:
            category (hamsterlib.Category): ``Category`` to be added.

        Returns:
            hamsterlib.Category: Newly created ``Category`` instance.

        Raises:
            ValueError: When the category name was already present! It is supposed to be
            unique.
            ValueError: If category passed already got an PK. Indicating that update would
                be more appropriate.

        Note:
            * Legacy version stored the proper name as well as a ``lower(name)`` version
            in a dedicated field named ``search_name``.
        """
        raise NotImplementedError

    def _update(self, category):
        """
        Update a ``Categories`` values in our backend.

        Args:
            category (hamsterlib.Category): Category to be updated.

        Returns:
            hamsterlib.Category: The updated Category.

        Raises:
            KeyError: If the ``Category`` can not be found by the backend.
            ValueError: If the ``Category().name`` is already being used by
                another ``Category`` instance.
            ValueError: If category passed does not have a PK.
        """
        raise NotImplementedError

    def remove(self, category):
        """
        Remove a category.

        Any ``Activity`` referencing the passed category will be set to
        ``Activity().category=None``.

        Args:
            category (hamsterlib.Category): Category to be updated.

        Returns:
            None: If everything went ok.

        Raises:
            KeyError: If the ``Category`` can not be found by the backend.
            TypeError: If category passed is not an hamsterlib.Category instance.
            ValueError: If category passed does not have an pk.
        """
        raise NotImplementedError

    def get(self, pk):
        """
        Get an ``Category`` by its primary key.

        Args:
            pk (int): Primary key of the ``Category`` to be fetched.

        Returns:
            hamsterlib.Category: ``Category`` with given primary key.

        Raises:
            KeyError: If no ``Category`` with this primary key can be found by the backend.
        """

        raise NotImplementedError

    def get_by_name(self, name):
        """
        Look up a category by its name.

        Args:
            name (str): Unique name of the ``Category`` to we want to fetch.

        Returns:
            hamsterlib.Category: ``Category`` with given name.

        Raises:
            KeyError: If no ``Category`` with this name was found by the backend.
        """
        raise NotImplementedError

    def get_all(self):
        """
        Return a list of all categories.

        Returns:
            list: List of ``Categories``, ordered by ``lower(name)``.
        """
        raise NotImplementedError


@python_2_unicode_compatible
class BaseActivityManager(BaseManager):
    """Base class defining the minimal API for a ActivityManager implementation."""
    def save(self, activity):
        """
        Save a ``Activity`` to the backend.

        This public method decides if it calls either ``_add`` or ``_update``.

        Args:
            activity (hamsterlib.Activity): ``Activity`` to be saved.

        Returns:
            hamsterlib.Activity: The saved ``Activity``.
        """

        self.store.logger.debug(_("'{}' has been received.".format(activity)))
        if activity.pk or activity.pk == 0:
            result = self._update(activity)
        else:
            result = self._add(activity)
        return result

    def get_or_create(self, activity):
        """
        Convenience method to either get an activity matching the specs or create a new one.

        Args:
            activity (hamsterlib.Activity): The activity we want.

        Returns:
            hamsterlib.Activity: The retrieved or created activity
        """
        self.store.logger.debug(_("'{}' has been received.".format(activity)))
        try:
            activity = self.get_by_composite(activity.name, activity.category)
        except KeyError:
            activity = self.save(hamsterlib.Activity(activity.name, category=activity.category,
                deleted=activity.deleted))
        return activity

    def _add(self, activity):
        """
        Add a new ``Activity`` instance to the database.

        Args:
            activity (hamsterlib.Activity): The ``Activity`` to be added.

        Returns:
            hamsterlib.Activity: The newly created ``Activity``.

        Raises:
            ValueError: If the passed activity has a PK.
            ValueError: If the category/activity.name combination to be added is
                already present in the db.

        Note:
            According to ``storage.db.Storage.__add_activity``: when adding a new activity
            with a new category, this category does not get created but instead this
            activity.category=None. This makes sense as categories passed are just ids, we
            however can pass full category objects. At the same time, this approach allows
            to add arbitrary category.id as activity.category without checking their existence.
            this may lead to db anomalies.
        """
        raise NotImplementedError

    def _update(self, activity):
        """
        Update values for a given activity.

        Which activity to refer to is determined by the passed PK new values
        are taken from passed activity as well.

        Args:
            activity (hamsterlib.Activity): Activity to be updated.

        Returns:
            hamsterlib.Activity: Updated activity.
        Raises:
            ValueError: If the new name/category.name combination is already taken.
            ValueError: If the the passed activity does not have a PK assigned.
            KeyError: If the the passed activity.pk can not be found.

        Note:
            Seems to modify ``index``.
        """

        raise NotImplementedError

    def remove(self, activity):
        """
        Remove an ``Activity`` from the database.import

        If the activity to be removed is associated with any ``Fact``-instances,
        we set ``activity.deleted=True`` instead of deleting it properly.
        If it is not, we delete it from the backend.

        Args:
            activity (hamsterlib.Activity): The activity to be removed.

        Returns:
            bool: True

        Raises:
            KeyError: If the given ``Activity`` can not be found in the database.

        Note:
            Should removing the last activity of a category also trigger category
            removal?
        """
        raise NotImplementedError

    def get(self, pk):
        """
        Return an activity based on its primary key.

        Args:
            pk (int): Primary key of the activity

        Returns:
            hamsterlib.Activity: Activity matching primary key.

        Raises:
            KeyError: If the primary key can not be found in the database.
        """
        raise NotImplementedError

    def get_by_composite(self, name, category):
        """
        Lookup for unique 'name/category.name'-composite key.

        This method utilizes that to return the corresponding entry or None.

        Args:
            name (str): Name of the ``Activities`` in question.
            category (hamsterlib.Category or None): ``Category`` of the activities. May be None.

        Returns:
            hamsterlib.Activity: The corresponding activity

        Raises:
            KeyError: If the composite key can not be found.
        """

        raise NotImplementedError

    def get_all(self, category=None, search_term=''):
        """
        Return all matching activities.

        Args:
            category (hamsterlib.Category, optional): Limit activities to this category.
                Defaults to ``None``.
            search_term (str, optional): Limit activities to those matching this string
                a substring in their name. Defaults to ``empty string``.

        Returns:
            list: List of ``hamsterlib.Activity`` instances matching constrains. This list
                is ordered by ``Activity.name``.

        Note:
            * This method combines legacy ``storage.db.__get_activities`` and
                ``storage.db.____get_category_activities``.
            * Can search terms be prefixed with 'not'?
            * Original implementation in ``hamster.storage.db.__get_activities`` returns
                activity names converted to lowercase!
            * Does exclude activities with ``deleted=True``.
        """
        raise NotImplementedError


@python_2_unicode_compatible
class BaseFactManager(BaseManager):
    """Base class defining the minimal API for a FactManager implementation."""
    def save(self, fact):
        """
        Save a Fact to our selected backend.

        Unlike the private ``_add`` and ``_update`` methods, ``save`` enforces that
        the config given ``fact_min_delta`` is enforced.

        Args:
            fact (hamsterlib.Fact): Fact to be saved. Needs to be complete otherwise
            this will fail.

        Returns:
            hamsterlib.Fact: Saved Fact.

        Raises:
            ValueError: If ``fact.delta`` is smaller than ``self.store.config['fact_min_delta']``-
        """
        self.store.logger.debug(_("Fact: '{}' has been received.".format(fact)))

        fact_min_delta = datetime.timedelta(seconds=int(self.store.config['fact_min_delta']))
        if fact.delta and (fact.delta < fact_min_delta):
            message = _(
                "The passed facts delta is shorter than the mandatory value of {} seconds"
                " specified in your config.".format(fact_min_delta)
            )
            self.store.logger.error(message)
            raise ValueError(message)

        if fact.pk or fact.pk == 0:
            result = self._update(fact)
        elif fact.end is None:
            result = self._start_tmp_fact(fact)
        else:
            result = self._add(fact)
        return result

    def _add(self, fact):
        """
        Add a new ``Fact`` to the backend.

        Args:
            fact (hamsterlib.Fact): Fact to be added.

        Returns:
            hamsterlib.Fact: Added ``Fact``.

        Raises:
            ValueError: If the passed fact has a PK assigned. New facts should not have one.
            ValueError: If the timewindow is already occupied.
        """
        raise NotImplementedError

    def _update(self, fact):
        """
        Update and existing fact with new values.

        Args:
            fact (hamsterlib.fact): Fact instance holding updated values.

        Returns:
            hamsterlib.fact: Updated Fact

        Raises:
            KeyError: if a Fact with the relevant PK could not be found.
            ValueError: If the the passed activity does not have a PK assigned.
            ValueError: If the timewindow is already occupied.
        """
        raise NotImplementedError

    def remove(self, fact):
        """
        Remove a given ``Fact`` from the backend.

        Args:
            fact (hamsterlib.Fact): ``Fact`` instance to be removed.

        Returns:
            bool: Success status

        Raises:
            ValueError: If fact passed does not have an pk.
            KeyError: If the ``Fact`` specified could not be found in the backend.
        """
        raise NotImplementedError

    def get(self, pk):
        """
        Return a Fact by its primary key.

        Args:
            pk (int): Primary key of the ``Fact to be retrieved``.

        Returns:
            hamsterlib.Fact: The ``Fact`` corresponding to the primary key.

        Raises:
            KeyError: If primary key not found in the backend.
        """
        raise NotImplementedError

    def get_all(self, start=None, end=None, filter_term=''):
        """
        Return all facts within a given timeframe (beginning of start_date
        end of end_date) that match given search terms.

        Args:
            start_date (datetime.datetime, optional): Consider only Facts starting at or after
                this date. Alternatively you can also pass a ``datetime.datetime`` object
                in which case its own time will be considered instead of the default ``day_start``
                or a ``datetime.time`` which will be considered as today.
                Defaults to ``None``.
            end_date (datetime.datetime, optional): Consider only Facts ending before or at
                this date. Alternatively you can also pass a ``datetime.datetime`` object
                in which case its own time will be considered instead of the default ``day_start``
                or a ``datetime.time`` which will be considered as today.
                Defaults to ``None``.
            filter_term (str, optional): Only consider ``Facts`` with this string as part of their
                associated ``Activity.name``

        Returns:
            list: List of ``Facts`` matching given specifications.

        Raises:
            TypeError: If ``start`` or ``end`` are not ``datetime.date``, ``datetime.time`` or
                ``datetime.datetime`` objects.
            ValueError: If ``end`` is before ``start``.

        Note:
            * This public function only provides some sanity checks and normalization. The actual
                backend query is handled by ``_get_all``.
            * ``search_term`` should be prefixable with ``not`` in order to invert matching.
            * This does only return proper facts and does not include any existing 'ongoing fact'.
        """
        self.store.logger.debug(_(
            "Start: '{start}', end: {end} with filter: {filter} has been received.".format(
                start=start, end=end, filter=filter_term)
        ))

        if start is not None:
            if isinstance(start, datetime.datetime):
                # isinstance(datetime.datetime, datetime.date) returns True,
                # which is why we need to catch this case first.
                pass
            elif isinstance(start, datetime.date):
                start = datetime.datetime.combine(start, self.store.config['day_start'])
            elif isinstance(start, datetime.time):
                start = datetime.datetime.combine(datetime.date.today(), start)
            else:
                message = _(
                    "You need to pass either a datetime.date, datetime.time or datetime.datetime"
                    " object."
                )
                self.store.logger.debug(message)
                raise TypeError(message)

        if end is not None:
            if isinstance(end, datetime.datetime):
                # isinstance(datetime.datetime, datetime.date) returns True,
                # which is why we need to except this case first.
                pass
            elif isinstance(end, datetime.date):
                end = helpers.end_day_to_datetime(end, self.store.config)
            elif isinstance(end, datetime.time):
                end = datetime.datetime.combine(datetime.date.today(), end)
            else:
                message = _(
                    "You need to pass either a datetime.date, datetime.time or datetime.datetime"
                    " object."
                )
                raise TypeError(message)

        if start and end and (end <= start):
            message = _("End value can not be earlier than start!")
            self.store.logger.debug(message)
            raise ValueError(message)

        return self._get_all(start, end, filter_term)

    def _get_all(self, start=None, end=None, search_terms=''):
        """
        Return a list of ``Facts`` matching given criteria.

        Args:
            start_date (datetime.datetime, optional): Consider only Facts starting at or after
                this datetime. Defaults to ``None``.
            end_date (datetime.datetime): Consider only Facts ending before or at
                this datetime. Defaults to ``None``.
            filter_term (str, optional): Only consider ``Facts`` with this string as part of their
                associated ``Activity.name``.

        Returns:
            list: List of ``Facts`` matching given specifications.

        Note:
            In contrast to the public ``get_all``, this method actually handles the
            backend query.
        """
        raise NotImplementedError

    def get_today(self):
        """
        Return all facts for today, while respecting ``day_start``.

        Returns:
            list: List of ``Fact`` instances.

        Note:
            * This does only return proper facts and does not include any existing 'ongoing fact'.
        """
        self.store.logger.debug(_("Returning today's facts"))

        today = datetime.date.today()
        return self.get_all(
            datetime.datetime.combine(today, self.store.config['day_start']),
            helpers.end_day_to_datetime(today, self.store.config)
        )

    def _timeframe_is_free(self, start, end):
        """
        Determine if a given timeframe already holds any facts start or end time.

        Args:
            start (datetime): *Start*-datetime that needs to be validated.
            end (datetime): *End*-datetime that needs to be validated.

        Returns:
            bool: True if free, False if occupied.
        """
        raise NotImplementedError

    def _start_tmp_fact(self, fact):
        """
        Store new ongoing fact in persistent tmp file

        Args:
            fact (hamsterlib.Fact): Fact to be stored.

        Returns:
            hamsterlib.Fact: Fact stored.

        Raises:
            ValueError: If we already have a ongoing fact running.
            ValueError: If the fact passed does have an end and hence does not
                qualify for an 'ongoing fact'.
        """
        self.store.logger.debug(_("Fact: '{}' has been received.".format(fact)))
        if fact.end:
            message = _("The passed fact has an end specified.")
            self.store.logger.debug(message)
            raise ValueError(message)

        tmp_fact = helpers._load_tmp_fact(self._get_tmp_fact_path())
        if tmp_fact:
            message = _("Trying to start with ongoing fact already present.")
            self.store.logger.debug(message)
            raise ValueError(message)
        else:
            with open(self._get_tmp_fact_path(), 'wb') as fobj:
                pickle.dump(fact, fobj)
            self.store.logger.debug(_("New temporary fact started."))
        return fact

    def stop_tmp_fact(self):
        """
        Stop current 'ongoing fact'.

        Returns:
            hamsterlib.Fact: The stored fact.

        Raises:
            ValueError: If there is no currently 'ongoing fact' present.
        """
        self.store.logger.debug(_("Stopping 'ongoing fact'."))
        fact = helpers._load_tmp_fact(self._get_tmp_fact_path())
        if fact:
            fact.end = datetime.datetime.now()
            result = self.save(fact)
            os.remove(self._get_tmp_fact_path())
            self.store.logger.debug(_("Temporary fact stopped."))
        else:
            message = _("Trying to stop a non existing ongoing fact.")
            self.store.logger.debug(message)
            raise ValueError(message)
        return result

    def get_tmp_fact(self):
        """
        Provide a way to retrieve any existing 'ongoing fact'.

        Returns:
            hamsterlib.Fact: An instance representing our current 'ongoing fact'.capitalize

        Raises:
            KeyError: If no ongoing fact is present.
        """
        self.store.logger.debug(_("Trying to get 'ongoing fact'."))

        fact = helpers._load_tmp_fact(self._get_tmp_fact_path())
        if not fact:
            message = _("Tried to retrieve an 'ongoing fact' when there is none present.")
            self.store.logger.debug(message)
            raise KeyError(message)
        return fact

    def cancel_tmp_fact(self):
        """
        Provide a way to stop an 'ongoing fact' without saving it in the backend.

        Returns:
            None: If everything worked as expected.

        Raises:
            KeyError: If no ongoing fact is present.
        """
        # [TODO]
        # Maybe it would be useful to return the canceled fact instead. So it
        # would be available to clients. Otherwise they may be tempted to look
        # it up before canceling. which would result in two retrievals.
        self.store.logger.debug(_("Trying to cancel 'ongoing fact'."))

        fact = helpers._load_tmp_fact(self._get_tmp_fact_path())
        if not fact:
            message = _("Trying to stop a non existing ongoing fact.")
            self.store.logger.debug(message)
            raise KeyError(message)
        os.remove(self._get_tmp_fact_path())
        self.store.logger.debug(_("Temporary fact stoped."))

    def _get_tmp_fact_path(self):
        """Convinience function to assemble the tmpfile_path from config settings."""
        return self.store.config['tmpfile_path']
