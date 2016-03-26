# - coding: utf-8 -

from __future__ import unicode_literals
from future.utils import python_2_unicode_compatible
from builtins import str

import csv
from gettext import gettext as _

from collections import namedtuple


"""
Module to provide generic reporting capabilities for easy adaption by clients.

The basic idea is to provide ``Writer`` classes that take care of the bulk of the setup
upon instanciation so all the client needs to do is to call ``write_report`` with a list
of ``FactTuples`` as arguments.
"""

FactTuple = namedtuple('FactTuple', ('start', 'end', 'activity', 'category',
    'description', 'duration'))


@python_2_unicode_compatible
class ReportWriter(object):
    def __init__(self, path, datetime_format="%Y-%m-%d %H:%M:%S"):
        """
        Initiate new instance and open an output file like object.

        Note:
            If you need added bells and wristels (like heading etc.) this would propably
            the method to extend.

        Args:
            path: File like object to be opend. This is where all output will be directed to.
            datetime_format (str): String specifying how datetime information is to be
                rendered in the output.
        """
        self.datetime_format = datetime_format
        self.file = open(path, 'w', encoding='utf-8')

    def write_report(self, facts):
        """
        Write facts to file output and make sure the file like object is closed at the end.

        Args:
            facts (Iterable): Iterable of ``hamsterlib.Fact`` instances to be exported.

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

        Args:
            fact (hamsterlib.Fact): Fact to be converted.

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
            category=category,
            description=description,
        )

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
        self.file.close()


@python_2_unicode_compatible
class TSVWriter(ReportWriter):
    def __init__(self, path):
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

        self.csv_writer.writerow([h for h in headers])

    def _write_fact(self, fact):
        self.csv_writer.writerow(fact)