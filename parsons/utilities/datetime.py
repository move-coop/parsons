from datetime import date, datetime, timezone
from typing import overload

from dateutil.parser import ParserError, parse

from parsons import logger


def _add_timezone_if_not_specified(date_time: datetime, tz: timezone) -> datetime:
    if date_time.tzinfo is None:
        logger.debug("Date '%s' has no timezone, assuming '%s'.", date_time, tz)
        return date_time.replace(tzinfo=tz)

    return date_time


@overload
def date_to_timestamp(
    value: datetime | int,
    tzinfo: timezone = ...,
) -> int: ...


@overload
def date_to_timestamp(
    value: str | datetime | int | None,
    tzinfo: timezone = ...,
) -> int | None: ...


def date_to_timestamp(
    value: int | str | datetime | None,
    tzinfo: timezone = timezone.utc,
) -> int | None:
    """
    Convert any date value into a Unix timestamp.

    Args:
        value: Date to parse.
        tzinfo:
            Timezone for the datetime, if not contained in value.
            Defaults to :attr:`datetime.timezone.utc`.

    Returns:
        Unix timestamp

    """
    if not value:
        logger.debug("Empty date, cannot parse: %s", value)
        return None

    try:
        parsed_date = parse_date(value)
    except ParserError:
        logger.warning("Failed to parse date: '%s'", value)
        return None

    parsed_date = _add_timezone_if_not_specified(parsed_date, tzinfo)

    return int(parsed_date.timestamp())


def convert_unix_to_readable(ts: int | str, tzinfo: timezone = timezone.utc) -> str:
    """
    Converts UNIX timestamps to readable timestamps.

    Args:
        value: Datetime to parse.
        tzinfo:
            Timezone for the datetime.
            Defaults to :attr:`datetime.timezone.utc`.

    Returns:
        Timestamp formatted as ``%Y-%m-%d %H:%M:%S %Z``

    """

    timestamp: datetime = datetime.fromtimestamp(int(ts) / 1000, tzinfo)

    return timestamp.strftime("%Y-%m-%d %H:%M:%S %Z")


@overload
def convert_date_to_iso(obj: None) -> None: ...


@overload
def convert_date_to_iso(obj: str | date | datetime) -> str: ...


def convert_date_to_iso(obj: str | date | datetime | None) -> str | None:
    """Ensure that dates/datetimes are provided as strings."""
    return obj.isoformat() if isinstance(obj, date) else obj


def parse_date(
    value: int | str | datetime,
    tzinfo: timezone = timezone.utc,
) -> datetime:
    """
    Parse an arbitrary date value into a :class:`datetime.datetime`.

    Args:
        value: Date to parse.
        tzinfo:
            Timezone for the datetime, if not contained in value.
            Defaults to :attr:`datetime.timezone.utc`.

    Raises:
        TypeError: If `value` is not a string, int, or datetime.

    """
    match value:
        case datetime():
            parsed_date = value
        case int():
            parsed_date = datetime.fromtimestamp(value, tzinfo)
        case str():
            parsed_date = parse(value)
        case _:
            raise TypeError(f"Expected int, str, or datetime; got {type(value).__name__}")

    return _add_timezone_if_not_specified(parsed_date, tzinfo)
