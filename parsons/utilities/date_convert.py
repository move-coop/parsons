import dateutil.parser as dp


def iso_to_unix(iso_date):
    # Convert an ISO date to a Unix time

    if iso_date:
        parsed_date = dp.parse(iso_date)
        return int(parsed_date.strftime('%s'))
    else:
        return None
