# -*- encoding: utf-8 -*-
from __future__ import unicode_literals
from past.builtins import basestring

from gettext import gettext as _
import datetime
from calendar import timegm
import re


class Category(object):
    """Storage agnostic class for categories."""

    def __init__(self, name, pk=None):
        self.pk = pk
        self.name = name
        if not self.name:
            raise ValueError(_(
                "Missing a name for our Category instance!"
            ))

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        if not name:
            raise ValueError(_("You need to specify a name."))
        if not isinstance(name, basestring):
            raise TypeError(_("Name must be a string like value."))
        else:
            self._name = name

    def __str__(self):
        return '[{pk}] {name}'.format(pk=self.pk, name=self.name)


class Activity(object):
    """Storage agnostic class for activities."""

    def __init__(self, name, pk=None, category=None, deleted=False):
        self.pk = pk
        self.name = name
        # Check its not empty
        if not self.name:
            raise ValueError(_(
                "Missing a name for our Activity instancec!"
            ))
        self.category = category
        self.deleted = bool(deleted)

    def __str__(self):
        if self.category is  None:
            string = '[{pk}] {name}'.format(pk=self.pk, name=self.name)
        else:
            string = '[{pk}] {name} ({category})'.format(
                pk=self.pk, name=self.name, category=self.category.name)
        return string

    def as_dict(self):
        return {
            'pk': self.pk,
            'name': self.name,
            'category': self.category.pk,
            'deleted': self.deleted,
        }


class Fact(object):
    """Storage agnostic class for facts.

    Note:
        There is some weired black magic still to be integrated from
        store.db.Storage. Among it __get_facts()
    """

    def __init__(self, activity, start, pk=None, end=None, description='', tags=[]):

        self.pk = pk
        if not isinstance(activity, Activity):
            raise TypeError(_(
                "'activity' should be an Activity instance, instead we got"
                " {type}.".format(type=type(activity))
            ))
        self.activity = activity
        self.start = start
        self.end = end
        self.description = description
        self.tags = tags

    @property
    def delta(self):
        """
        Return the offset of start to end for this fact.

        :return: Difference between start- and end datetime. If we only got a
        start datetime, we return None.
        :rtype: datetime.timedelta or None
        """
        return self.end - self.start

    def get_string_delta(self, format='raw'):
        if format == '%M':
            result = int(self.delta.total_seconds())/60
        elif format == '%H:%M':
            seconds = int(self.delta.total_seconds())
            result = '{hours}:{minutes}'.format(hours=(seconds/3600),
                minutes=((seconds%3600)/60))
        else:
            raise ValueError(_("Got invalid format argument."))
        return result



    @property
    def date(self):
        """
        Return the date the fact has started.

        :return: The date the fact has started.
        :rtype: datetime.date
        """
        # [FIXME]
        # Still needed?
        return self.start.date()

    @property
    def serialized_name(self):
        """
        Pattern:
        [<start>-<end>] <activity_name>[@<category_name>, <description_text>]

        Time format information from hamster-cli:
            * 'YYYY-MM-DD hh:mm:ss': If date is missing, it will default to today.
                If time is missing, it will default to 00:00 for start time and 23:59 for
                end time.
            * '-minutes': Relative time in minutes from the current date and time.
        """
        result = str(self.activity.name)

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


    def __str__(self):
        if self.start:
            time = self.start.strftime("%d-%m-%Y %H:%M")
        if self.end:
            time = "%s - %s" % (time, self.end.strftime("%H:%M"))
        return "%s %s" % (time, self.serialized_name)

    def as_dict(self):
        return {
            'pk': self.pk,
            'activity': self.activity,
            'start': self.start,
            'end': self.end,
            'description': self.description,
        }
