class Locations:
    """A class for getting, creating, and editing PDI locations"""

    def __init__(self):
        self.locations_url = self.base_url + "/locations"

        super().__init__()

    def get_locations(self, limit=None):
        """Get a list of PDI Locations

        `Args:`
            limit: int
                The max number of locations to return

        `Returns:`
            parsons.Table
                A Parsons table containing all requested location data.
        """

        return self._request(self.locations_url, limit=limit)

    def create_location(self, address: str, name: str):
        """Create a new PDI address
        `Args:`
            address: str
               A full address including street number, city, state, and zip.
            name: str
                The name of the location. E.g. "The Overlook Hotel"
        `Returns:`
            dict
                Response from PDI in dictionary object
        """

        payload = {"locationName": name, "locationAddress": address}
        return self._request(self.locations_url, req_type="POST", post_data=payload)

    def get_location(self, id: str):
        return self._request(f"{self.locations_url}/{id}")

    def update_location(self, id: str, location_name: str, address: str):
        payload = {"locationName": location_name, "locationAddress": address}
        res = self._request(f"{self.locations_url}/{id}", req_type="PUT", post_data=payload)
        if res["code"] == 201:
            return True
