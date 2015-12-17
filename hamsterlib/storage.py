# -*- encoding: utf-8 -*-

from hamsterlib import objects
from gettext import gettext as _
from future.utils import raise_from


"""
In lack of a better place to store this thought, here for now:
Our dbus service assumes/imposes that PKs are always >= 0 integers.
Whilst this is usualy the way to go, its worth noting as a constraint.

resurrect/temporary for add_fact is about checking for preexisting activities
by using __get_activity_by_name. If True we will consider 'deleted' activities
and stick this to our new fact.
"""

class BaseStore(object):
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
    def __init__(self, store):
        self.store = store


class BaseCategoryManager(BaseManager):
    def save(self, category):
        """
        Save a Category to our selected backend.
        Internal code decides wether we need to add or update.

        :param category: Category to be saved
        :type category: Category
        :return: Saved Category or False if we failed.
        :rtype: Category or bool
        """

        # We split this into two seperate steps to make validation easier to
        # extend. And yes I know we are supposed to duck-type, but I always feel
        # more comftable validating untrusted input this way.
        if not isinstance(category, objects.Category):
            raise TypeError(_("You need to pass a hamster category"))

        if category.pk or category.pk == 0:
            result = self._update(category)
        else:
            result = self._add(category)
        return result

    def get_or_create(self, name):
        """
        Check if we already got a category with that name, if not
        create one.

        This is a convinience method as it seems sensible to rather implement
        this once in our controler than having every client implementation
        deal with it anew.

        :param str name: The categories name.

        :return: The retrieved or created category
        :rtype: object.Category
        """

        #[TODO]
        # create_category checks for an existing category of that name as well
        # which is redundant. But for now this will do.
        category = self.get_by_name(name)
        if not category:
            category = objects.Category(name)
            category = self._add(name)
        return category

    def get(self, pk):
        raise NotImplementedError

    def get_by_name(self, name):
        """
        Look up a category by its name.

        :param str name: Name of the category to we want the PK of
        :return: Hamster-Category with given name
        :rtype: Hamster-Category instance.
        """
        raise NotImplementedError

    def get_all(self):
        """Return a list of all categories as hamster instances."""
        raise NotImplementedError

    def _add(self, category):
        """
        Add a category to our backend.

        :param category: Category to be added
        :type category: Category
        :return: The newly created category
        :rtype: Category
        """
        raise NotImplementedError

    def _update(self, category):
        """
        update a categories values in our backend.

        :param category: Category to be updated
        :type category: Category
        :return: The updated category
        :rtype: Category
        """
        raise NotImplementedError

    def remove(self, category):
        """
        Remove a category.

        :param category: Category to be removed.
        :type category: Hamster-Category
        :return: Success status
        :rtype: bool
        """
        raise NotImplementedError


class BaseActivityManager(BaseManager):
    def save(self, activity):
        if activity.pk or activity.pk == 0:
            #[FIXME]
            # [activity.name + activity.category] soll anscheinend unique sein.
            # Siehe storage.db __change_category()
            # D.h. Wenn wir die category einer activity updaten müssen wir sicher
            # gehen das es diese combination nicht shcon gibt.
            # Es bleibt zu bedenken ob wur das auf controler oder storage-backend
            # ebene abfertigen wollen.
            result = self._update(activity)
        else:
            result = self._add(activity)
        return result


    def create(self, name, category=None, deleted=False):
        """
        Convinience Method for creating and saving a new activity.
        Use this if you don't to build the activity yourself in order
        to just pass it on to save_activity.

        :param str name: The activity name.

        :return: The newly created and saved activity instance.
        :rtype: objects.Activity or None
        """
        activity = self.get(name, category)
        if not activity:
            activity = objects.Activity(name, category=category,
                                        deleted=deleted)
            return self.save(activity)

    def get_or_create(self, name, category=None, deleted=False):
        """
        Check if we already got an activity with that name and category,
        if not create one.

        This is a convinience method as it seems sensible to rather implement
        this once in our controler than having every client implementation
        deal with it anew.

        :param str name: The activity name.
        :param objects.Category category: This activities category

        :return: The retrieved or created activity
        :rtype: object.Activity
        """

        #[TODO]
        # create_category checks for an existing activity of that name and
        # category as well which is redundant. But for now this will do.
        activity = self.activities.get(name, category)
        if not activity:
            activity = self.create_activity(name, category=category,
                                            deleted=deleted)
        return activity

    def _add(self, activity, temporary=False):
        """
        :param str temporary: Who the fuck knows what this is about...

        For referece see storage.db.__add_activity(). If temporary, the fact
        will be created with deleted=True.
        """
        raise NotImplementedError

    def _update(self, activity):
        raise NotImplementedError

    def remove(self, activity):
        raise NotImplementedError

    def get(self, pk):
        """
        Return an activity based on its PK.

        :param int pk: PK of the activity

        :return: Activity matchin PK
        :rtype: Activity
        """
        raise NotImplementedError
    def get_by_composite(self, name, category):
        """
        It aprears that in our current datamodel each combination of
        name/category is unique.

        This method utilizes that to return the corresponding entry or None.

        :para str name: activities name
        :para objects.Category category: activities category

        :return: the correspondig activity or None
        :rtype: objects.Activity or None
        """

        raise NotImplementedError


    def get_all(self, category=False, search_term=''):
        """
        Return all activities.

        :param category: Category by to filter by. If None, return all
        activities without a category.
        :type category: Category or None

        :return: List of activities
        :rtype: list
        """
        raise NotImplementedError


class BaseFactManager(BaseManager):
    def save(self, fact):
        """
        Save a Fact to our selected backend.
        Internal code decides wether we need to add or update.

        :param fact: Fact to be saved
        :type fact: Fact

        :return: Saved Fact or False if we failed.
        :rtype: Fact or bool
        """

        if fact.pk or fact.pk == 0:
            result = self._update(fact)
        else:
            result = self._add(fact)
        return result

    def get(self, pk):
        raise NotImplementedError

    def get_all(self, start_date=None, end_date=None, filter_term=''):

        start = start_date
        end = end_date
        if start_date and end_date:
            start = datetime.datetime.combine(start_date, self.store.config['daystart'])
            end = datetime.datetime.combine(end_date, self.store.config['dayend'])
        return self._get_all(start, end, filter_term)

    def _add(self, fact):
        raise NotImplementedError

    def _update(self, fact):
        raise NotImplementedError

    def remove(self, fact):
        raise NotImplementedError

    def _get_all(self, start_date=None, end_date=None, search_terms=''):
        raise NotImplementedError

