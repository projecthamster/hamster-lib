def parse_time_info(self, time_info):
    """
    Generic parser for time(-range) information.

    Note:
        * We assume that timedeltas are relative to ``now``.
        * Relative times always return just ``(start, None)``.
        * It seems that the original implementation behaves rather weired
            with regards to the end-datetime fallback. When there is no
            end-date we try using the start date. If there is no start date
            we use today. However, at this point it is not quite clear
            what an enddate without an start date is supposed to mean.
            Should we rather throw an exception?

    Args:
        time_info (str): Time(-range) information. Space seperated list of
            [start-date] [start-time] [end-date] [end-time].

    Returns:
        tuple(): Tuple of (start, end) datetime objects. Each may be
            ``None``.
    """
    def get_time(time, fallback):
        """
        Convert a time string to a ``datetime.time`` instance.

        Note:
            Besides the regular builtin functionality this also handeles
            our fallback behaviour for empty strings.

        Args:
            time (str): Date in the format "hh:mm".
            fallback (datetime.time()): Fallback, if no time is specified.

        Returns:
            datetime.time(): ``time`` instance or ``None``.
        """
        result = fallback
        if time:
            result = datetime.datetime.strptime(time.strip(), "%H:%M").time()
        return result

    def get_date(date, fallback):
        """
        Convert a date string to a ``datetime.date`` instance.

        In addition to the builtin method we this also handles empty
        strings.

        Args:
            date (str): Date in the format "yyyy-mm-dd"
            fallback (datetime.date()): Fallback, if no date is specified.

        Returns:
            datetime.date(): ``date`` instance or ``None``.
        """
        result = fallback
        if date:
            result = datetime.datetime.strptime(date.strip(), "%Y-%m-%d").date()
        return result

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

    if not match:
        result = (None, None)
    else:
        fragments = match.groupdict()
        rest = (fragments['rest'] or '').strip()

        # Bail out early on relative minutes
        if fragments['relative']:
            delta = datetime.timedelta(minutes=int(fragments['relative']))
            result = (datetime.datetime.now() - delta, None)
        else:
            start, end = None, None

            start_date = fragments.get('date1', None)
            start_time = fragments.get('time1', None)

            end_date = fragments.get('date2', None)
            end_time = fragments.get('time2', None)

            if start_date or start_time:
                # Only  one of the two fallbacks should trigger at max!
                start_date = get_date(start_date, datetime.date.today())
                start = datetime.datetime.combine(
                    start_date,
                    get_time(start_time, datetime.time())
                )

            if end_date or end_time:
                # Only  one of the two fallbacks should trigger at max!
                end = datetime.datetime.combine(
                    get_date(end_date, start_date),
                    get_time(end_time, datetime.time())
                )
            result = (start, end)
    return result

