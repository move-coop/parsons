"""NGPVAN Locations Endpoints"""

from parsons.etl.table import Table
import logging

logger = logging.getLogger(__name__)


class Locations(object):
    def __init__(self, van_connection):

        self.connection = van_connection

    def get_locations(self, name=None):
        """
        Get locations.

        `Args:`
            name: str
                Filter locations by name.
        `Returns:`
            Parsons Table
                See :ref:`parsons-table` for output options.
        """

        tbl = Table(self.connection.get_request("locations", params={"name": name}))
        logger.info(f"Found {tbl.num_rows} locations.")
        return self._unpack_loc(tbl)

    def get_location(self, location_id):
        """
        Get a location.

        `Args:`
            location_id: int
                The location id.
        `Returns:`
            dict
        """

        r = self.connection.get_request(f"locations/{location_id}")
        logger.info(f"Found location {location_id}.")
        return r

    def create_location(
        self,
        name,
        address_line1=None,
        address_line2=None,
        city=None,
        state=None,
        zip_code=None,
    ):
        """
        Find or create a location. If location already exists, will return location id.

        `Args:`
            name: str
                A name for this location, no longer than 50 characters.
            address_line1: str
                First line of a street address.
            address_line2: str
                Second line of a street address.
            city: str
                City or town name.
            state: str
                Two or three character state or province code (e.g., MN, ON, NSW, etc.).
            zip_code: str
                ZIP, ZIP+4, Postal Code, Post code, etc.
            `Returns:`
                int
                    A location id.
        """

        location = {
            "name": name,
            "address": {
                "addressLine1": address_line1,
                "addressLine2": address_line2,
                "city": city,
                "stateOrProvince": state,
                "zipOrPostalCode": zip_code,
            },
        }

        r = self.connection.post_request("locations/findOrCreate", json=location)
        logger.info(f"Location {r} created.")
        return r

    def delete_location(self, location_id):
        """
        Delete a location.

        `Args:`
            location_id: int
                The location id
        `Returns:`
            ``None``
        """

        r = self.connection.delete_request(f"locations/{location_id}")
        logger.info(f"Location {location_id} deleted.")
        return r

    def _unpack_loc(self, table):
        # Internal method to unpack location json

        if isinstance(table, tuple):
            return table

        if "address" in table.columns:
            table.unpack_dict("address", prepend=False)

        if "geoLocation" in table.columns:
            table.unpack_dict("geoLocation", prepend=False)

        return table
