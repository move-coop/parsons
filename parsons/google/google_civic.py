import requests

from parsons import Table
from parsons.utilities import check_env

URI = "https://www.googleapis.com/civicinfo/v2/"


class GoogleCivic:
    """
    Args:
        api_key:
            A valid Google api key.
            Not required if ``GOOGLE_CIVIC_API_KEY`` env variable set.

    """

    def __init__(self, api_key: str | None = None):
        self.api_key = check_env.check("GOOGLE_CIVIC_API_KEY", api_key)
        self.uri = URI

    def request(self, url: str, args: dict[str, str] | None = None):
        # Internal request method

        if not args:
            args = {}

        if self.api_key:
            args["key"] = self.api_key

        r = requests.get(url, params=args)

        return r.json()

    def get_elections(self) -> Table:
        """Get a collection of information about elections and voter information."""
        url = self.uri + "elections"

        return Table((self.request(url))["elections"])

    def _get_voter_info(self, election_id: int, address: str):
        # Internal method to call voter info end point.
        # Portions of this are parsed for other methods.

        url = self.uri + "voterinfo"

        args = {"address": address, "electionId": election_id}

        return self.request(url, args=args)

    def get_polling_location(self, election_id: int, address: str):
        """
        Get polling location information for a given address.

        Args:
            election_id:
                A valid election id.
                Election ids can be found by running :meth:`.get_elections`.
            address: A valid US address in a single string.

        """
        r = self._get_voter_info(election_id, address)

        return r["pollingLocations"]

    def get_polling_locations(
        self, election_id: int, table: Table, address_field: str = "address"
    ) -> Table:
        """
        Get polling location information for a table of addresses.

        Args:
            election_id:
                A valid election id.
                Election ids can be found by running :meth:`.get_elections`.
            table: A :ref:`Table` containing valid US address in single strings.
            address_field: The name of the column where the address is stored.

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
        self,
        address: str,
        include_offices: bool = True,
        levels: list[str] | None = None,
        roles: list[str] | None = None,
    ):
        """
        Get representative information for a given address.

        This method returns the raw JSON response from the Google Civic API.
        It is a complex response that is not easily parsed into a table.
        Here is the information on how to parse the response:
        `<https://developers.google.com/resources/api-libraries/documentation/civicinfo/v2/python/latest/civicinfo_v2.representatives.html#representativeInfoByAddress>`__

        Args:
            address: A valid US address in a single string.
            include_offices:
                Whether to return information about offices and officials.
                If false, only the top-level district information will be returned. (Default: True)
            levels:
                A list of office levels to filter by.
                Only offices that serve at least one of these levels will be returned.
                Divisions that don't contain a matching office will not be returned.
                Acceptable values are:

                - "administrativeArea1"
                - "administrativeArea2"
                - "country"
                - "international"
                - "locality"
                - "regional"
                - "special"
                - "subLocality1"
                - "subLocality2"

            roles:
                A list of office roles to filter by.
                Only offices fulfilling one of these roles will be returned.
                Divisions that don't contain a matching office will not be returned.
                Acceptable values are:

                - "deputyHeadOfGovernment"
                - "executiveCouncil"
                - "governmentOfficer"
                - "headOfGovernment"
                - "headOfState"
                - "highestCourtJudge"
                - "judge"
                - "legislatorLowerBody"
                - "legislatorUpperBody"
                - "schoolBoard"
                - "specialPurposeOfficer"

        Raises:
            ValueError: If levels or roles is not a list of strings.
            ValueError: If address is not a string.
            ValueError: If the response contains "error".

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
