from collections import namedtuple
import re
import datetime


TimeFrame = namedtuple('Timeframe', ('start_date', 'start_time',
    'end_date', 'end_time', 'offset'))


def parse_time_info(time_info):
    """
    Generic parser for time(-range) information.

    Note:
        * We assume that timedeltas are relative to ``now``.
        * Relative times always return just ``(start, None)``.
    """
    result = TimeFrame(None, None, None, None, None)

    def get_time(time):
        if time:
            time = datetime.datetime.strptime(time.strip(), "%H:%M").time()
        return time

    def get_date(date):
        if date:
            date = datetime.datetime.strptime(date.strip(), "%Y-%m-%d").date()
        return date

    patterns = (
        '^((?P<relative>-\d.+)?|('
        '(?P<date1>\d{4}-\d{2}-\d{2})?'
        '(?P<time1> ?\d{2}:\d{2})?'
        '(?P<dash> ?-)?'
        '(?P<date2> ?\d{4}-\d{2}-\d{2})?'
        '(?P<time2> ?\d{2}:\d{2})?)?)'
        '(?P<rest>\D.+)?$'
    )
    match = re.compile(patterns).match(time_info)
    if match:
        fragments = match.groupdict()
        rest = (fragments['rest'] or '').strip()

        # Bail out early on relative minutes
        if fragments['relative']:
            result = TimeFrame(None, None, None, None,
                datetime.timedelta(minutes=abs(int(fragments['relative']))))
        else:
            result = TimeFrame(
                start_date=get_date(fragments.get('date1', None)),
                start_time=get_time(fragments.get('time1', None)),
                end_date=get_date(fragments.get('date2', None)),
                end_time=get_time(fragments.get('time2', None)),
                offset=None
            )
    return result

