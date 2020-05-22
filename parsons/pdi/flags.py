from dateutil.parser import parse


class Flags:
    """A class to access the Flags PDI API endpoint."""

    def __init__(self):
        flags_endpoint = "/flags"
        self.url_flags = self.base_url + flags_endpoint

        super().__init__()

    def get_flags(self, start_date, end_date, limit=None):
        """Get a list of flags.

        `Args:`
            start_date: str
                A start date formatted like yyyy-MM-dd.
            end_date: str
                An end date formatted like yyyy-MM-dd.
            limit: int
                Specify limit to return.

        `Returns:`
            parsons.Table
                A Parsons table of all the data.
        """
        try:
            start_date = parse(start_date).date().isoformat()
            end_date = parse(end_date).date().isoformat()
        except ValueError:
            raise ValueError("Invalid date format.")

        params = {
            "startDate": start_date,
            "endDate": end_date,
        }

        return self._request(self.url_flags, args=params, limit=limit)
