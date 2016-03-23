from collections import namedtuple
import re
import datetime
from gettext import gettext as _


TimeFrame = namedtuple('Timeframe', ('start_date', 'start_time',
    'end_date', 'end_time', 'offset'))


def parse_time_range(time_info):
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


def complete_timeframe(timeframe, day_start, day_end):
    """Apply fallback strategy to incomplete timeframes."""

    def complete_start_date(date):
        if not date:
            date = datetime.date.today()
        else:
            if not isinstance(date, datetime.date):
                raise TypeError(_(
                    "Expected datetime.date instance, got {type} instead.".format(
                        type=type(date))
                ))
        return date

    def complete_start_time(time, day_start):
        if not time:
            time = day_start
        else:
            if not isinstance(time, datetime.time):
                raise TypeError(_(
                    "Expected datetime.time instance, got {type} instead.".format(
                        type=type(time))
                ))
        return time

    def complete_end_date(date, start_date):
        if not date:
            date = start_date
        else:
            if not isinstance(date, datetime.date):
                raise TypeError(_(
                    "Expected datetime.date instance, got {type} instead.".format(
                        type=type(date))
                ))
        return date

    def complete_end_time(time, day_end):
        if not time:
            time = day_end
        else:
            if not isinstance(time, datetime.time):
                raise TypeError(_(
                    "Expected datetime.time instance, got {type} instead.".format(
                        type=type(time))
                ))
        return time

    if not timeframe.offset:
        start = datetime.datetime.combine(
            complete_start_date(timeframe.start_date),
            complete_start_time(timeframe.start_time, day_start),
        )
    else:
        start = datetime.datetime.now() - timeframe.offset

    end = datetime.datetime.combine(
        complete_end_date(timeframe.end_date, start.date()),
        complete_end_time(timeframe.end_time, day_end)
    )
    return (start, end)


def parse_time(time):
    """
    Parse a (date-)time string and return properly typed components.

    Supported formats:
        * '%Y-%m-%d'
        * '%H:%M'
        * '%Y-%m-%d %H:%M'
    """
    result = time.strip().split()
    length = len(result)
    if length == 1:
        try:
            result = datetime.datetime.strptime(time, '%H:%M')
        except ValueError:
            result = datetime.datetime.strptime(time, '%Y-%m-%d')
    elif length == 2:
        result = datetime.datetime.strptime(time, '%Y-%m-%d %H:%M')
    else:
        raise ValueError(_(
            "Sting does not seem to be in one of our supported time formats."
        ))
    return result

