from datetime import UTC, datetime, timezone

from dateutil.parser import parse


def date_to_timestamp(value: int | str | datetime, tzinfo: timezone = UTC) -> int | None:
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


def convert_unix_to_readable(ts: str | int) -> str:
    """Convert UNIX timestamps to readable timestamps."""
    timestamp = datetime.fromtimestamp(int(ts) / 1000, tz=UTC)

    return timestamp.strftime("%Y-%m-%d %H:%M:%S UTC")


def parse_date(value: int | str | datetime, tzinfo: timezone = UTC) -> datetime | None:
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
        parsed = datetime.fromtimestamp(value, tzinfo)
    elif isinstance(value, datetime):
        parsed = value
    elif isinstance(value, str):
        parsed = parse(value)
    else:
        err_msg = f"Unable to parse value; must be one of string or int or datetime, but got type {type(value)}"
        raise TypeError(err_msg)

    if not parsed.tzinfo:
        parsed = parsed.replace(tzinfo=tzinfo)

    return parsed
