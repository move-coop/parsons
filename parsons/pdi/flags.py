from dateutil.parser import parse
from datetime import datetime


class Flags:
    """A class to access the Flags PDI API endpoint."""

    def __init__(self):
        super().__init__()
        flags_endpoint = "/flags"
        self.url_flags = self.base_url + flags_endpoint

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

    def create_flags(self, flag_list: list):
        """
        Save a list of flags, each flag must look like the dictionary below
        [
            {
                "pdiId": "string",
                "flagEntryDate": An end date formatted like yyyy-MM-dd.,
                "acquisitionTypeId": "string",
                "flagId": "string",
                "questionId": "string",
                "contactId": "string"
            }
        ]
        """
        if "pdiId" not in list(flag_list[0].keys()):
            raise ValueError("missing required key")
            return {}
        for flag in flag_list:
            try:
                flag["flagEntryDate"] = str(
                    datetime.strptime(flag["flagEntryDate"], "%Y-%m-%d").isoformat()
                )
            except ValueError:
                raise ValueError("Invalid date format.")
        print(flag_list)
        return self._request(self.url_flags, post_data=flag_list, req_type="POST")

    def delete_flag(self, id: str):
        """
        Delete a Flag by id.
        `Args:`
            id: str
                The Flag id
        """
        return self._request(f"self.url_flags/{id}", req_type="DELETE")
