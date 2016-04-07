# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

import csv
import os.path

import pytest
from hamsterlib import reports
from six import text_type


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

        expectations = (
            'start time',
            'end time',
            'activity',
            'category',
            'description',
            'duration minutes',
        )

        tsv_writer._close()
        with open(path, 'r') as fobj:
            reader = csv.reader(fobj, dialect='excel-tab')
            header = next(reader)
        for field, expectation in zip(header, expectations):
            if isinstance(field, text_type):
                assert field == expectation
            else:
                assert field.decode('utf-8') == expectation

    def test__write_fact(self, path, fact, tsv_writer):
        """Make sure the writen fact is what we expect."""
        fact_tuple = tsv_writer._fact_to_tuple(fact)
        tsv_writer._write_fact(fact_tuple)
        tsv_writer._close()
        with open(path, 'r') as fobj:
            reader = csv.reader(fobj, dialect='excel-tab')
            next(reader)
            line = next(reader)
            for field, expectation in zip(line, fact_tuple):
                if isinstance(field, text_type):
                    assert field == expectation
                else:
                    assert field.decode('utf-8') == expectation
