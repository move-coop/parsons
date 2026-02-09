"""NGPVAN Locations Endpoints"""

import logging

from parsons import Table

logger = logging.getLogger(__name__)


class Locations:
    def __init__(self, van_connection):
        self.connection = van_connection

    def get_locations(self, name: str = None) -> Table:
        """
        Get locations.

        Args:
            name (str, optional): Filter locations by name. Defaults to None.

        Returns:
            Table: See :ref:`parsons-table` for output options.

        """
        tbl = Table(self.connection.get_request("locations", params={"name": name}))
        logger.info(f"Found {tbl.num_rows} locations.")
        return self._unpack_loc(tbl)

    def get_location(self, location_id: int) -> dict:
        """
        Get a location.

        Args:
            location_id (int): The location id.

        Returns:
            dict

        """
        r = self.connection.get_request(f"locations/{location_id}")
        logger.info(f"Found location {location_id}.")
        return r

    def create_location(
        self,
        name: str,
        address_line1: str = None,
        address_line2: str = None,
        city: str = None,
        state: str = None,
        zip_code: str = None,
    ) -> int:
        """
        Find or create a location.

        If location already exists, will return location id.

        Args:
            name (str): A name for this location, no longer than 50 characters.
            address_line1 (str, optional): First line of a street address. Defaults to None.
            address_line2 (str, optional): Second line of a street address. Defaults to None.
            city (str, optional): City or town name. Defaults to None.
            state (str, optional): Two or three character state or province code (e.g., MN, ON, NSW, etc.).
                Defaults to None.
            zip_code (str, optional): ZIP, ZIP+4, Postal Code, Post code, etc. Defaults to None.

        Returns:
            int: A location id.

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

    def delete_location(self, location_id: int):
        """
        Delete a location.

        Args:
            location_id (int): The location id.

        """
        r = self.connection.delete_request(f"locations/{location_id}")
        logger.info(f"Location {location_id} deleted.")
        return r

    def _unpack_loc(self, table: Table | tuple):
        # Internal method to unpack location json

        if isinstance(table, tuple):
            return table

        if "address" in table.columns:
            table.unpack_dict("address", prepend=False)

        if "geoLocation" in table.columns:
            table.unpack_dict("geoLocation", prepend=False)

        return table
