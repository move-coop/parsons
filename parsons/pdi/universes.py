class Universes:
    """A class to access the Universes PDI API endpoint."""

    def __init__(self):
        universes_endpoint = "/universes"
        self.url_universes = self.base_url + universes_endpoint

        super().__init__()

    def get_universes(self, limit=None):
        """
        Get a list of Universes.

        `Args:`
            limit: int
                The number of universes to return.
        `Returns:`
            parsons.Table
                A Parsons table of all the data.
        """

        return self._request(self.url_universes, limit=limit)
