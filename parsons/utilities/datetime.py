import datetime

from dateutil.parser import parse


def date_to_timestamp(value, tzinfo: datetime.timezone = datetime.timezone.utc) -> int | None:
    """Convert any date value into a Unix timestamp.

    Args:
        value:
            Value to parse
        tzinfo:
            Timezone for the datetime.
            Defaults to UTC.

    Returns:
        Unix timestamp (int)

    """
    parsed_date = parse_date(value)

    if not parsed_date:
        return None

    if not parsed_date.tzinfo:
        parsed_date = parsed_date.replace(tzinfo=tzinfo)

    return int(parsed_date.timestamp())


def convert_unix_to_readable(ts) -> str:
    """Converts UNIX timestamps to readable timestamps."""
    ts = datetime.datetime.fromtimestamp(int(ts) / 1000, tz=datetime.timezone.utc)

    return ts.strftime("%Y-%m-%d %H:%M:%S UTC")


def parse_date(
    value: int | str | datetime.datetime, tzinfo: datetime.timezone = datetime.timezone.utc
) -> datetime.datetime | None:
    """
    Parse an arbitrary date value into a Python datetime.

    If no value is provided (i.e., the value is None or empty),
    then the return value will be None.

    Args:
        value:
            Value to parse
        tzinfo:
            Timezone for the datetime.
            Defaults to UTC.

    Raises:
        TypeError:
            If the value is not a string, int, or datetime.

    """
    if not value:
        return None

    # If it's a number, we (probably) have a unix timestamp
    if isinstance(value, int):
        parsed = datetime.datetime.fromtimestamp(value, tzinfo)
    elif isinstance(value, datetime.datetime):
        parsed = value
    elif isinstance(value, str):
        parsed = parse(value)
    else:
        raise TypeError(
            "Unable to parse value; must be one of string or int or datetime, but got type "
            f"{type(value)}"
        )

    if not parsed.tzinfo:
        parsed = parsed.replace(tzinfo=tzinfo)

    return parsed
