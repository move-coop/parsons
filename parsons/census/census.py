import logging

from parsons import Table
from parsons.utilities import check_env
from parsons.utilities.api_connector import APIConnector

logger = logging.getLogger(__name__)


class Census:
    """Class that creates a connector to the Census Bureau API."""

    def __init__(self, api_key=None):
        """
        Instantiate Census class.

        Args:
            api_key: String, key for Census API access
                (optional, can also be pulled from environment variable CENSUS_API_KEY). Defaults to None.

        """
        self.api_key = check_env.check("CENSUS_API_KEY", api_key)
        self.host = "https://api.census.gov/data"

    def get_census(self, year=None, dataset_acronym=None, variables=None, location=None):
        """
        Pull census data.

        For background check out the `Census API Guide
        <https://www.census.gov/data/developers/guidance/api-user-guide.html>`__.

        Args:
            year (str, optional): | int
                4-digit string or integer e.g. '2019' or 2019. Defaults to None.
            dataset_acronym (str, optional): Dataset name e.g. '/acs/acs1'. Defaults to None.
            variables (str, optional): Comma-separated variable names e.g. 'NAME,B01001_001E'.
                Defaults to None.
            location (str, optional): Desired locations e.g. 'us:*'. Defaults to None.

        Returns:
            Table

        """
        # set up the URL
        g = "?get="
        usr_key = f"&key={self.api_key}"
        year = str(year)  # in case someone passes int
        location = "&for=" + location
        query_url = f"{self.host}/{year}{dataset_acronym}{g}{variables}{location}{usr_key}"

        # create connector
        connector = APIConnector(uri=self.host)

        # pull data
        response = connector.get_request(url=query_url)

        # turn into Parsons table and return it
        return Table(response)
