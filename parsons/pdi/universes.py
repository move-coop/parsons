class Universes:
    """A class to access the Universes PDI API endpoint."""

    def __init__(self):
        universes_endpoint = "/universes"
        self.url_universes = self.base_url + universes_endpoint

        super().__init__()

    def get_universes(self, limit=None):
        """Get a list of Universes."""

        return self._request(self.url_universes, limit=limit)
