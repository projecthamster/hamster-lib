# -*- encoding: utf-8 -*-

from hamsterlib import objects
from gettext import gettext as _
import datetime
# from future.utils import raise_from


"""
Module containing base classes intended to be inherited from when implementing storage backends.

Note:
    In lack of a better place to store this thought, here for now:
    Our dbus service assumes/imposes that PKs are always >= 0 integers.
    Whilst this is usualy the way to go, its worth noting as a constraint.

    resurrect/temporary for ``add_fact`` is about checking for preexisting activities
    by using ``__get_activity_by_name``. If True we will consider 'deleted' activities
    and stick this to our new fact.
"""


class BaseStore(object):
    """A controlers Store provides unified interfaces to interact with our stored enteties."""

    def __init__(self, path):
        self.path = path
        self.categories = BaseCategoryManager(self)
        self.activities = BaseActivityManager(self)
        self.facts = BaseFactManager(self)

    def cleanup(self):
        """
        Any backend specific teardown code that needs to be executed before
        we shut down gracefully.
        """
        raise NotImplementedError


class BaseManager(object):
    """Base class for all object managers."""

    def __init__(self, store):
        self.store = store


class BaseCategoryManager(BaseManager):
    """Base class defining the minimal API for a CategoryManager implementation."""

    def save(self, category):
        """
        Save a Category to our selected backend.
        Internal code decides wether we need to add or update.

        Args:
            category (hamsterlib.Category): Category instance to be saved.

        Returns:
            hamsterlib.Category: Saved Category

        Raises:
            TypeError: If the ``category`` parameter is not a valid ``Category`` instance.
        """

        # We split this into two seperate steps to make validation easier to
        # extend. And yes I know we are supposed to duck-type, but I always feel
        # more comftable validating untrusted input this way.
        if not isinstance(category, objects.Category):
            raise TypeError(_("You need to pass a hamster category"))

        # We don't check for just ``category.pk`` becauses we don't want to make
        # assumptions about the PK beeing an int.
        if category.pk or category.pk == 0:
            result = self._update(category)
        else:
            result = self._add(category)
        return result

    def get_or_create(self, name):
        """
        Check if we already got a category with that name, if not create one.

        This is a convinience method as it seems sensible to rather implement
        this once in our controler than having every client implementation
        deal with it anew.

        Args:
            namea (str): The categories name.

        Returns:
            hamsterlib.Category: The retrieved or created category
        """

        # [TODO]
        # create_category checks for an existing category of that name as well
        # which is redundant. But for now this will do.
        category = self.get_by_name(name)
        if not category:
            category = objects.Category(name)
            category = self._add(name)
        return category

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
            name (str): Name of the ``Category`` to we want to fetch.

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
            list: List of ``Categories``.
        """
        raise NotImplementedError

    def _add(self, category):
        """
        Add a ``Category`` to our backend.

        Args:
            category (hamsterlib.Category): ``Category`` to be added.

        Returns:
            hamsterlib.Category: Newly created ``Category`` instance.
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
        """
        raise NotImplementedError

    def remove(self, category):
        """
        Remove a category.

        Args:
            category (hamsterlib.Category): Category to be updated.

        Returns:
            None: If everything went ok.

        Raises:
            KeyError: If the ``Category`` can not be found by the backend.
        """
        raise NotImplementedError


class BaseActivityManager(BaseManager):
    """Base class defining the minimal API for a ActivityManager implementation."""
    def save(self, activity):
        """
        Save a ``Activity`` to the backend.

        This public method decides if it calles either ``_add`` or ``_update``.

        Args:
            activity (hamsterlib.Activity): ``Activity`` to be saved.

        Returns:
            hamsterlib.Activity: The saved ``Activity``.
        """

        if activity.pk or activity.pk == 0:
            # [FIXME]
            # It appears that[activity.name + activity.category] is supposed to
            # be unique (see ``storage.db __change_category()``).
            # That means that if we update the category of an activity we need
            # to ensure that particular combination does not exist already.
            # We still need to contemplate if this is to be handled on the
            # controler or storage-backend level.
            result = self._update(activity)
        else:
            result = self._add(activity)
        return result

    def get_or_create(self, name, category=None, deleted=False):
        """
        Convinience method to either get an activity matching the specs or create a new one.

        Args:
            name (str): Activity name
            category (hamsterlib.Category): The activities category
            deleted (bool): If the to be created category is marked as deleted.

        Returns:
            hamsterlib.Activity: The retrieved or created activity
        """

        # [TODO]
        # create_category checks for an existing activity of that name and
        # category as well which is redundant. But for now this will do.
        activity = self.get_by_composite(name, category)
        if not activity:
            activity = self.create_activity(name, category=category,
                                            deleted=deleted)
            activity = self.save(activity)
        return activity

    def _add(self, activity, temporary=False):
        """
        Add a new ``Activity`` instance to the databasse.

        Args:
            activity (hamsterlib.Activity): The ``Activity`` to be added.
            temporary (bool, optional): If ``True``, the fact will be created with
                ``Fact.deleted = True``. Defaults to ``False``.

        Returns:
            hamsterlib.Activity: The newly created ``Activity``.

        Note:
            For referece see ``storage.db.__add_activity()``.
        """
        raise NotImplementedError

    def _update(self, activity):
        raise NotImplementedError

    def remove(self, activity):
        """
        Remove an ``Activity`` from the database.import

        Args:
            activity (hamsterlib.Activity): The activity to be removed.

        Returns:
            bool: True

        Raises:
            KeyError: If the given ``Activity`` can not be found in the database.
        """
        raise NotImplementedError

    def get(self, pk):
        """
        Return an activity based on its primary key.

        Args:
            pk (int): Primary key of the activity

        Returns:
            hamsterlib.Activity: Activity matchin primary key.

        Raises:
            KeyError: If the primary key can not be found in the database.
        """
        raise NotImplementedError

    def get_by_composite(self, name, category):
        """
        Lookup for a supposedly unique ``Activityname`` / ``Category`` pair.

        This method utilizes that to return the corresponding entry or None.

        Args:
            name (str): Name of the ``Activities`` in question.
            category (hamsterlib.Category): ``Category`` of the activities.

        Returns:
            hamsterlib.Activity: The correspondig activity

        Raises:
            KeyError: If the composite key can not be found.
        """

        raise NotImplementedError

    def get_all(self, category=None, search_term=''):
        """
        Return all activities.

        Args:
            category (hamsterlib.Category, optional): Category to filter by. Defaults to ``None``.
                If ``None``, return all activities without a category.
            search_term (str): (Sub-)String that needs to be present in the ``Article.name`` in
                order to be considered for the resulti``Article.name`` in
                    order to be considered for the resulting list.

        Returns:
            list: List of activities
        """
        raise NotImplementedError


class BaseFactManager(BaseManager):
    """Base class defining the minimal API for a FactManager implementation."""
    def save(self, fact):
        """
        Save a Fact to our selected backend.

        Args:
            fact (hamsterlib.Fact): Fact to be saved. Needs to be complete otherwise this will
            fail.

        Returns:
            hamsterlib.Fact: Saved Fact.
        """

        if fact.pk or fact.pk == 0:
            result = self._update(fact)
        else:
            result = self._add(fact)
        return result

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

    def get_all(self, start_date=None, end_date=None, filter_term=''):
        """
        Return a list of ``Facts`` matching given criterias.

        Args:
            start_date (datetime.date, optional): Consider only Facts starting at or after
                this date. Alternativly you can also pass a ``datetime.datetime`` object
                in which case its own time will be considered instead of the default ``day_start``.
                Defaults to ``None``.
            end_date (datetime.datetime, optional): Consider only Facts ending before or at
                this date. Alternativly you can also pass a ``datetime.datetime`` object
                in which case its own time will be considered instead of the default ``day_start``.
                Defaults to ``None``.
            filter_term (str, optional): Only consider ``Facts`` with this string as part of their
                associated ``Activity.name``.

        Returns:
            list: List of ``Facts`` matching given specifications.
        """

        start = start_date
        end = end_date
        if start_date and end_date:
            start = datetime.datetime.combine(start_date, self.store.config['daystart'])
            # [FIXME]
            # If we get rid of the dedicated ``day_end`` this needs to be
            # adjusted.
            end = datetime.datetime.combine(end_date, self.store.config['dayend'])
        return self._get_all(start, end, filter_term)

    def _add(self, fact):
        """
        Add a new ``Fact`` to the backend.

        Args:
            fact (hamsterlib.Fact): Fact to be added.

        Returns:
            hamsterlib.Fact: Added ``Fact``.

        Returns:
            hamsterlib.Fact: Added ``Fact``.
        """
        raise NotImplementedError

    def _update(self, fact):
        raise NotImplementedError

    def remove(self, fact):
        """
        Remove a given ``Fact`` from the backend.

        Args:
            fact (hamsterlib.Fact): ``Fact`` instance to be removed.

        Returns:
            None: If everything worked as intended.

        Raises:
            KeyError: If the ``Fact`` specified could not be found in the backend.
        """
        raise NotImplementedError

    def _get_all(self, start=None, end=None, search_terms=''):
        """
        Get all Facts in a given timeframe.

        Note:
            Unlike the public method this one expects datetime objects.
        """
        raise NotImplementedError
