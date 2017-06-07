# - coding: utf-8 -

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


"""
Module to provide generic reporting capabilities for easy adaption by clients.

The basic idea is to provide ``Writer`` classes that take care of the bulk of the setup
upon instantiation so all the client needs to do is to call ``write_report`` with a list
of ``FactTuples`` as arguments.
"""


from __future__ import unicode_literals

import csv
import datetime
import sys
from collections import namedtuple
from xml.dom.minidom import Document

from future.utils import python_2_unicode_compatible
from icalendar import Calendar, Event
from six import text_type

FactTuple = namedtuple('FactTuple', ('start', 'end', 'activity', 'category',
    'description', 'duration'))


@python_2_unicode_compatible
class ReportWriter(object):
    def __init__(self, path, datetime_format="%Y-%m-%d %H:%M:%S"):
        """
        Initiate new instance and open an output file like object.

        Note:
            If you need added bells and wristels (like heading etc.) this would probably
            the method to extend.

        Args:
            path: File like object to be opened. This is where all output will be directed to.
            datetime_format (str): String specifying how datetime information is to be
                rendered in the output.
        """
        self.datetime_format = datetime_format
        # No matter through what loops we jump, at the end of the day py27
        # ``writerow`` will insist on casting our data to binary str()
        # instances. This clearly conflicts with any generic open() that provides
        # transparent text input/output and would take care of the encoding
        # instead.

        # [FIXME]
        # If it turns out that this is specific to csv handling we may move it
        # there and use a simpler default behaviour for our base method.
        if sys.version_info < (3,):
            self.file = open(path, 'wb')
        else:
            self.file = open(path, 'w', encoding='utf-8')

    def write_report(self, facts):
        """
        Write facts to file output and make sure the file like object is closed at the end.

        Args:
            facts (Iterable): Iterable of ``hamster_lib.Fact`` instances to be exported.

        Returns:
            None: If everything worked as expected.
        """
        for fact in facts:
            self._write_fact(self._fact_to_tuple(fact))
        self._close()

    def _fact_to_tuple(self, fact):
        """
        Convert a ``Fact`` to its normalized tuple.

        This is where all type conversion for ``Fact`` attributes to strings as well
        as any normalization happens.

        Note:
            Because different writers may require different types, we need to so this
            individualy.

        Args:
            fact (hamster_lib.Fact): Fact to be converted.

        Returns:
            FactTuple: Tuple representing the original ``Fact``.
        """
        raise NotImplementedError

    def _write_fact(self, fact):
        """
        Represent one ``Fact`` in the output file.

        What this means exactly depends on the format and kind of output.
        At this point all type conversions and normalization have already been done.

        Args:
            fact (FactTuple): The individual fact to be written.

        Returns:
            None
        """
        raise NotImplementedError

    def _close(self):
        """Default teardown method."""
        self.file.close()


@python_2_unicode_compatible
class TSVWriter(ReportWriter):
    def __init__(self, path):
        """
        Initialize a new instance.

        Besides our default behaviour we create a localized heading.
        Also, we need to make sure that our heading is UTF-8 encoded on python 2!
        In that case ``self.file`` will be openend in binary mode and ready to accept
        those encoded headings.
        """
        super(TSVWriter, self).__init__(path)
        self.csv_writer = csv.writer(self.file, dialect='excel-tab')
        headers = (
            _("start time"),
            _("end time"),
            _("activity"),
            _("category"),
            _("description"),
            _("duration minutes"),
        )
        results = []
        for h in headers:
            data = text_type(h)
            if sys.version_info < (3, 0):
                data = data.encode('utf-8')
            results.append(data)
        self.csv_writer.writerow(results)

    def _fact_to_tuple(self, fact):
        """
        Convert a ``Fact`` to its normalized tuple.

        This is where all type conversion for ``Fact`` attributes to strings as well
        as any normalization happens.

        Args:
            fact (hamster_lib.Fact): Fact to be converted.

        Returns:
            FactTuple: Tuple representing the original ``Fact``.
        """
        # Fields that may have ``None`` value will be represented by ''
        if fact.category:
            category = fact.category.name
        else:
            category = ''

        description = fact.description or ''

        return FactTuple(
            start=fact.start.strftime(self.datetime_format),
            end=fact.end.strftime(self.datetime_format),
            activity=fact.activity.name,
            duration=fact.get_string_delta('%H:%M'),
            category=text_type(category),
            description=description,
        )

    def _write_fact(self, fact_tuple):
        """
        Write a single fact.

        On python 2 we need to make sure we encode our data accordingly so we can feed it to our
        file object which in this case needs to be opened in binary mode.
        """
        results = []
        for value in fact_tuple:
            data = text_type(value)
            if sys.version_info < (3, 0):
                data = data.encode('utf-8')
            results.append(data)
        self.csv_writer.writerow(results)


@python_2_unicode_compatible
class ICALWriter(ReportWriter):
    """A simple ical writer for fact export."""
    def __init__(self, path, datetime_format="%Y-%m-%d %H:%M:%S"):
        """
        Initiate new instance and open an output file like object.

        Args:
            path: File like object to be opend. This is where all output will be directed to.
            datetime_format (str): String specifying how datetime information is to be
                rendered in the output.
        """
        self.datetime_format = datetime_format
        self.file = open(path, 'wb')
        self.calendar = Calendar()

    def _fact_to_tuple(self, fact):
        """
        Convert a ``Fact`` to its normalized tuple.

        This is where all type conversion for ``Fact`` attributes to strings as well
        as any normalization happens.

        Note:
            Because different writers may require different types, we need to so this
            individualy.

        Args:
            fact (hamster_lib.Fact): Fact to be converted.

        Returns:
            FactTuple: Tuple representing the original ``Fact``.
        """
        # Fields that may have ``None`` value will be represented by ''
        if fact.category:
            category = fact.category.name
        else:
            category = ''

        description = fact.description or ''

        return FactTuple(
            start=fact.start,
            end=fact.end,
            activity=text_type(fact.activity.name),
            duration=None,
            category=text_type(category),
            description=text_type(description),
        )

    def _write_fact(self, fact_tuple):
        """
        Write a singular fact to our report.

        Note:
            * ``dtent`` is non-inclusive according to Page 54 of RFC 5545

        Returns:
            None: If everything worked out alright.
        """
        # [FIXME]
        # It apears that date/time requirements for VEVENT have changed between
        # RFCs. 5545 now seems to require a 'dstamp' and a 'uid'!
        event = Event()
        event.add('dtstart', fact_tuple.start)
        event.add('dtend', fact_tuple.end + datetime.timedelta(seconds=1))
        event.add('categories', fact_tuple.category)
        event.add('summary', fact_tuple.activity)
        event.add('description', fact_tuple.description)
        self.calendar.add_component(event)

    def _close(self):
        """Custom close method to make sure the calendar is actually writen do disk."""
        self.file.write(self.calendar.to_ical())
        return super(ICALWriter, self)._close()


class XMLWriter(ReportWriter):
    """Writer for a basic xml export."""

    # This is a straight forward copy of the 'legacy hamster' XMLWriter class
    # contributed by 'tbaugis' in 11e3f66

    def __init__(self, path, datetime_format="%Y-%m-%d %H:%M:%S"):
        """Setup the writer including a main xml document."""
        self.datetime_format = datetime_format
        self.file = open(path, 'wb')
        self.document = Document()
        self.fact_list = self.document.createElement("facts")

    def _fact_to_tuple(self, fact):
        """
        Convert a ``Fact`` to its normalized tuple.

        This is where all type conversion for ``Fact`` attributes to strings as
        well as any normalization happens.

        Note:
            Because different writers may require different types, we need to
            do this individually.

        Args:
            fact (hamster_lib.Fact): Fact to be converted.

        Returns:
            FactTuple: Tuple representing the original ``Fact``.
        """
        # Fields that may have ``None`` value will be represented by ''
        if fact.category:
            category = fact.category.name
        else:
            category = ''

        description = fact.description or ''

        return FactTuple(
            start=fact.start.strftime(self.datetime_format),
            end=fact.end.strftime(self.datetime_format),
            activity=text_type(fact.activity.name),
            duration=fact.get_string_delta(format='%M'),
            category=text_type(category),
            description=text_type(description),
        )

    def _write_fact(self, fact_tuple):
        """
        Create new fact element and populate attributes.

        Once the child is prepared append it to ``fact_list``.
        """
        fact = self.document.createElement("fact")
        fact.setAttribute('start', fact_tuple.start)
        fact.setAttribute('end', fact_tuple.end)
        fact.setAttribute('activity', fact_tuple.activity)
        fact.setAttribute('duration', fact_tuple.duration)
        fact.setAttribute('category', fact_tuple.category)
        fact.setAttribute('description', fact_tuple.description)
        self.fact_list.appendChild(fact)

    def _close(self):
        """
        Append the xml fact list to the main document write file and cleanup.

        ``toxml`` should take care of encoding everything with UTF-8.
        """

        self.document.appendChild(self.fact_list)
        self.file.write(self.document.toxml(encoding='utf-8'))
        return super(XMLWriter, self)._close()
