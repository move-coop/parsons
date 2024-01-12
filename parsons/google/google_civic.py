from parsons.utilities import check_env
import requests
from parsons.etl import Table

URI = "https://www.googleapis.com/civicinfo/v2/"


class GoogleCivic(object):
    """
    `Args:`
        api_key : str
            A valid Google api key. Not required if ``GOOGLE_CIVIC_API_KEY``
            env variable set.
    `Returns:`
        class
    """

    def __init__(self, api_key=None):

        self.api_key = check_env.check("GOOGLE_CIVIC_API_KEY", api_key)
        self.uri = URI

    def request(self, url, args=None):
        # Internal request method

        if not args:
            args = {}

        args["key"] = self.api_key

        r = requests.get(url, params=args)

        return r.json()

    def get_elections(self):
        """
        Get a collection of information about elections and voter information.

        `Returns:`
            Parsons Table
                See :ref:`parsons-table` for output options.
        """

        url = self.uri + "elections"

        return Table((self.request(url))["elections"])

    def _get_voter_info(self, election_id, address):
        # Internal method to call voter info end point. Portions of this are
        # parsed for other methods.

        url = self.uri + "voterinfo"

        args = {"address": address, "electionId": election_id}

        return self.request(url, args=args)

    def get_polling_location(self, election_id, address):
        """
        Get polling location information for a given address.

        `Args:`
            election_id: int
                A valid election id. Election ids can be found by running the
                :meth:`get_elections` method.
            address: str
                A valid US address in a single string.
        `Returns:`
            Parsons Table
                See :ref:`parsons-table` for output options.
        """

        r = self._get_voter_info(election_id, address)

        return r["pollingLocations"]

    def get_polling_locations(self, election_id, table, address_field="address"):
        """
        Get polling location information for a table of addresses.

        `Args:`
            election_id: int
                A valid election id. Election ids can be found by running the
                :meth:`get_elections` method.
            address: str
                A valid US address in a single string.
            address_field: str
                The name of the column where the address is stored.
        `Returns:`
            Parsons Table
                See :ref:`parsons-table` for output options.
        """

        polling_locations = []

        # Iterate through the rows of the table
        for row in table:
            loc = self.get_polling_location(election_id, row[address_field])
            # Insert original passed address
            loc[0]["passed_address"] = row[address_field]

            # Add to list of lists
            polling_locations.append(loc[0])

        # Unpack values
        tbl = Table(polling_locations)
        tbl.unpack_dict("address", prepend_value="polling")
        tbl.unpack_list("sources", replace=True)
        tbl.unpack_dict("sources_0", prepend_value="source")
        tbl.rename_column("polling_line1", "polling_address")

        # Resort columns
        tbl.move_column("pollingHours", len(tbl.columns))
        tbl.move_column("notes", len(tbl.columns))
        tbl.move_column("polling_locationName", 1)
        tbl.move_column("polling_address", 2)

        return tbl

    def get_representative_info_by_address(
        self, address: str, include_offices=True, levels=None, roles=None
    ):
        """
        Get representative information for a given address.
        This method returns the raw JSON response from the Google Civic API.
        It is a complex response that is not easily parsed into a table.
        Here is the information on how to parse the response:
        https://developers.google.com/civic-information/docs/v2/representatives/representativeInfoByAddress

        `Args:`
            address: str
                A valid US address in a single string.
            include_offices: bool
                Whether to return information about offices and officials.
                If false, only the top-level district information will be returned. (Default: True)
            levels: list of str
                A list of office levels to filter by.
                Only offices that serve at least one of these levels will be returned.
                Divisions that don't contain a matching office will not be returned.
                    Acceptable values are:
                    "administrativeArea1"
                    "administrativeArea2"
                    "country"
                    "international"
                    "locality"
                    "regional"
                    "special"
                    "subLocality1"
                    "subLocality2"
            roles: list of str
                A list of office roles to filter by.
                Only offices fulfilling one of these roles will be returned.
                Divisions that don't contain a matching office will not be returned.
                    Acceptable values are:
                    "deputyHeadOfGovernment"
                    "executiveCouncil"
                    "governmentOfficer"
                    "headOfGovernment"
                    "headOfState"
                    "highestCourtJudge"
                    "judge"
                    "legislatorLowerBody"
                    "legislatorUpperBody"
                    "schoolBoard"
                    "specialPurposeOfficer"

        `Returns:`
            Parsons Table
                See :ref:`parsons-table` for output options.
        """

        if levels is not None and not isinstance(levels, list):
            raise ValueError("levels must be a list of strings")
        if roles is not None and not isinstance(roles, list):
            raise ValueError("roles must be a list of strings")
        if address is None or not isinstance(address, str):
            raise ValueError("address must be a string")

        url = self.uri + "representatives"

        args = {
            "address": address,
            "includeOffices": include_offices,
            "levels": levels,
            "roles": roles,
        }

        response = self.request(url, args=args)

        # Raise an error if the address was invalid
        if "error" in response:
            raise ValueError(response["error"]["message"])

        return response
