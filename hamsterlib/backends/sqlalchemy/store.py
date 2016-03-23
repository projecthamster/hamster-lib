# -*- encoding: utf-8 -*-

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, mapper, relationship
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.sql.expression import and_, or_

from gettext import gettext as _
from past.builtins import basestring

from hamsterlib.backends.sqlalchemy import alchemy
from hamsterlib import storage
from hamsterlib import Category, Activity, Fact
from hamsterlib.backends.sqlalchemy import AlchemyCategory, AlchemyActivity, AlchemyFact

import logging
logger = logging.getLogger('hamsterlib.lib')


class SQLAlchemyStore(storage.BaseStore):
    def __init__(self, path):
        engine = create_engine(path)
        alchemy.metadata.bind = engine
        alchemy.metadata.create_all(engine)

        Session = sessionmaker(bind=engine)
        self.session = Session()
        self.categories = CategoryManager(self)
        self.activities = ActivityManager(self)
        self.facts = FactManager(self)


    def cleanup(self):
        pass


class CategoryManager(storage.BaseCategoryManager):
    def _add(self, hamster_category):
        """
        Add a hamster category. Reteurn saved instance hamster style.

        Args:
            hamster_category (Category): Hamster Category instance.

        Returns:
            Category: Saved instance, as_hamster()
        """
        logger.debug(
            _("Recieved <{}> to be added to DB.".format(
                hamster_category))
        )
        category = AlchemyCategory(hamster_category)
        self.store.session.add(category)
        self.store.session.commit()
        return category.as_hamster()

    def _update(self, hamster_category):
        category = AlchemyCategory(hamster_category)
        self.store.session.commit()
        return category.as_hamster()

    def remove(self, category):
        # [FIXME] Figure our what exactly does it mean to remove a category.
        """
        Delete a given category.

        :param hamster_category: Category to be removed.
        :type hamster_category: Hamster-Category instance.
        :return: Success status
        :rtype: bool or Error
        """

        if not isinstance(category, Category):
            raise TypeError(_("Category instance expected."))
        elif category.pk is None:
            raise ValueError(_("PK-less Category. Are you trying to remove a"
                               " new Category?"
                               ))
        else:
            alchemy_category = self.store.session.query(AlchemyCategory).get(category.pk)
            self.store.session.delete(alchemy_category)
            self.store.session.commit()
            return True

    def get(self, pk):
        """Return a category based on their pk.

        We need this for now, as the service just provides pks, not names.
        """
        return self.store.session.query(AlchemyCategory).get(pk)

    def get_by_name(self, name):
        """ Return a category based on its (unique?) name."""
        if not isinstance(name, basestring):
            raise TypeError(_("Name must be a (base-)string!"))

        result = self.store.session.query(AlchemyCategory).filter_by(
            name=name).one_or_none()
        if result:
            result.as_hamster()
        return result

    def get_or_create(self, name):
        # [FIXME] This may actually already be covered by the base manager!
        """
        Args:
            name (str): Name of the category

        Returns:
            Category: Hamster category of that name.
        """
        alchemy_category = self.get_by_name(name)
        if not alchemy_category:
            alchemy_category = AlchemyCategory(Category(name))
            self._add(alchemy_category)
        return alchemy_category


    def get_all(self):
        """Get all categories."""
        return [alchemy_category for alchemy_category in (
            self.store.session.query(AlchemyCategory).order_by(AlchemyCategory.name).all())]


class ActivityManager(storage.BaseActivityManager):

    def _add(self, activity):
        """
        Args:
            activity (Activity): Hamster activity

        Returns:
            Activity: Hamster activity representation of stored instance.
        """
        alchemy_activity = AlchemyActivity(activity)
        self.store.session.add(alchemy_activity)
        self.store.session.commit()
        return alchemy_activity.as_hamster()

    def _update(self, activity):
        self.store.session.commit()
        return activity

    def remove(self, activity):
        """
        Remove an activity from our internal backend.

        :param activity: Activity to be removed
        :type activity: Activity

        :return: Success status
        :rtype: bool
        """
        # [TODO] Check if this is the original functionality. Most likly we just
        # need to set deleted marker isntead of deleting the actual instance.
        alchemy_activity = self.store.session.query(AlchemyActivity).get(activity.pk)
        self.store.session.delete(alchemy_activity)
        self.store.session.commit()
        return True

    def get_or_create(self, name, category):
        """
        Args:
            name (str): Activity name
            category (Category): Category the activiry is associated with.

        Returns:
            Activity: Hamster Activity
        """
        activity = self.get_by_composite(name, category)
        if not activity:
            activity = Activity(name, category=category)
            activity = self._add(activity)
        return activity

    def get(self, pk):
        return self.store.session.query(AlchemyActivity).get(pk)

    def get_by_composite(self, name, category):
        """
        As far as we understand the legacy code in ``__change_category`` and
        ``__get_activity_by`` the combination of activity.name and
        activity.category is unique.

        Whilst it is questionable if our datamodel is the most
        apropiate one, we will stick to work around this premise for now.

        :param str name: The activities name.
        :param category: The activities category
        :type category: objects.Category

        :return: The activity if it exists in this combination
        :rtype: objects.Activity or None
        """

        if category:
            alchemy_category = AlchemyCategory(category)
        else:
            alchemy_category = None

        result = self.store.session.query(AlchemyActivity).filter_by(
            name=name).filter_by(category=alchemy_category).one_or_none()
        if result:
            result = result.as_hamster()
        return result

    def get_all(self, category=None, search_term=''):
        result = self.store.session.query(AlchemyActivity)

        if category:
            alchemy_category = AlchemyCategory(category)
        else:
            alchemy_category = None
        result = result.filter_by(category=alchemy_category)

        if search_term:
            result = result.filter(AlchemyActivity.name.ilike('%{}%'.format(search_term)))
        result.order_by(AlchemyActivity.name)
        return result.all()


class FactManager(storage.BaseFactManager):

    def _add(self, fact):
        """
        Args:
            fact (Fact): Hamster Fact

        Returns:
            Fact: Hamster fact
        """
        alchemy_fact = AlchemyFact(fact)
        self.store.session.add(alchemy_fact)
        self.store.session.commit()
        return alchemy_fact.as_hamster()

    def _update(self, fact):
        self.store.session.commit()
        return fact

    def remove(self, fact):
        """
        Remove a fact from our internal backend.

        :param fact: Fact to be removed
        :type fact: Fact
        :return: Success status
        :rtype: bool
        """

        alchemy_fact = self.store.session.query(AlchemyFact).get(fact.pk)
        self.store.session.delete(alchemy_fact)
        self.store.session.commit()
        return True

    def get(self, pk):
        """Return a fact based on its PK.

        :param in pk: PF of the fact to be retrieved

        :return: A hamster Fact matching given PK
        :rtype: Fact
        """
        return self.store.session.query(AlchemyFact).get(pk)

    def get_all(self, start=None, end=None, search_term=''):
        """
        Return all facts within a given timeframe (beginning of start_date
        end of end_date) that match given search terms.

        If no timeframe is given, return all facts?

        :return: List of facts
        :rtype: list
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

