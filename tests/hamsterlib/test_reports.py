# -*- encoding: utf-8 -*-

from __future__ import unicode_literals
from six import text_type

import pytest
import os.path
import sys
import csv
from hamsterlib import reports


@pytest.fixture
def path(tmpdir):
    path = tmpdir.mkdir('reports').join('report.csv').strpath
    return text_type(path)


@pytest.fixture
def report_writer(path):
    return reports.ReportWriter(path)


@pytest.fixture
def tsv_writer(path):
    return reports.TSVWriter(path)


class TestReportWriter(object):
    @pytest.mark.parametrize('datetime_format', [None, '%Y-%m-%d'])
    def test_init_stores_datetime_format(self, path, datetime_format):
        """Make sure that Writer initialization stores the ``datetime_format``."""
        writer = reports.ReportWriter(path, datetime_format)
        assert writer.datetime_format == datetime_format

    def test_init_file_opened(self, path):
        """Make sure a file like object is beeing opened."""
        writer = reports.ReportWriter(path)
        assert os.path.isfile(path)
        assert writer.file.closed is False

    def test__fact_to_tuple_no_category(self, report_writer, fact):
        """Make sure that ``None`` category values translate to ``empty strings``."""
        fact.activity.category = None
        result = report_writer._fact_to_tuple(fact)
        assert result.category == ''

    def test__fact_to_tuple_with_category(self, report_writer, fact):
        """Make sure that category references translate to their names."""
        result = report_writer._fact_to_tuple(fact)
        assert result.category == fact.category.name

    def test_write_report_write_lines(self, mocker, report_writer, list_of_facts):
        """Make sure that each ``Fact`` instances triggers a new line."""
        number_of_facts = 10
        facts = list_of_facts(number_of_facts)
        report_writer._write_fact = mocker.MagicMock(return_value=None)
        report_writer.write_report(facts)
        assert report_writer._write_fact.call_count == number_of_facts

    def test_write_report_file_closed(self, report_writer, list_of_facts):
        """Make sure our output file is closed at the end."""
        facts = list_of_facts(10)
        with pytest.raises(NotImplementedError):
            report_writer.write_report(facts)
        assert report_writer.file.closed is False

    def test__close(self, report_writer, path):
        """Ensure that the the output gets closed."""
        report_writer._close()
        assert report_writer.file.closed


class TestTSVWriter(object):
    def test_init_csv_writer(self, tsv_writer):
        """Make sure that initialition provides us with a ``csv.writer`` instance."""
        assert tsv_writer.csv_writer
        assert tsv_writer.csv_writer.dialect == csv.get_dialect('excel-tab')

    def test_init_heading(self, path, tsv_writer):
        """Make sure that initialition writes header as expected."""

        expectation = (
            'start time',
            'end time',
            'activityöß',
            'category',
            'description',
            'duration minutes',
        )

        tsv_writer._close()
        # with codecs.open(path, 'r', encoding='utf-8') as fobj:
        with open(path, 'r') as fobj:
            reader = csv.reader(fobj, dialect='excel-tab')
            header = next(reader)
        for item in header:
            i = header.index(item)
            item == expectation[i]

    def test__write_fact(self, path, fact, tsv_writer):
        """Make sure the writen fact is what we expect."""
        # [TODO]
        # Spliting the code path works but is mighty ugly. However, we
        # encountered numerous problems finding a unified solution.
        # Try again later or once we finaly drop py27 support.
        fact_tuple = tsv_writer._fact_to_tuple(fact)
        tsv_writer._write_fact(fact_tuple)
        tsv_writer._close()
        if sys.version_info < (3, 0):
            # python 2 prefers binary and then decode
            with open(path, 'rb') as fobj:
                reader = csv.reader(fobj, dialect='excel-tab')
                reader.next()
                line = reader.next()
                for i in line:
                    index = line.index(i)
                    assert i.decode('utf-8') == fact_tuple[index]
        else:
            # python 3 insists on text, so we can iterate over
            with open(path, 'r', encoding='utf-8') as fobj:
                reader = csv.reader(fobj, dialect='excel-tab')
                next(reader)
                line = next(reader)
                for i in line:
                    index = line.index(i)
                    assert i == fact_tuple[index]
