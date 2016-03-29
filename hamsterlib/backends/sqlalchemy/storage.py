# -*- encoding: utf-8 -*-

from __future__ import unicode_literals
from builtins import str
from future.utils import python_2_unicode_compatible

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker  # , mapper, relationship
from sqlalchemy.sql.expression import and_, or_
from sqlalchemy.orm.exc import FlushError, NoResultFound, MultipleResultsFound
from sqlalchemy.exc import IntegrityError

from gettext import gettext as _

from . import objects
from hamsterlib import storage
from hamsterlib import Category, Activity  # , Fact
from .objects import AlchemyCategory, AlchemyActivity, AlchemyFact

import logging

logger = logging.getLogger('hamsterlib')

"""
A striking reason for having id for PKs is to deal with the updating of instances.
If the PK is the name or such, and we want to update an existing instances spelling, it
would be tricky to retrieve the old version if all we have is the new name.
"""


@python_2_unicode_compatible
class SQLAlchemyStore(storage.BaseStore):
    """
    SQLAlchemy based backend.

    Unfortunatly despite using SQLAlchemy some database specific settings can not
    be avoided (autoincrement, indexes etc).
    Some of those issues will not be relevant in later versions as we may get rid
    of Category and Activity ids entirely, just using their natural/composite keys
    as primary keys.

    However, for now we just support sqlite until the basic framework is up and running.
    It should take only minor but delayable effort to broaden the applicability to
    postgres, mysql and the likes.

    The main takeaway right now is, that their is no actuall guarantee that in a
    distributed environment no race condition occur and we may end up with duplicate
    Category/Activity entries. No backend code will be able to prevent this by virtue of
    this beeing a DB issue.
    Furthermore, we will try hard to avoid placing more than one fact in a given time
    window. However, there can be no guarantee that in a distributed environment this
    will allways work out. As a consequence, we make sure that all our single object
    data retrieval methods return only one item or throw an error alerting us the the
    inconsistency.
    """
    def __init__(self, path):
        engine = create_engine(path)
        objects.metadata.bind = engine
        objects.metadata.create_all(engine)

        Session = sessionmaker(bind=engine)
        self.session = Session()
        self.categories = CategoryManager(self)
        self.activities = ActivityManager(self)
        self.facts = FactManager(self)

    def cleanup(self):
        pass


@python_2_unicode_compatible
class CategoryManager(storage.BaseCategoryManager):
    def get_or_create(self, category, raw=False):
        """
        Custom version of the default method in order to provide access to alchemy instances.

        Args:
            category (hamsterlib.Category: Category we want.
            raw (bool): Wether to return the AlchemyCategory instead.

        Returns:
            hamsterlib.Category: Category.
        """

        if category:
            try:
                category = self.get_by_name(category.name, raw=raw)
            except KeyError:
                category = objects.Category(category.name)
                category = self._add(category, raw=raw)
        else:
            category = None
        return category

    def _add(self, category, raw=False):
        """
        Add a new category to the database.

        This method should not be used by any client code. Call ``save`` to make
        the decission wether to modify an existing entry or to add a new one is
        done correctly..

        Args:
            category (hamsterlib.Category): Hamster Category instance.

        Returns:
            Category: Saved instance, as_hamster()

        Raises:
            ValueError: If the name to be added is already present in the db.
            ValueError: If category passed already got an PK. Indicating that update would
                be more apropiate.
        """

        if category.pk:
            message = _(
                "The category ('{!r}') you are trying to add already has an PK."
                " Are you sure you do not want to ``_update`` instead?".format(category)
            )
            logger.debug(message)
            raise ValueError(message)
        alchemy_category = AlchemyCategory(category)
        self.store.session.add(alchemy_category)
        try:
            self.store.session.commit()
        except FlushError as e:
            message = _(
                "An error occured! Are you sure the category.name is not already present in our"
                " database? Here is the full original exception: '{}'.".format(e)
            )
            logger.debug(message)
            raise ValueError(message)
        logger.debug(_("Category '{!r}' added.".format(alchemy_category)))

        if not raw:
            alchemy_category = alchemy_category.as_hamster()
        return alchemy_category


    def _update(self, category):
        """
        Update a given Category.

        Args:
            category (hamsterlib.Category): Category to be updated.

        Returns:
            hamsterlib.Category: Updated category.

        Raises:
            ValueError: If the new name is already taken.
            ValueError: If category passed does not have a PK.
        """
        if not category.pk:
            message = _(
                "The category passed ('{!r}') does not seem to havea PK. We don't know"
                "which entry to modify.".format(category)
            )
            logger.debug(message)
            raise ValueError(message)
        alchemy_category = AlchemyCategory(category)
        try:
            self.store.session.commit()
        except IntegrityError as e:
            raise ValueError(_(
                "An error occured! Are you sure the category.name is not already present in our"
                " database? Here is the full original exception: '{}'.".format(e)
            ))

        return alchemy_category.as_hamster()

    def remove(self, category):
        """
        Delete a given category.

        Args:
            category (hamsterlib.Category): Category to be removed.

        Returns:
            None: If everything went alright.

        Raises:
            TypeError: If category passed is not an hamsterlib.Category instance.
            ValueError: If category passed does not have an pk.
        """
        # [FIXME] Figure our what exactly does it mean to remove a category.

        if not isinstance(category, Category):
            raise TypeError(_(
                "Category instance expected. Got {} instead.".format(type(category))
            ))
        if not category.pk:
            raise ValueError(_("PK-less Category. Are you trying to remove a new Category?"))
        alchemy_category = self.store.session.query(AlchemyCategory).get(category.pk)
        self.store.session.delete(alchemy_category)
        self.store.session.commit()

    def get(self, pk):
        """
        Return a category based on their pk.

        Args:
            pk: PK of the category to be retrieved.

        Returns:
            hamsterlib.Category: Category matching given PK.

        Raises:
            KeyError: If no such PK was found.

        Note:
            We need this for now, as the service just provides pks, not names.
        """
        result = self.store.session.query(AlchemyCategory).get(pk)
        if not result:
            raise KeyError(_("No category with 'pk: {}' was found!".format(pk)))
        return result.as_hamster()

    def get_by_name(self, name, raw=False):
        """
        Return a category based on its (unique?) name.

        Args:
            name (str): Unique name of the category.

        Returns:
            hamsterlib.Category: Category of given name.

        Raises:
            KeyError: If no category matching the name was found.

        """
        name = str(name)
        try:
            result = self.store.session.query(AlchemyCategory).filter_by(name=name).one()
        except NoResultFound:
            raise KeyError(_("No category with 'name: {}' was found!".format(name)))

        if not raw:
            result = result.as_hamster()
        return result

    def get_all(self):
        """
        Get all categories.

        Returns:
            list: List of all Categories present in the database. Results are ordered by name.
        """
        return [alchemy_category for alchemy_category in (
            self.store.session.query(AlchemyCategory).order_by(AlchemyCategory.name).all())]


@python_2_unicode_compatible
class ActivityManager(storage.BaseActivityManager):

    def _add(self, activity):
        """
        Args:
            activity (hamsterlib.Activity): Hamster activity

        Returns:
            hamsterlib.Activity: Hamster activity representation of stored instance.

        Raises:
            ValueError: If the category/activity.name combination to be added is
            already present in the db.
        """
        if activity.pk:
            message = _(
                "The activity ('{!r}') you are trying to add already has an PK."
                " Are you sure you do not want to ``_update`` instead?".format(activity)
            )
            logger.debug(message)
            raise ValueError(message)

        try:
            self.get_by_composite(activity.name, activity.category)
            message = _("Our database already contains the passed name/category.name"
                        "combination.")
            raise ValueError(message)
        except KeyError:
            pass

        alchemy_activity = AlchemyActivity(activity)
        try:
            alchemy_activity.category = self.store.categories.get_by_name(
                activity.category, raw=True)
        except KeyError:
            alchemy_activity.category = AlchemyCategory(activity.category)
        self.store.session.add(alchemy_activity)
        self.store.session.commit()
        return alchemy_activity.as_hamster()

    def _update(self, activity):
        """
        Update a given Activity.

        Args:
            activity (hamsterlib.Activity): Activity to be updated.

        Returns:
            hamsterlib.Activity: Updated activity.

        Raises:
            ValueError: If the new name/category.name combination is already taken.
        """
        if not activity.pk:
            message = _(
                "The activity passed ('{!r}') does not seem to havea PK. We don't know"
                "which entry to modify.".format(activity)
            )
            logger.debug(message)
            raise ValueError(message)

        try:
            self.get_by_composite(activity.name, activity.category)
            message = _("Our database already contains the passed name/category.name"
                        "combination.")
            raise ValueError(message)
        except KeyError:
            pass

        alchemy_activity = self.store.session.query(AlchemyActivity).get(activity.pk)
        alchemy_activity.name = activity.name
        alchemy_activity.category = self.store.categories.get_or_create(
            activity.category, raw=True)
        alchemy_activity.deleted = activity.deleted
        try:
            self.store.session.commit()
        except IntegrityError as e:
            raise ValueError(_(
                "There seems to already be an activity like this for the given category."
                "Can not change this activities values. Original exception: {}".format(e)
            ))
        return alchemy_activity.as_hamster()

    def remove(self, activity):
        """
        Remove an activity from our internal backend.

        Note:
            Should removeing the last activity of a category also trigger category
            removal?

        :param activity: Activity to be removed
        :type activity: Activity

        :return: Success status
        :rtype: bool
        """
        # [TODO] Check if this is the original functionality. Most likly we just
        # need to set deleted marker isntead of deleting the actual instance.
        if not activity.pk:
            message = _("The activity you passed does not have a PK. Please provide one.")
            raise ValueError(message)

        alchemy_activity = self.store.session.query(AlchemyActivity).get(activity.pk)
        if not alchemy_activity:
            message = _("The activity you try to remove does not seem to exist.")
            raise KeyError(message)
        self.store.session.delete(alchemy_activity)
        self.store.session.commit()
        return True

    def get(self, pk, raw=False):
        """
        Query for an Activity with given key.

        Args:
            pk: PK to look up.
            raw (bool): Return the AlchemyActivity instead.

        Returns:
            hamsterlib.Activity: Activity with given PK.

        Raises:
            KeyError: If no such pk was found.
        """
        result = self.store.session.query(AlchemyActivity).get(pk)
        if not result:
            raise KeyError(_("No Activity with 'pk: {}' was found!".format(pk)))
        if not raw:
            result = result.as_hamster()
        return result

    def get_by_composite(self, name, category, raw=False):
        """
        Retrieve an activity by its name and category)

        Args:
            name (str): The activities name.
            category (str or None): The activities category
            raw (bool): Return the AlchemyActivity instead.

        Returns:
            hamsterlib.Activity: The activity if it exists in this combination.

        Raises:
            KeyError: if composite key can not be found in the db.

        Note:
            As far as we understand the legacy code in ``__change_category`` and
            ``__get_activity_by`` the combination of activity.name and
            activity.category is unique. This is reflected in the uniqueness constraint
            of the underlying table.
        """
        name = str(name)
        if category:
            category = str(category.name)
            try:
                alchemy_category = self.store.categories.get_by_name(category, raw=True)
            except KeyError:
                raise KeyError(_(
                    "The category passed ({}) does not exist in the backend. Consequently no"
                    " related activity can be returned.".format(category)
                ))
        else:
            alchemy_category = None

        try:
            result = self.store.session.query(AlchemyActivity).filter_by(name=name).filter_by(
                category=alchemy_category).one()
        except NoResultFound:
            raise KeyError(_(
                "No activity of given combination (name: {name}, category: {category})"
                " could be found.".format(name=name, category=category)
            ))
        if not raw:
            result = result.as_hamster()
        return result

    def get_all(self, category=None, search_term=''):
        """
        Retrieve all activities stored in the backend.

        Args:
            category (hamsterlib.Category, optional): Limit activities to this category.
                Defaults to ``None``.
            search_term (str, optional): Limit activities to those matching this string a substring
                in their name. Defaults to ``empty string``.

        Returns:
            list: List of ``hamsterlib.Activity`` instances matching constrains. This list
                is ordered by ``Activity.name``.
        """
        result = self.store.session.query(AlchemyActivity)

        if category:
            alchemy_category = self.store.session.query(AlchemyCategory).get(category.pk)
        else:
            alchemy_category = None
        result = result.filter_by(category=alchemy_category)

        if search_term:
            result = result.filter(AlchemyActivity.name.ilike('%{}%'.format(search_term)))
        result.order_by(AlchemyActivity.name)
        return result.all()


@python_2_unicode_compatible
class FactManager(storage.BaseFactManager):

    def _add(self, fact):
        """
        Add a new fact to the database.

        Args:
            fact (hamsterlib.Fact): Fact to be added.

        Returns:
            hamsterlib.Fact: Fact as stored in the database
        """
        alchemy_fact = AlchemyFact(fact)
        self.store.session.add(alchemy_fact)
        self.store.session.commit()
        return alchemy_fact.as_hamster()

    def _update(self, fact):
        """Update and existing fact with new values.

        Args:
            fact (hamsterlib.fact): Fact instance holding updated values.

        Returns:
            hamsterlib.fact: Updated Fact


        Raises:
            KeyError: if a Fact with the relevant PK could not be found.
        """
        alchemy_fact = self.store.session.query(AlchemyFact).get(fact.pk)
        if not alchemy_fact:
            raise KeyError(_("No fact with 'pk: {}' was found.".format(fact.pk)))

        alchemy_fact.activity = AlchemyActivity(self.store.activities.get_or_create(
            fact.activity.name, fact.activity.category, fact.activity.deleted))
        self.store.session.commit()
        return fact

    def remove(self, fact):
        """
        Remove a fact from our internal backend.

        Args:
            fact (hamsterlib.Fact): Fact to be removed
        Returns:
            bool: Success status
        """

        alchemy_fact = self.store.session.query(AlchemyFact).get(fact.pk)
        self.store.session.delete(alchemy_fact)
        self.store.session.commit()
        return True

    def get(self, pk):
        """Return a fact based on its PK.

        Args:
            pk: PK of the fact to be retrieved

        Returns:
            hamsterlib.Fact: Fact matching given PK

        Raises:
            KeyError: If no Fact of given key was found.
        """
        return self.store.session.query(AlchemyFact).get(pk)

    def get_all(self, start=None, end=None, search_term=''):
        """
        Return all facts within a given timeframe (beginning of start_date
        end of end_date) that match given search terms.

        If no timeframe is given, return all facts?

        Args:
            start (datetime.datetime, optional): Start of timeframe

        Returns:
            list: List of ``hamsterlib.Facts`` instances.
        """
        # [FIXME] Figure out against what to match search_terms
        results = self.store.session.query(AlchemyFact)
        if start and end:
            # [FIXME]
            # Account for (start or end)! Check with reference implementation.

            # This assumes that start <= end!
            results = results.filter(and_(AlchemyFact.start >= start, AlchemyFact.end <= end))
        if search_term:
            results = results.join(AlchemyActivity).join(AlchemyCategory).filter(
                or_(AlchemyActivity.name.ilike('%{}%'.format(search_term)),
                    AlchemyCategory.name.ilike('%{}%'.format(search_term))
                    )
            )
        # [FIXME]
        # Depending on scale, this could be a problem.
        return [fact.as_hamster() for fact in results.all()]
