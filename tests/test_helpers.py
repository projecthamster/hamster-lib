import datetime
import pytest
from hamsterlib import helpers
from freezegun import freeze_time



@pytest.mark.parametrize(('time_info', 'expectation'), [
    ('2015-12-10', helpers.TimeFrame(
        start_date=datetime.date(2015, 12, 10),
        start_time=None,
        end_date=None,
        end_time=None,
        offset=None
    )),
    ('2015-12-10 12:30', helpers.TimeFrame(
        start_date=datetime.date(2015, 12, 10),
        start_time=datetime.time(12, 30, 0),
        end_date=None,
        end_time=None,
        offset=None
    )),
    ('2015-12-10 12:30 - 2015-12-20', helpers.TimeFrame(
        start_date=datetime.date(2015, 12, 10),
        start_time=datetime.time(12, 30, 0),
        end_date=datetime.date(2015, 12, 20),
        end_time=None,
        offset=None
    )),
    ('2015-12-10 12:30 - 2015-12-20 16:15', helpers.TimeFrame(
        start_date=datetime.date(2015, 12, 10),
        start_time=datetime.time(12, 30, 0),
        end_date=datetime.date(2015, 12, 20),
        end_time=datetime.time(16, 15, 0),
        offset=None
    )),
    ('-85', helpers.TimeFrame(
        start_date=None,
        start_time=None,
        end_date=None,
        end_time=None,
        offset=datetime.timedelta(minutes=85)
    )),
])
def test_parse_time_info(time_info, expectation):
    assert helpers.parse_time_info(time_info) == expectation


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
            datetime.datetime(2015, 12, 11, 10, 59, 59)
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
            datetime.datetime(2015, 12, 4, 5, 29, 59)
        ),
    ),
])
@freeze_time('2015-12-10 12:30')
def test_complete_timeframe_valid(base_config, timeframe, expectation):
    assert helpers.complete_timeframe(timeframe, base_config['day_start']) == expectation

