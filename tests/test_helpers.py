import datetime
import pytest
from hamsterlib import helpers
from freezegun import freeze_time


class TestGetDayEnd(object):
    @pytest.mark.parametrize(('day_start', 'expectation'), [
        (datetime.time(0, 0, 0), datetime.time(23, 59, 59)),
        (datetime.time(5, 30, 0), datetime.time(5, 29, 59)),
        (datetime.time(23, 59, 59), datetime.time(23, 59, 58)),
        (datetime.time(14, 44, 23), datetime.time(14, 44, 22)),
    ])
    def test_various_day_start_times(self, base_config, day_start, expectation):
        """Ensure that resulting end times match our expectation given ``day_start``-"""
        base_config['day_start'] = day_start
        assert helpers.get_day_end(base_config) == expectation


class TestEndDayToDatetime(object):
    @pytest.mark.parametrize(('day_start', 'expectation'), [
        (datetime.time(0, 0, 0), datetime.datetime(2015, 4, 15, 23, 59, 59)),
        (datetime.time(5, 30, 0), datetime.datetime(2015, 4, 16, 5, 29, 59)),
        (datetime.time(23, 59, 59), datetime.datetime(2015, 4, 16, 23, 59, 58)),
        (datetime.time(14, 44, 23), datetime.datetime(2015, 4, 16, 14, 44, 22)),
    ])
    def test_various_end_days(self, base_config, day_start, expectation):
        """Ensure that resulting ``end datetimes`` match our expectation given ``day_end``"""
        base_config['day_start'] = day_start
        end_day = datetime.datetime(2015, 4, 15)
        assert helpers.end_day_to_datetime(end_day, base_config) == expectation


class TestParseTimeRange(object):
    @pytest.mark.parametrize(('time_info', 'expectation'), [
        ('-30',
         helpers.TimeFrame(None, None, None, None, datetime.timedelta(minutes=30))),
        ('2014-01-05 18:15 - 2014-04-01 05:19',
         helpers.TimeFrame(datetime.date(2014, 1, 5), datetime.time(18, 15),
            datetime.date(2014, 4, 1), datetime.time(5, 19), None)),
        ('2014-01-05 - 2014-04-01 05:19',
         helpers.TimeFrame(datetime.date(2014, 1, 5), None,
            datetime.date(2014, 4, 1), datetime.time(5, 19), None)),
        ('2014-01-05 - 2014-04-01',
         helpers.TimeFrame(datetime.date(2014, 1, 5), None,
            datetime.date(2014, 4, 1), None, None)),
        # We can ommit whitespace between two absolute dates.
        ('2014-01-05-2014-04-01',
         helpers.TimeFrame(datetime.date(2014, 1, 5), None,
            datetime.date(2014, 4, 1), None, None)),
        # More than one whitespace afer '-' however will prevent parsing of the rest.
        ('2014-01-05 -     2014-04-01',
         helpers.TimeFrame(datetime.date(2014, 1, 5), None,
            None, None, None)),
        ('2014-04-01', helpers.TimeFrame(datetime.date(2014, 4, 1), None, None, None, None)),
        ('18:43', helpers.TimeFrame(None, datetime.time(18, 43), None, None, None)),
        # We can not ommit the start and just specify the end.
        (' - 2014-04-01', helpers.TimeFrame(None, None, None, None, None)),
    ])
    def test_various_time_infos(self, time_info, expectation):
        """Make sure that our parser works according to our expectations."""
        assert helpers.parse_time_range(time_info) == expectation

    def test_with_relative_and_absolute_time_info(self):
        """If a relative time offset is given as well as an absolute timespan, expect an error!"""
        with pytest.raises(ValueError):
            helpers.parse_time_range('-30 2014-01-05 18:15 - 2014-04-01 05:19')


class TestCompleteTimeFrame(object):
    @pytest.mark.parametrize(('timeframe', 'expectation'), [
        (
            helpers.TimeFrame(
                start_date=None,
                start_time=None,
                end_date=None,
                end_time=None,
                offset=datetime.timedelta(minutes=90)
            ),
            (
                datetime.datetime(2015, 12, 10, 11, 0, 0),
                datetime.datetime(2015, 12, 11, 5, 29, 59)
            ),
        ),
        (
            helpers.TimeFrame(
                start_date=None,
                start_time=None,
                end_date=None,
                end_time=None,
                offset=None
            ),
            (
                datetime.datetime(2015, 12, 10, 5, 30, 0),
                datetime.datetime(2015, 12, 11, 5, 29, 59)
            ),
        ),
        (
            helpers.TimeFrame(
                start_date=datetime.date(2015, 12, 1),
                start_time=None,
                end_date=datetime.date(2015, 12, 4),
                end_time=None,
                offset=None
            ),
            (
                datetime.datetime(2015, 12, 1, 5, 30, 0),
                datetime.datetime(2015, 12, 5, 5, 29, 59)
            ),
        ),
        (
            helpers.TimeFrame(
                start_date=datetime.date(2015, 12, 1),
                start_time=None,
                end_date=None,
                end_time=datetime.time(17, 0, 0),
                offset=None
            ),
            (
                datetime.datetime(2015, 12, 1, 5, 30, 0),
                datetime.datetime(2015, 12, 1, 17, 0, 0)
            ),
        ),
        (
            helpers.TimeFrame(
                start_date=datetime.date(2015, 12, 1),
                start_time=None,
                end_date=None,
                end_time=datetime.time(2, 0, 0),
                offset=None
            ),
            (
                datetime.datetime(2015, 12, 1, 5, 30, 0),
                datetime.datetime(2015, 12, 2, 2, 0, 0)
            ),
        ),
    ])
    @freeze_time('2015-12-10 12:30')
    def test_complete_timeframe_valid(self, base_config, timeframe, expectation):
        """Test that completing an partial timeframe results in expected results.""",
        assert helpers.complete_timeframe(timeframe, base_config) == expectation

    @pytest.mark.parametrize(('end_day', 'day_start', 'expectation'), [
        (datetime.date(2015, 4, 5),
        datetime.time(0, 0, 0),
        datetime.datetime(2015, 4, 5, 23, 59, 59)),
        (datetime.date(2015, 4, 5),
        datetime.time(4, 30, 0),
        datetime.datetime(2015, 4, 6, 4, 29, 59)),
        (datetime.date(2015, 4, 5),
        datetime.time(18, 0, 0),
        datetime.datetime(2015, 4, 6, 17, 59, 59)),
    ])
    def test_end_day_to_daytime(self, base_config, end_day, day_start, expectation):
        """Make sure that end_day conversion matches our expectation."""
        config = base_config
        config['day_start'] = day_start
        assert helpers.end_day_to_datetime(end_day, config) == expectation
