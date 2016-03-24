from collections import namedtuple
import re
import datetime
from gettext import gettext as _


TimeFrame = namedtuple('Timeframe', ('start_date', 'start_time',
    'end_date', 'end_time', 'offset'))


def get_day_end(config):
    """Get the day end time given the day start. This assumes full 24h day."""
    day_start_datetime = datetime.datetime.combine(datetime.date.today(), config['day_start'])
    day_end_datetime = day_start_datetime - datetime.timedelta(seconds=1)
    return day_end_datetime.time()


def end_day_to_datetime(end_day, config):
    """
    Convert a given end day to its proper datetime.

    This is non trivial because of variables ``day_starts``. We want to make sure
    that even if an 'end day' is specified the actual point in time may reach into the following
    day.

    Args:
        end (datetime.date): Raw end date that is to be adjusted.
        config: Controler config containing information on when a workday starts.

    Returns:
        datetime.datetime: The endday as a adjusted datetime object.

    Example:
        Given a ``day_start`` of ``5:30`` and end date of ``2015-04-01`` we actually want to
        consider even points in time up to ``2015-04-02 5:29``. That is to represent that a
        *work day*
        does not match *calendar days*.
    """

    day_start_time = config['day_start']
    day_end_time = get_day_end(config)

    if day_start_time == datetime.time(0, 0, 0):
        end = datetime.datetime.combine(end_day, day_end_time)
    else:
        end = datetime.datetime.combine(end_day, day_end_time) + datetime.timedelta(days=1)
    return end


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
        # rest = (fragments['rest'] or '').strip()

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


def complete_timeframe(timeframe, config):
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

    def complete_end_date(date, start_date, day_start, end_time):
        if not date:
            date = start_date
        else:
            if not isinstance(date, datetime.date):
                raise TypeError(_(
                    "Expected datetime.date instance, got {type} instead.".format(
                        type=type(date))
                ))

        if day_start != datetime.time(0, 0, 0):
            # Each calendar day actually 'ends' sometime the following day.
            start_datetime = datetime.datetime.combine(
                date, datetime.datetime.now().time()
            )
            if not end_time or (end_time < day_start):
                date = start_datetime + datetime.timedelta(days=1)

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

    day_start = config['day_start']

    if not timeframe.offset:
        start = datetime.datetime.combine(
            complete_start_date(timeframe.start_date),
            complete_start_time(timeframe.start_time, day_start),
        )
    else:
        start = datetime.datetime.now() - timeframe.offset

    end = datetime.datetime.combine(
        complete_end_date(timeframe.end_date, start.date(), day_start, timeframe.end_time),
        complete_end_time(timeframe.end_time, get_day_end(config))
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
