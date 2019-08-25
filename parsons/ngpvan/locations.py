

class Locations(object):
    """Class for '/locations' end points."""

    def __init__(self, van_connection):

        self.connection = van_connection

    def get_locations(self, name=None):
        """
        Get locations and optionally filter by name

        `Args:`
            name: str
                Filters to Locations with names that contain the given input
        `Returns:`
            Parsons Table
                See :ref:`parsons-table` for output options.
         """

        url = self.connection.uri + 'locations'

        if name:
            name = {'name': name}

        return self._unpack_loc(self.connection.request_paginate(url, args=name))

    def get_location(self, location_id):
        """
        Get a location object

        `Args:`
            location_id: int
                A valid location id
        `Returns:`
            Parsons Table
                See :ref:`parsons-table` for output options.
        """

        url = self.connection.uri + 'locations/{}'.format(location_id)

        return self._unpack_loc(self.connection.request(url))

    def create_location(self, name, address_line1=None, address_line2=None, city=None,
                        state=None, zipcode=None):
        """
        Find or Create a location. If location already exists, will return location id.

        `Args:`
            name: str
                A name for this Location, no longer than 50 characters
            address_line1: str
                Optional; First line of a Street Address
            address_line2: str
                Optional; Second line of a Street Address
            city: str
                Optional; City or Town
            state: str
                Optional; Two or three character State or Province code (e.g., MN, ON, NSW, etc.)
            zipcode: str
                Optional; ZIP, ZIP+4, Postal Code, Post code, etc.
            `Returns:`
                A location id
        """

        url = self.connection.uri + 'locations/findOrCreate'

        location = {'name': name,
                    'address': {
                        'addressLine1': address_line1,
                        'addressLine2': address_line2,
                        'city': city,
                        'stateOrProvince': state,
                        'zipOrPostalCode': zipcode
                    }}

        return self.connection.request(url, req_type='POST', post_data=location, raw=True)

    def delete_location(self, location_id):
        """
        Delete a location object

        `Args:`
            location_id:
                A valid location id
        `Returns:`
            ``200: OK`` if successful and ``404 Not Found`` if location not found
        """

        url = self.connection.uri + 'locations/{}'.format(location_id)

        return self.connection.request(url, req_type='DELETE', raw=True)

    def _unpack_loc(self, table):
        # Internal method to unpack location json

        if isinstance(table, tuple):
            return table

        if 'address' in table.columns:
            table.unpack_dict('address', prepend=False)

        if 'geoLocation' in table.columns:
            table.unpack_dict('geoLocation', prepend=False)

        return table
