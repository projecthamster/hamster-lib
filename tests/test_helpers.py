import datetime
import pytest
from hamsterlib import helpers
from freezegun import freeze_time


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
def test_complete_timeframe_valid(base_config, timeframe, expectation):
    """Test that completing an partial timeframe results in expected results."""
    assert helpers.complete_timeframe(timeframe, base_config) == expectation
