import datetime
import pytest
from hamsterlib import helpers



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
def test_parse_time_info(controler, time_info, expectation):
    assert helpers.parse_time_info(time_info) == expectation

