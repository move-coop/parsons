class Locations:
    """A class for getting, creating, and editing PDI locations"""

    def __init__(self):
        self.locations_url = self.base_url + '/locations'

        super().__init__()

    def get_locations(self, limit=None):
        """Get a list of PDI Locations

        `Args:`
            limit: int
                The max number of locations to return

        `Returns:`
            parsons.Table
                A Parsons table of all the data.
        """

        return self._request(self.locations_url, limit=limit)


    def find_or_create_locations(self, addresses):
        """Find the IDs of existing PDI locations or create IDs for new locations for a table of
        addresses

        `Args:`
            addresses: parsons table
                A parsons table containing a column named 'address' and another column named 'name'
                where the 'address' column contains a full address (street number, city, state, zip)
                and the 'name' column contains the name of the location to be create if no match
                is found for the address in PDI.

        `Returns`
            parsons table
                The input table with 2 new columns: the 'id' column will contain each locations
                PDI LocationID, and the 'existed' column will contain True if PDI already contained
                a location match, or False where a new address was created.
        """
