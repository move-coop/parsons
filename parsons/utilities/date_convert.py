from dateutil.parser import parse
from datetime import timezone


def iso_to_unix(iso_date, tzinfo=None):
    # Convert an ISO date to a Unix time

    if iso_date:
        parsed_date = parse(iso_date)

        # if no timezone info is parsed or provided, use UTC
        if not parsed_date.tzinfo:
            if tzinfo:
                parsed_date = parsed_date.replace(tzinfo=tzinfo)
            else:
                parsed_date = parsed_date.replace(tzinfo=timezone.utc)

        return int(parsed_date.timestamp())
    else:
        return None
