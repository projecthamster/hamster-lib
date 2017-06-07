# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

import csv
import datetime
import os.path
import xml

import pytest
from hamster_lib import reports
from icalendar import Calendar
from six import text_type


# Fixtures
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


@pytest.fixture
def ical_writer(path):
    return reports.ICALWriter(path)


@pytest.fixture
def xml_writer(path):
    return reports.XMLWriter(path)


# Tests
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

    def test__fact_to_tuple(self, report_writer, fact):
        with pytest.raises(NotImplementedError):
            report_writer._fact_to_tuple(fact)

    def test_write_report_write_lines(self, mocker, report_writer, list_of_facts):
        """Make sure that each ``Fact`` instances triggers a new line."""
        number_of_facts = 10
        facts = list_of_facts(number_of_facts)
        report_writer._write_fact = mocker.MagicMock(return_value=None)
        report_writer._fact_to_tuple = mocker.MagicMock(return_value=None)
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

    def test__fact_to_tuple_no_category(self, tsv_writer, fact):
        """Make sure that ``None`` category values translate to ``empty strings``."""
        fact.activity.category = None
        result = tsv_writer._fact_to_tuple(fact)
        assert result.category == ''

    def test__fact_to_tuple_with_category(self, tsv_writer, fact):
        """Make sure that category references translate to their names."""
        result = tsv_writer._fact_to_tuple(fact)
        assert result.category == fact.category.name

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


class TestICALWriter(object):
    """Make sure the iCal writer works as expected."""
    def test_init(self, ical_writer):
        """Make sure that init creates a new calendar instance to add events to."""
        assert ical_writer.calendar

    def test__fact_to_tuple(self, ical_writer, fact):
        """Make sure that our general expection about conversions are matched."""
        result = ical_writer._fact_to_tuple(fact)
        assert result.start == fact.start
        assert result.end == fact.end
        assert result.activity == text_type(fact.activity.name)
        assert result.duration is None
        assert result.category == text_type(fact.category.name)
        assert result.description == text_type(fact.description)

    def test__fact_to_tuple_no_category(self, ical_writer, fact):
        """Make sure that ``None`` category values translate to ``empty strings``."""
        fact.activity.category = None
        result = ical_writer._fact_to_tuple(fact)
        assert result.category == ''

    def test__fact_to_tuple_with_category(self, ical_writer, fact):
        """Make sure that category references translate to their names."""
        result = ical_writer._fact_to_tuple(fact)
        assert result.category == fact.category.name

    def test_write_fact(self, ical_writer, fact, mocker):
        """Make sure that the fact attached to the calendar matches our expectations."""
        fact_tuple = ical_writer._fact_to_tuple(fact)
        ical_writer.calendar.add_component = mocker.MagicMock()
        ical_writer._write_fact(fact_tuple)
        result = ical_writer.calendar.add_component.call_args[0][0]
        assert result.get('dtstart').dt == fact_tuple.start
        assert result.get('dtend').dt == fact_tuple.end + datetime.timedelta(seconds=1)
        assert result.get('summary') == fact_tuple.activity
        assert result.get('categories') == fact_tuple.category
        assert result.get('description') == fact_tuple.description

    def test__close(self, ical_writer, fact, path):
        """Make sure the calendar is actually written do disk before file is closed."""
        ical_writer.write_report((fact,))
        with open(path, 'rb') as fobj:
            result = Calendar.from_ical(fobj.read())
            assert result.walk()


class TestXMLWriter(object):
    """Make sure the XML writer works as expected."""

    def test_init_(self, xml_writer):
        """Make sure a XML main document and a facts list child element is set up."""
        assert xml_writer.document
        assert xml_writer.fact_list

    def test_fact_to_tuple(self, xml_writer, fact):
        """Make sure type conversion and normalization matches our expectations."""
        result = xml_writer._fact_to_tuple(fact)
        assert result.start == fact.start.strftime(xml_writer.datetime_format)
        assert result.end == fact.end.strftime(xml_writer.datetime_format)
        assert result.activity == text_type(fact.activity.name)
        assert result.duration == text_type(fact.get_string_delta(format='%M'))
        assert result.category == text_type(fact.category.name)
        assert result.description == text_type(fact.description)

    def test__fact_to_tuple_no_category(self, xml_writer, fact):
        """Make sure that ``None`` category values translate to ``empty strings``."""
        fact.activity.category = None
        result = xml_writer._fact_to_tuple(fact)
        assert result.category == ''

    def test_write_fact(self, xml_writer, fact, mocker):
        """Make sure that the attributes attached to the fact matche our expectations."""
        fact_tuple = xml_writer._fact_to_tuple(fact)
        xml_writer.fact_list.appendChild = mocker.MagicMock()
        xml_writer._write_fact(fact_tuple)
        result = xml_writer.fact_list.appendChild.call_args[0][0]
        assert result.getAttribute('start') == fact_tuple.start
        assert result.getAttribute('end') == fact_tuple.end
        assert result.getAttribute('duration') == fact_tuple.duration
        assert result.getAttribute('activity') == fact_tuple.activity
        assert result.getAttribute('category') == fact_tuple.category
        assert result.getAttribute('description') == fact_tuple.description

    def test__close(self, xml_writer, fact, path):
        """Make sure the calendar is actually written do disk before file is closed."""
        xml_writer.write_report((fact,))
        with open(path, 'rb') as fobj:
            result = xml.dom.minidom.parse(fobj)
            assert result.toxml()
