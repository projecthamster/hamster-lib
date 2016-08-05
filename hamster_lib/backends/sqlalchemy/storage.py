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

import os.path
from builtins import str

from future.utils import python_2_unicode_compatible
from hamster_lib import storage
from six import text_type
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.sql.expression import and_, or_

from . import objects
from .objects import AlchemyActivity, AlchemyCategory, AlchemyFact, AlchemyTag


@python_2_unicode_compatible
class SQLAlchemyStore(storage.BaseStore):
    """
    SQLAlchemy based backend.

    Unfortunately despite using SQLAlchemy some database specific settings can not
    be avoided (autoincrement, indexes etc).
    Some of those issues will not be relevant in later versions as we may get rid
    of Category and Activity ids entirely, just using their natural/composite keys
    as primary keys.

    However, for now we just support sqlite until the basic framework is up and running.
    It should take only minor but delayable effort to broaden the applicability to
    postgres, mysql and the likes.

    The main takeaway right now is, that their is no actual guarantee that in a
    distributed environment no race condition occur and we may end up with duplicate
    Category/Activity entries. No backend code will be able to prevent this by virtue of
    this being a DB issue.
    Furthermore, we will try hard to avoid placing more than one fact in a given time
    window. However, there can be no guarantee that in a distributed environment this
    will always work out. As a consequence, we make sure that all our single object
    data retrieval methods return only one item or throw an error alerting us about the
    inconsistency.
    """

    def __init__(self, config, session=None):
        """
        Set up the store.

        Args:
            path (str): Specifies the database to be used. See SQLAlchemy docs for
                details.
            session (SQLALcheny Session object, optional): Provide a dedicated session
                to be used. Defaults to ``None``.

        Note:
            The ``session`` argument is mainly useful for tests.
        """
        super(SQLAlchemyStore, self).__init__(config)
        # [TODO]
        # It takes more deliberation to decide how to handle engine creation if
        # we receive a session. Should be require the session to bring its own
        # engine?
        engine = create_engine(self._get_db_url())
        self.logger.debug(_('Engine created.'))
        objects.metadata.bind = engine
        objects.metadata.create_all(engine)
        self.logger.debug(_("Database tables created."))
        if not session:
            Session = sessionmaker(bind=engine)  # NOQA
            self.logger.debug(_("Bound engine to session-object."))
            self.session = Session()
            self.logger.debug(_("Instantiated session."))
        else:
            self.session = session
        self.categories = CategoryManager(self)
        self.activities = ActivityManager(self)
        self.tags = TagManager(self)
        self.facts = FactManager(self)

    def cleanup(self):
        pass

    def _get_db_url(self):
        """
        Create a ``database_url`` from ``config`` suitable to be consumed by ``create_engine``

        Our config may include:
            * ''db_engine``; Engine to be used.
            * ``db_host``; Host to connect to.
            * ``db_port``; Port to connect to.
            * ``db_path``; Used if ``engine='sqlite'``.
            * ``db_user``; Database user to be used for connection.
            * ``db_password``; Database user passwort to authenticate user.

        If ``db_engine='sqlite'`` you need to provide ``db_path`` as well. For any other engine
        ``db_host`` and ``db_name`` are mandatory.

        Note:
            * `SQLAlchemy docs <http://docs.sqlalchemy.org/en/latest/core/engines.html>`_

        Returns:
            str: ``database_url`` suitable to be consumed by ``create_engine``.

        Raises:
            ValueError: If a required config key/value pair is not present for the choosen
                ``db_engine``.
        """
        # [FIXME]
        # Contemplate if there are security implications that warrant sanitizing
        # config values.

        engine = self.config.get('db_engine', '')
        host = self.config.get('db_host', '')
        name = self.config.get('db_name', '')
        path = self.config.get('db_path', '')
        port = self.config.get('db_port', '')
        user = self.config.get('db_user', '')
        password = self.config.get('db_password', '')

        if not engine:
            message = _("No engine found in config!")
            self.logger.error(message)
            raise ValueError(message)

        # URL composition is slightly different for sqlite
        if engine == 'sqlite':
            if not path:
                # We could have allowed for blank paths, which would make
                # SQLAlchemy default to ``:memory:``. But explicit is better
                # than implicit. You can still create an in memory db by passing
                # ``db_path=':memory:'`` deliberately.
                message = _("No 'db_path' found in config! Sqlite requires one.")
                self.logger.error(message)
                raise ValueError(message)
            if path != ':memory:':
                # Make sure we always use an absolute path.
                path = os.path.abspath(path)
            database_url = '{engine}:///{path}'.format(engine=engine, path=path)
        else:
            if not host:
                message = _("No 'db_host' found in config! Engines other than sqlite require one.")
                self.logger.error(message)
                raise ValueError(message)
            if not name:
                message = _("No 'db_name' found in config! Engines other than sqlite require one.")
                self.logger.error(message)
                raise ValueError(message)
            if not user:
                message = _("No 'db_user' found in config! Engines other than sqlite require one.")
                self.logger.error(message)
                raise ValueError(message)
            if not password:
                message = _("No 'db_password' found in config! Engines other than"
                            " sqlite require one.")
                self.logger.error(message)
                raise ValueError(message)
            if port:
                port = ':{}'.format(port)
            database_url = '{engine}://{user}:{password}@{host}{port}/{name}'.format(
                engine=engine, user=user, password=password, host=host, port=port, name=name)
        return database_url


@python_2_unicode_compatible
class CategoryManager(storage.BaseCategoryManager):
    def get_or_create(self, category, raw=False):
        """
        Custom version of the default method in order to provide access to alchemy instances.

        Args:
            category (hamster_lib.Category): Category we want.
            raw (bool): Wether to return the AlchemyCategory instead.

        Returns:
            hamster_lib.Category or None: Category.
        """

        message = _("Recieved {!r} and raw={}.".format(category, raw))
        self.store.logger.debug(message)

        try:
            category = self.get_by_name(category.name, raw=raw)
        except KeyError:
            category = self._add(category, raw=raw)
        return category

    def _add(self, category, raw=False):
        """
        Add a new category to the database.

        This method should not be used by any client code. Call ``save`` to make
        the decission wether to modify an existing entry or to add a new one is
        done correctly..

        Args:
            category (hamster_lib.Category): Hamster Category instance.
            raw (bool): Wether to return the AlchemyCategory instead.

        Returns:
            hamster_lib.Category: Saved instance, as_hamster()

        Raises:
            ValueError: If the name to be added is already present in the db.
            ValueError: If category passed already got an PK. Indicating that update would
                be more apropiate.
        """

        message = _("Recieved {!r} and raw={}.".format(category, raw))
        self.store.logger.debug(message)

        if category.pk:
            message = _(
                "The category ('{!r}') you are trying to add already has an PK."
                " Are you sure you do not want to ``_update`` instead?".format(category)
            )
            self.store.logger.error(message)
            raise ValueError(message)
        alchemy_category = AlchemyCategory(pk=None, name=category.name)
        self.store.session.add(alchemy_category)
        try:
            self.store.session.commit()
        except IntegrityError as e:
            message = _(
                "An error occured! Are you sure the category.name is not already present in our"
                " database? Here is the full original exception: '{}'.".format(e)
            )
            self.store.logger.error(message)
            raise ValueError(message)
        self.store.logger.debug(_("'{!r}' added.".format(alchemy_category)))

        if not raw:
            alchemy_category = alchemy_category.as_hamster()
        return alchemy_category

    def _update(self, category):
        """
        Update a given Category.

        Args:
            category (hamster_lib.Category): Category to be updated.

        Returns:
            hamster_lib.Category: Updated category.

        Raises:
            ValueError: If the new name is already taken.
            ValueError: If category passed does not have a PK.
            KeyError: If no category with passed PK was found.
        """

        message = _("Recieved {!r}.".format(category))
        self.store.logger.debug(message)

        if not category.pk:
            message = _(
                "The category passed ('{!r}') does not seem to havea PK. We don't know"
                "which entry to modify.".format(category)
            )
            self.store.logger.error(message)
            raise ValueError(message)
        alchemy_category = self.store.session.query(AlchemyCategory).get(category.pk)
        if not alchemy_category:
            message = _("No category with PK: {} was found!".format(category.pk))
            self.store.logger.error(message)
            raise KeyError(message)
        alchemy_category.name = category.name

        try:
            self.store.session.commit()
        except IntegrityError as e:
            message = _(
                "An error occured! Are you sure the category.name is not already present in our"
                " database? Here is the full original exception: '{}'.".format(e)
            )
            self.store.logger.error(message)
            raise ValueError(message)

        return alchemy_category.as_hamster()

    def remove(self, category):
        """
        Delete a given category.

        Args:
            category (hamster_lib.Category): Category to be removed.

        Returns:
            None: If everything went alright.

        Raises:
            KeyError: If the ``Category`` can not be found by the backend.
            ValueError: If category passed does not have an pk.
        """

        message = _("Recieved {!r}.".format(category))
        self.store.logger.debug(message)

        if not category.pk:
            message = _("PK-less Category. Are you trying to remove a new Category?")
            self.store.logger.error(message)
            raise ValueError(message)
        alchemy_category = self.store.session.query(AlchemyCategory).get(category.pk)
        if not alchemy_category:
            message = _("``Category`` can not be found by the backend.")
            self.store.logger.error(message)
            raise KeyError(message)
        self.store.session.delete(alchemy_category)
        message = _("{!r} successfully deleted.".format(category))
        self.store.logger.debug(message)
        self.store.session.commit()

    def get(self, pk):
        """
        Return a category based on their pk.

        Args:
            pk (int): PK of the category to be retrieved.

        Returns:
            hamster_lib.Category: Category matching given PK.

        Raises:
            KeyError: If no such PK was found.

        Note:
            We need this for now, as the service just provides pks, not names.
        """

        message = _("Recieved PK: '{}'.".format(pk))
        self.store.logger.debug(message)

        result = self.store.session.query(AlchemyCategory).get(pk)
        if not result:
            message = _("No category with 'pk: {}' was found!".format(pk))
            self.store.logger.error(message)
            raise KeyError(message)
        message = _("Returning {!r}.".format(result))
        self.store.logger.debug(message)
        return result.as_hamster()

    def get_by_name(self, name, raw=False):
        """
        Return a category based on its name.

        Args:
            name (str): Unique name of the category.
            raw (bool): Wether to return the AlchemyCategory instead.


        Returns:
            hamster_lib.Category: Category of given name.

        Raises:
            KeyError: If no category matching the name was found.

        """

        message = _("Recieved name: '{}', raw={}.".format(name, raw))
        self.store.logger.debug(message)

        name = text_type(name)
        try:
            result = self.store.session.query(AlchemyCategory).filter_by(name=name).one()
        except NoResultFound:
            message = _("No category with 'name: {}' was found!".format(name))
            self.store.logger.error(message)
            raise KeyError(message)

        if not raw:
            result = result.as_hamster()
            self.store.logger.debug(_("Returning: {!r}.").format(result))
        return result

    def get_all(self):
        """
        Get all categories.

        Returns:
            list: List of all Categories present in the database, ordered by lower(name).
        """

        # We avoid the costs of always computing the length of the returned list
        # or even spamming the logs with the enrire list. Instead we just state
        # that we return something.
        self.store.logger.debug(_("Returning list of all categories."))
        return [alchemy_category for alchemy_category in (
            self.store.session.query(AlchemyCategory).order_by(AlchemyCategory.name).all())]


@python_2_unicode_compatible
class ActivityManager(storage.BaseActivityManager):

    def get_or_create(self, activity, raw=False):
        """
        Custom version of the default method in order to provide access to alchemy instances.

        Args:
            activity (hamster_lib.Activity): Activity we want.
            raw (bool): Wether to return the AlchemyActivity instead.

        Returns:
            hamster_lib.Activity: Activity.
        """

        message = _("Recieved {!r}, raw={}.".format(activity, raw))
        self.store.logger.debug(message)

        try:
            result = self.get_by_composite(activity.name, activity.category, raw=raw)
        except KeyError:
            result = self._add(activity, raw=raw)
        self.store.logger.debug(_("Returning {!r}.").format(result))
        return result

    def _add(self, activity, raw=False):
        """
        Add a new ``Activity`` instance to the databasse.

        Args:
            activity (hamster_lib.Activity): Hamster activity

        Returns:
            hamster_lib.Activity: Hamster activity representation of stored instance.

        Raises:
            ValueError: If the passed activity has a PK.
            ValueError: If the category/activity.name combination to be added is
                already present in the db.
        """

        message = _("Recieved {!r}, raw={}.".format(activity, raw))
        self.store.logger.debug(message)

        if activity.pk:
            message = _(
                "The activity ('{!r}') you are trying to add already has an PK."
                " Are you sure you do not want to ``_update`` instead?".format(activity)
            )
            self.store.logger.error(message)
            raise ValueError(message)

        try:
            self.get_by_composite(activity.name, activity.category)
            message = _("Our database already contains the passed name/category.name"
                        "combination.")
            self.store.logger.error(message)
            raise ValueError(message)
        except KeyError:
            pass

        alchemy_activity = AlchemyActivity(None, activity.name, None,
            activity.deleted)
        if activity.category:
            try:
                category = self.store.categories.get_by_name(
                    activity.category.name, raw=True)
            except KeyError:
                category = AlchemyCategory(None, activity.category.name)
        else:
            category = None
        alchemy_activity.category = category
        self.store.session.add(alchemy_activity)
        self.store.session.commit()
        result = alchemy_activity
        if not raw:
            result = alchemy_activity.as_hamster()
        self.store.logger.debug(_("Returning {!r}.").format(result))
        return result

    def _update(self, activity):
        """
        Update a given Activity.

        Args:
            activity (hamster_lib.Activity): Activity to be updated.

        Returns:
            hamster_lib.Activity: Updated activity.

        Raises:
            ValueError: If the new name/category.name combination is already taken.
            ValueError: If the the passed activity does not have a PK assigned.
            KeyError: If the the passed activity.pk can not be found.
        """

        message = _("Recieved {!r}.".format(activity))
        self.store.logger.debug(message)

        if not activity.pk:
            message = _(
                "The activity passed ('{!r}') does not seem to havea PK. We don't know"
                "which entry to modify.".format(activity))
            self.store.logger.error(message)
            raise ValueError(message)

        try:
            self.get_by_composite(activity.name, activity.category)
            message = _("Our database already contains the passed name/category.name"
                        "combination.")
            self.store.logger.error(message)
            raise ValueError(message)
        except KeyError:
            pass

        alchemy_activity = self.store.session.query(AlchemyActivity).get(activity.pk)
        if not alchemy_activity:
            message = _("No activity with this pk can be found.")
            self.store.logger.error(message)
            raise KeyError(message)
        alchemy_activity.name = activity.name
        alchemy_activity.category = self.store.categories.get_or_create(activity.category,
            raw=True)
        alchemy_activity.deleted = activity.deleted
        try:
            self.store.session.commit()
        except IntegrityError as e:
            message = _("There seems to already be an activity like this for the given category."
                "Can not change this activities values. Original exception: {}".format(e))
            self.store.logger.error(message)
            raise ValueError(message)
        result = alchemy_activity.as_hamster()
        self.store.logger.debug(_("Returning: {!r}.".format(result)))
        return result

    def remove(self, activity):
        """
        Remove an activity from our internal backend.

        Args:
            activity (hamster_lib.Activity): The activity to be removed.

        Returns:
            bool: True

        Raises:
            KeyError: If the given ``Activity`` can not be found in the database.
        """

        message = _("Recieved {!r}.".format(activity))
        self.store.logger.debug(message)

        if not activity.pk:
            message = _("The activity you passed does not have a PK. Please provide one.")
            self.store.logger.error(message)
            raise ValueError(message)

        alchemy_activity = self.store.session.query(AlchemyActivity).get(activity.pk)
        if not alchemy_activity:
            message = _("The activity you try to remove does not seem to exist.")
            self.store.logger.error(message)
            raise KeyError(message)
        if alchemy_activity.facts:
            alchemy_activity.deleted = True
            self.store.activities._update(alchemy_activity)
        else:
            self.store.session.delete(alchemy_activity)
        self.store.session.commit()
        self.store.logger.debug(_("Deleted {!r}.".format(activity)))
        return True

    def get(self, pk, raw=False):
        """
        Query for an Activity with given key.

        Args:
            pk: PK to look up.
            raw (bool): Return the AlchemyActivity instead.

        Returns:
            hamster_lib.Activity: Activity with given PK.

        Raises:
            KeyError: If no such pk was found.
        """

        message = _("Recieved PK: '{}', raw={}.".format(pk, raw))
        self.store.logger.debug(message)

        result = self.store.session.query(AlchemyActivity).get(pk)
        if not result:
            message = _("No Activity with 'pk: {}' was found!".format(pk))
            self.store.logger.error(message)
            raise KeyError(message)
        if not raw:
            result = result.as_hamster()
        self.store.logger.debug(_("Returning: {!r}.".format(result)))
        return result

    def get_by_composite(self, name, category, raw=False):
        """
        Retrieve an activity by its name and category)

        Args:
            name (str): The activities name.
            category (hamster_lib.Category or None): The activities category. May be None.
            raw (bool): Return the AlchemyActivity instead.

        Returns:
            hamster_lib.Activity: The activity if it exists in this combination.

        Raises:
            KeyError: if composite key can not be found in the db.

        Note:
            As far as we understand the legacy code in ``__change_category`` and
            ``__get_activity_by`` the combination of activity.name and
            activity.category is unique. This is reflected in the uniqueness constraint
            of the underlying table.
        """

        message = _("Recieved name: '{}' and {!r} with 'raw'={}.".format(name, category, raw))
        self.store.logger.debug(message)

        name = str(name)
        if category:
            category = text_type(category.name)
            try:
                alchemy_category = self.store.categories.get_by_name(category, raw=True)
            except KeyError:
                message = _(
                    "The category passed ({}) does not exist in the backend. Consequently no"
                    " related activity can be returned.".format(category)
                )
                self.store.logger.error(message)
                raise KeyError(message)
        else:
            alchemy_category = None

        try:
            result = self.store.session.query(AlchemyActivity).filter_by(name=name).filter_by(
                category=alchemy_category).one()
        except NoResultFound:
            message = _(
                "No activity of given combination (name: {name}, category: {category})"
                " could be found.".format(name=name, category=category)
            )
            self.store.logger.error(message)
            raise KeyError(message)
        if not raw:
            result = result.as_hamster()
        self.store.logger.debug(_("Returning: {!r}.".format(result)))
        return result

    def get_all(self, category=False, search_term=''):
        """
        Retrieve all matching activities stored in the backend.

        Args:
            category (hamster_lib.Category, optional): Limit activities to this category.
                Defaults to ``False``. If ``category=None`` only activities without a
                category will be considered.
            search_term (str, optional): Limit activities to those matching this string a substring
                in their name. Defaults to ``empty string``.

        Returns:
            list: List of ``hamster_lib.Activity`` instances matching constrains. This list
                is ordered by ``Activity.name``.
        """

        message = _("Recieved '{!r}', 'search_term'={}.".format(category, search_term))
        self.store.logger.debug(message)

        query = self.store.session.query(AlchemyActivity)

        if category is not False:
            if category:
                alchemy_category = self.store.session.query(AlchemyCategory).get(category.pk)
            else:
                alchemy_category = None
            query = query.filter_by(category=alchemy_category)
        else:
            pass

        if search_term:
            query = query.filter(AlchemyActivity.name.ilike('%{}%'.format(search_term)))
        query.order_by(AlchemyActivity.name)
        self.store.logger.debug(_("Returning list of matches."))
        return query.all()


@python_2_unicode_compatible
class TagManager(storage.BaseTagManager):
    def get_or_create(self, tag, raw=False):
        """
        Custom version of the default method in order to provide access to alchemy instances.

        Args:
            tag (hamster_lib.Tag): Tag we want.
            raw (bool): Wether to return the AlchemyTag instead.

        Returns:
            hamster_lib.Tag or None: Tag.
        """

        message = _("Recieved {!r} and raw={}.".format(tag, raw))
        self.store.logger.debug(message)

        try:
            tag = self.get_by_name(tag.name, raw=raw)
        except KeyError:
            tag = self._add(tag, raw=raw)
        return tag

    def _add(self, tag, raw=False):
        """
        Add a new tag to the database.

        This method should not be used by any client code. Call ``save`` to make
        the decission wether to modify an existing entry or to add a new one is
        done correctly..

        Args:
            tag (hamster_lib.Tag): Hamster Tag instance.
            raw (bool): Wether to return the AlchemyTag instead.

        Returns:
            hamster_lib.Tag: Saved instance, as_hamster()

        Raises:
            ValueError: If the name to be added is already present in the db.
            ValueError: If tag passed already got an PK. Indicating that update would
                be more apropiate.
        """

        message = _("Recieved {!r} and raw={}.".format(tag, raw))
        self.store.logger.debug(message)

        if tag.pk:
            message = _(
                "The tag ('{!r}') you are trying to add already has an PK."
                " Are you sure you do not want to ``_update`` instead?".format(tag)
            )
            self.store.logger.error(message)
            raise ValueError(message)
        alchemy_tag = AlchemyTag(pk=None, name=tag.name)
        self.store.session.add(alchemy_tag)
        try:
            self.store.session.commit()
        except IntegrityError as e:
            message = _(
                "An error occured! Are you sure the tag.name is not already present in our"
                " database? Here is the full original exception: '{}'.".format(e)
            )
            self.store.logger.error(message)
            raise ValueError(message)
        self.store.logger.debug(_("'{!r}' added.".format(alchemy_tag)))

        if not raw:
            alchemy_tag = alchemy_tag.as_hamster()
        return alchemy_tag

    def _update(self, tag):
        """
        Update a given Tag.

        Args:
            tag (hamster_lib.Tag): Tag to be updated.

        Returns:
            hamster_lib.Tag: Updated tag.

        Raises:
            ValueError: If the new name is already taken.
            ValueError: If tag passed does not have a PK.
            KeyError: If no tag with passed PK was found.
        """

        message = _("Recieved {!r}.".format(tag))
        self.store.logger.debug(message)

        if not tag.pk:
            message = _(
                "The tag passed ('{!r}') does not seem to havea PK. We don't know"
                "which entry to modify.".format(tag)
            )
            self.store.logger.error(message)
            raise ValueError(message)
        alchemy_tag = self.store.session.query(AlchemyTag).get(tag.pk)
        if not alchemy_tag:
            message = _("No tag with PK: {} was found!".format(tag.pk))
            self.store.logger.error(message)
            raise KeyError(message)
        alchemy_tag.name = tag.name

        try:
            self.store.session.commit()
        except IntegrityError as e:
            message = _(
                "An error occured! Are you sure the tag.name is not already present in our"
                " database? Here is the full original exception: '{}'.".format(e)
            )
            self.store.logger.error(message)
            raise ValueError(message)

        return alchemy_tag.as_hamster()

    def remove(self, tag):
        """
        Delete a given tag.

        Args:
            tag (hamster_lib.Tag): Tag to be removed.

        Returns:
            None: If everything went alright.

        Raises:
            KeyError: If the ``Tag`` can not be found by the backend.
            ValueError: If tag passed does not have an pk.
        """

        message = _("Recieved {!r}.".format(tag))
        self.store.logger.debug(message)

        if not tag.pk:
            message = _("PK-less Tag. Are you trying to remove a new Tag?")
            self.store.logger.error(message)
            raise ValueError(message)
        alchemy_tag = self.store.session.query(AlchemyTag).get(tag.pk)
        if not alchemy_tag:
            message = _("``Tag`` can not be found by the backend.")
            self.store.logger.error(message)
            raise KeyError(message)
        self.store.session.delete(alchemy_tag)
        message = _("{!r} successfully deleted.".format(tag))
        self.store.logger.debug(message)
        self.store.session.commit()

    def get(self, pk):
        """
        Return a tag based on their pk.

        Args:
            pk (int): PK of the tag to be retrieved.

        Returns:
            hamster_lib.Tag: Tag matching given PK.

        Raises:
            KeyError: If no such PK was found.

        Note:
            We need this for now, as the service just provides pks, not names.
        """

        message = _("Recieved PK: '{}'.".format(pk))
        self.store.logger.debug(message)

        result = self.store.session.query(AlchemyTag).get(pk)
        if not result:
            message = _("No tag with 'pk: {}' was found!".format(pk))
            self.store.logger.error(message)
            raise KeyError(message)
        message = _("Returning {!r}.".format(result))
        self.store.logger.debug(message)
        return result.as_hamster()

    def get_by_name(self, name, raw=False):
        """
        Return a tag based on its name.

        Args:
            name (str): Unique name of the tag.
            raw (bool): Wether to return the AlchemyTag instead.


        Returns:
            hamster_lib.Tag: Tag of given name.

        Raises:
            KeyError: If no tag matching the name was found.

        """

        message = _("Recieved name: '{}', raw={}.".format(name, raw))
        self.store.logger.debug(message)

        name = text_type(name)
        try:
            result = self.store.session.query(AlchemyTag).filter_by(name=name).one()
        except NoResultFound:
            message = _("No tag with 'name: {}' was found!".format(name))
            self.store.logger.error(message)
            raise KeyError(message)

        if not raw:
            result = result.as_hamster()
            self.store.logger.debug(_("Returning: {!r}.").format(result))
        return result

    def get_all(self):
        """
        Get all tags.

        Returns:
            list: List of all Categories present in the database, ordered by lower(name).
        """

        # We avoid the costs of always computing the length of the returned list
        # or even spamming the logs with the enrire list. Instead we just state
        # that we return something.
        self.store.logger.debug(_("Returning list of all tags."))
        return [alchemy_tag for alchemy_tag in (
            self.store.session.query(AlchemyTag).order_by(AlchemyTag.name).all())]


@python_2_unicode_compatible
class FactManager(storage.BaseFactManager):
    def _add(self, fact, raw=False):
        """
        Add a new fact to the database.

        Args:
            fact (hamster_lib.Fact): Fact to be added.
            raw (bool): If ``True`` return ``AlchemyFact`` instead.

        Returns:
            hamster_lib.Fact: Fact as stored in the database

        Raises:
            ValueError: If the passed fact has a PK assigned. New facts should not have one.
            ValueError: If the timewindow is already occupied.
        """

        self.store.logger.debug(_("Received '{!r}', 'raw'={}.".format(fact, raw)))

        if fact.pk:
            message = _(
                "The fact ('{!r}') you are trying to add already has an PK."
                " Are you sure you do not want to ``_update`` instead?".format(fact)
            )
            self.store.logger.error(message)
            raise ValueError(message)

        if self._get_all(fact.start, fact.end, partial=True):
            message = _("Our database already contains facts for this facts timewindow."
                        "There can ever only be one fact at any given point in time")
            self.store.logger.error(message)
            raise ValueError(message)

        alchemy_fact = AlchemyFact(None, None, fact.start, fact.end, fact.description)
        alchemy_fact.activity = self.store.activities.get_or_create(fact.activity, raw=True)
        alchemy_fact.tags = [self.store.tags.get_or_create(tag, raw=True) for tag in fact.tags]
        self.store.session.add(alchemy_fact)
        self.store.session.commit()
        self.store.logger.debug(_("Added {!r}.".format(alchemy_fact)))
        return alchemy_fact

    def _update(self, fact, raw=False):
        """
        Update and existing fact with new values.

        Args:
            fact (hamster_lib.fact): Fact instance holding updated values.
            raw (bool): If ``True`` return ``AlchemyFact`` instead.

        Returns:
            hamster_lib.fact: Updated Fact

        Raises:
            KeyError: if a Fact with the relevant PK could not be found.
            ValueError: If the the passed activity does not have a PK assigned.
            ValueError: If the timewindow is already occupied.
        """

        self.store.logger.debug(_("Recieved '{!r}', 'raw'={}.".format(fact, raw)))

        if not fact.pk:
            message = _(
                "{!r} does not seem to have a PK. We don't know"
                "which entry to modify.".format(fact)
            )
            self.store.logger.error(message)
            raise ValueError(message)

        facts_in_timeframe = self._get_all(fact.start, fact.end, partial=True)
        # This works because the conditional gets evaluated from left to right.
        # If ``facts_in_timeframe`` would be empty and hence would throw an
        # index error, we wouldn't reach the offending part ...
        if facts_in_timeframe and not (len(facts_in_timeframe) == 1 and
                                       facts_in_timeframe[0].pk == fact.pk):
            message = _("Our database already contains facts for this facts timewindow."
                        " There can ever only be one fact at any given point in time")
            self.store.logger.error(message)
            raise ValueError(message)

        alchemy_fact = self.store.session.query(AlchemyFact).get(fact.pk)
        if not alchemy_fact:
            message = _("No fact with PK: {} was found.".format(fact.pk))
            self.store.logger.error(message)
            raise KeyError(message)

        alchemy_fact.start = fact.start
        alchemy_fact.end = fact.end
        alchemy_fact.description = fact.description
        alchemy_fact.activity = self.store.activities.get_or_create(fact.activity, raw=True)
        tags = [self.store.tags.get_or_create(tag, raw=True) for tag in fact.tags]
        alchemy_fact.tags = tags
        self.store.session.commit()
        self.store.logger.debug(_("{!r} has been updated.".format(fact)))
        return fact

    def remove(self, fact):
        """
        Remove a fact from our internal backend.

        Args:
            fact (hamster_lib.Fact): Fact to be removed

        Returns:
            bool: Success status

        Raises:
            ValueError: If fact passed does not have an pk.
            KeyError:If no fact with passed PK was found.
        """

        self.store.logger.debug(_("Recieved '{!r}'.".format(fact)))

        if not fact.pk:
            message = _(
                "The fact passed ('{!r}') does not seem to havea PK. We don't know"
                "which entry to remove.".format(fact)
            )
            self.store.logger.error(message)
            raise ValueError(message)

        alchemy_fact = self.store.session.query(AlchemyFact).get(fact.pk)
        if not alchemy_fact:
            message = _("No fact with given pk was found!")
            self.store.logger.error(message)
            raise KeyError(message)
        self.store.session.delete(alchemy_fact)
        self.store.session.commit()
        self.store.logger.debug(_("{!r} has been removed.".format(fact)))
        return True

    def get(self, pk, raw=False):
        """
        Retrieve a fact based on its PK.

        Args:
            pk: PK of the fact to be retrieved

        Returns:
            hamster_lib.Fact: Fact matching given PK

        Raises:
            KeyError: If no Fact of given key was found.
        """

        self.store.logger.debug(_("Recieved PK: {}', 'raw'={}.".format(pk, raw)))

        result = self.store.session.query(AlchemyFact).get(pk)
        if not result:
            message = _("No fact with given PK found.")
            self.store.logger.error(message)
            raise KeyError(message)
        if not raw:
            result = result.as_hamster()
        self.store.logger.debug(_("Returning {!r}.".format(result)))
        return result

    def _get_all(self, start=None, end=None, search_term='', partial=False):
        """
        Return all facts within a given timeframe that match given search terms.

        ``get_all`` already took care of any normalization required.

        If no timeframe is given, return all facts?

        Args:
            start (datetime.datetime, optional): Start of timeframe.
            end (datetime.datetime, optional): End of timeframe.
            search_term (text_type): Cases insensitive strings to match
                ``Activity.name`` or ``Category.name``.
            partial (bool): If ``False`` only facts which start *and* end
                within the timeframe will be considered.

        Returns:
            list: List of ``hamster_lib.Facts`` instances.
        """

        def get_complete_overlaps(query, start, end):
            """Return all facts with start and end within the timeframe."""

            # SQLAlchemy does not allow ``<=`` used with ``None`` values, so we have
            # check for passed arguments first.
            if start:
                query = query.filter(AlchemyFact.start >= start)
            if end:
                query = query.filter(AlchemyFact.end <= end)
            return query

        def get_partial_overlaps(query, start, end):
            """Return all facts where either start or end falls within the timeframe."""

            # SQLAlchemy does not allow ``<=`` used with ``None`` values, so we have
            # check for passed arguments first.
            if start and not end:
                query = query.filter(or_(AlchemyFact.start >= start, AlchemyFact.end >= start))
            elif not start and end:
                query = query.filter(or_(AlchemyFact.start <= end, AlchemyFact.end <= end))
            elif start and end:
                query = query.filter(or_(
                    and_(AlchemyFact.start >= start, AlchemyFact.start <= end),
                    and_(AlchemyFact.end >= start, AlchemyFact.end <= end),
                ))
            else:
                pass
            return query

        def filter_search_term(query, term):
            """
            Limit query to facts that match the search terms.

            Terms are matched against ``Category.name`` and ``Activity.name``.
            The matching is not case sensitive.
            """
            query = query.join(AlchemyActivity).join(AlchemyCategory).filter(
                or_(AlchemyActivity.name.ilike('%{}%'.format(search_term)),
                    AlchemyCategory.name.ilike('%{}%'.format(search_term))
                    )
            )
            return query

        self.store.logger.debug(_(
            "Received start: '{}', end: '{}' and search_term='{}'.".format(
                start, end, search_term)
        ))

        # [FIXME] Figure out against what to match search_terms
        query = self.store.session.query(AlchemyFact)

        if partial:
            query = get_partial_overlaps(query, start, end)
        else:
            query = get_complete_overlaps(query, start, end)

        if search_term:
            query = filter_search_term(query, search_term)

        # [FIXME]
        # Depending on scale, this could be a problem.
        self.store.logger.debug(_("Returning list of results."))
        return [fact.as_hamster() for fact in query.all()]
