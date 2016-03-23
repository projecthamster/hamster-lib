# - coding: utf-8 -

import csv
from gettext import gettext as _

from collections import namedtuple


FactTuple = namedtuple('FactTuple', ('start', 'end', 'activity', 'category',
    'description', 'duration'))


class ReportWriter(object):
    def __init__(self, path, datetime_format="%Y-%m-%d %H:%M:%S"):
        self.datetime_format = datetime_format
        self.file = open(path, 'w')

    def write_report(self, facts):
            for fact in facts:
                if fact.category:
                    category = fact.category.name
                else:
                    category = ''

                if fact.description:
                    description = fact.description
                else:
                    description = ''
                fact = FactTuple(
                    start=fact.start.strftime(self.datetime_format),
                    end=fact.end.strftime(self.datetime_format),
                    activity=fact.activity.name,
                    duration=fact.get_string_delta('%H:%M'),
                    category=category,
                    description=description,
                )
                self._write_fact(fact)
            self._close()

    def _write_fact(self, fact):
        raise NotImplementedError

    def _close(self):
        self.file.close()


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
