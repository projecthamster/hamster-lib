# -*- encoding: utf-8 -*-

# Copyright (C) 2015-2016 Eric Goller <eric.goller@ninjaduck.solutions>

# This file is part of 'hamster-lib'.
#
# 'hamster-lib' is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# 'hamster-lib' is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with 'hamster-lib'.  If not, see <http://www.gnu.org/licenses/>.


"""This module provides several time realted convinience functions."""

from __future__ import absolute_import, unicode_literals

import datetime
import re
from collections import namedtuple

TimeFrame = namedtuple('Timeframe', ('start_date', 'start_time',
    'end_date', 'end_time', 'offset'))


def get_day_end(config):
    """
    Get the day end time given the day start. This assumes full 24h day.

    Args:
        config (dict): Configdict. Needed to extract ``day_start``.

    Note:
        This is merely a convinience funtion so we do not have to deduct this from ``day_start``
        by hand all the time.
    """
    day_start_datetime = datetime.datetime.combine(datetime.date.today(), config['day_start'])
    day_end_datetime = day_start_datetime - datetime.timedelta(seconds=1)
    return day_end_datetime.time()


def end_day_to_datetime(end_day, config):
    """
    Convert a given end day to its proper datetime.

    This is non trivial because of variable ``day_start``. We want to make sure
    that even if an 'end day' is specified the actual point in time may reach into the following
    day.

    Args:
        end (datetime.date): Raw end date that is to be adjusted.
        config: Controller config containing information on when a workday starts.

    Returns:
        datetime.datetime: The endday as a adjusted datetime object.

    Example:
        Given a ``day_start`` of ``5:30`` and end date of ``2015-04-01`` we actually want to
        consider even points in time up to ``2015-04-02 5:29``. That is to represent that a
        *work day*
        does not match *calendar days*.

    Note:
        An alternative implementation for the similar problem in legacy hamster:
            ``hamster.storage.db.Storage.__get_todays_facts``.
    """

    day_start_time = config['day_start']
    day_end_time = get_day_end(config)

    if day_start_time == datetime.time(0, 0, 0):
        end = datetime.datetime.combine(end_day, day_end_time)
    else:
        end = datetime.datetime.combine(end_day, day_end_time) + datetime.timedelta(days=1)
    return end


def extract_time_info(text):
    """
    Extract valid time(-range) information from a string according to our specs.

    Args:
        text (text_type): Raw string containing encoded time(-span) information.
            Date/Time-combinations are expected in a ``YYYY-MM-DD hh:mm`` format.
            Relative  times can be given with ``-minutes``.
            Please note that either *relative* or *absolute* times will be considered.
            It is possible to either just specify a start date (as time, date,
            or datetime) or a timerange (start and end). If a timerange is given
            start and end need to be delimited exactly by ' - '.

    Returns:
        tuple: ``(timeframe, rest)`` tuple. Where ``timeframe`` is a tuple that
            provides convinient access to all seperate elements extracted from
            the raw string and ``rest`` is any substring stat has not been
            matched to valid time/date info.

    Note:
        * Relative times always return just ``(None, None, None, None, timedelta)``.
    """

    # [TODO] Add a list of supported formats.

    def get_time(time):
        """Convert a times string representation to datetime.time instance."""
        if time:
            time = datetime.datetime.strptime(time.strip(), "%H:%M").time()
        return time

    def get_date(date):
        """Convert a dates string representation to datetime.date instance."""
        if date:
            date = datetime.datetime.strptime(date.strip(), "%Y-%m-%d").date()
        return date

    def date_time_from_groupdict(groupdict):
        """Return a date/time tuple by introspecting a passed dict."""
        if groupdict['datetime']:
            dt = parse_time(groupdict['datetime'])
            time = dt.time()
            date = dt.date()
        else:
            date = get_date(groupdict.get('date', None))
            time = get_time(groupdict.get('time', None))
        return (date, time)

    # Baseline/default values.
    result = {
        'start_date': None,
        'start_time': None,
        'end_date': None,
        'end_time': None,
        'offset': None
    }
    rest = None

    # Individual patterns for time/date  substrings.
    relative_pattern = '(?P<relative>-\d+)'
    time_pattern = '(?P<time>\d{2}:\d{2})'
    date_pattern = '(?P<date>\d{4}-\d{2}-\d{2})'
    datetime_pattern = '(?P<datetime>\d{4}-\d{2}-\d{2} \d{2}:\d{2})'

    start = re.match('^({}|{}|{}|{}) (?P<rest>.+)'.format(relative_pattern, datetime_pattern,
        date_pattern, time_pattern), text)
    if start:
        start_groups = start.groupdict()
        if start_groups['relative']:
            result['offset'] = datetime.timedelta(minutes=abs(int(start_groups['relative'])))
        else:
            date, time = date_time_from_groupdict(start_groups)
            result['start_date'] = date
            result['start_time'] = time
        rest = start_groups['rest']

        if rest:
            end = re.match('^- ({}|{}|{}) (?P<rest>.+)'.format(datetime_pattern, date_pattern,
                time_pattern), rest)
        else:
            end = None

        if end and not start_groups['relative']:
            end_groups = end.groupdict()
            date, time = date_time_from_groupdict(end_groups)
            result['end_date'] = date
            result['end_time'] = time
            rest = end_groups['rest']

    result = TimeFrame(result['start_date'], result['start_time'], result['end_date'],
        result['end_time'], result['offset'])

    # Consider the whole string as 'rest' if no time/date info was extracted
    if not rest:
        rest = text
    return (result, rest.strip())


def complete_timeframe(timeframe, config, partial=False):
    """
    Apply fallback strategy to incomplete timeframes.

    Our fallback strategy is as follows:
        * Missing start-date: Fallback to ``today``.
        * Missing start-time: Fallback to ``store.config['day_start']``.
        * Missing end-date: Fallback to ``today`` for ``day_start='00:00`,
          ``tomorrow`` otherwise.
          See ``hamster_lib.helpers.end_day_to_datetime`` for details and
          explanations.
        * Missing end-time: 1 second before ``store.config['day_start']``.

    Args:
        timeframe (TimeFrame): ``TimeFrame`` instance incorporating all
            available information available about the timespan. Any missing info
            will be completed per fallback strategy.
        config (dict): A config-dict providing settings relevant to determine
            fallback values.
        partial (bool, optional): If true, we will only complete start/end times if there
            is at least either date or time information present. Defaults to
            ``False``.

    Returns:
        tuple: ``(start, end)`` tuple. Where ``start`` and ``end`` are full
        ``datetime.datetime`` instances.

    Raises:
        TypeError: If any of the ``timeframe`` values is of inappropriate
            datetime type.
    """

    def complete_start_date(date):
        """
        Assign ``today`` if ``date=None``, else ensure its a ``datetime.date`` instance.

        Args:
            date (datetime.date): Startdate information.

        Returns:
            datetime.date: Either the original date or the default solution.

        Raises:
            TypeError: If ``date``` is neither ``None`` nor  ``datetime.date`` instance.

        Note:
            Reference behavior taken from [hamster-cli](https://github.com/projecthamster/
            hamster/blob/master/src/hamster-cli#L368).
        """

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
        """Assign ``day_start`` if no start-time is given."""
        if not time:
            time = day_start
        else:
            if not isinstance(time, datetime.time):
                raise TypeError(_(
                    "Expected datetime.time instance, got {type} instead.".format(
                        type=type(time))
                ))
        return time

    def complete_start(date, time, config):
        return datetime.datetime.combine(
            complete_start_date(timeframe.start_date),
            complete_start_time(timeframe.start_time, config['day_start']),
        )

    def complete_end_date(date):
        if not date:
            date = datetime.date.today()
        else:
            if not isinstance(date, datetime.date):
                raise TypeError(_(
                    "Expected datetime.date instance, got {type} instead.".format(
                        type=type(date))
                ))
        return date

    def complete_end(date, time, config):
        date = complete_end_date(date)
        if time:
            result = datetime.datetime.combine(date, time)
        else:
            result = end_day_to_datetime(date, config)
        return result

    start, end = None, None

    if any((timeframe.offset, timeframe.start_time, timeframe.start_date)) or not partial:
        if not timeframe.offset:
            start = complete_start(timeframe.start_date, timeframe.start_time, config)
        else:
            start = datetime.datetime.now() - timeframe.offset

    if any((timeframe.end_date, timeframe.end_time)) or not partial:
        end = complete_end(timeframe.end_date, timeframe.end_time, config)

    return (start, end)


def parse_time(time):
    """
    Parse a date/time string and return a corresponding datetime object.

    Args:
        time (str): A ``string` of one of the following formats: ``%H:%M``, ``%Y-%m-%d`` or
            ``%Y-%m-%d %H:%M``.

    Returns:
        datetime.datetime: Depending on input string either returns ``datetime.date``,
            ``datetime.time`` or ``datetime.datetime``.

    Raises:
        ValueError: If ``time`` can not be matched against any of the accepted formats.

    Note:
        This parse just a singlular date, time or datetime representation.
    """

    length = len(time.strip().split())
    if length == 1:
        try:
            result = datetime.datetime.strptime(time, '%H:%M').time()
        except ValueError:
            result = datetime.datetime.strptime(time, '%Y-%m-%d').date()
    elif length == 2:
        result = datetime.datetime.strptime(time, '%Y-%m-%d %H:%M')
    else:
        raise ValueError(_(
            "String does not seem to be in one of our supported time formats."
        ))
    return result


def validate_start_end_range(range_tuple):
    """
    Perform basic sanity checks on a timeframe.

    Args:
        range_tuple (tuple): ``(start, end)`` tuple as returned by
            ``complete_timeframe``.

    Raises:
        ValueError: If start > end.

    Returns:
        tuple: ``(start, end)`` tuple that passed validation.

    Note:
        ``timeframes`` may be incomplete, especially if ``complete_timeframe(partial=True)`` has
        been used to construct them.
    """

    start, end = range_tuple

    if (start and end) and (start > end):
        raise ValueError(_("Start after end!"))

    return range_tuple
