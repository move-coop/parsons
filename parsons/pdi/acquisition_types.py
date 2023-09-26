class AcquisitionTypes:
    """A class to access the Acquisition Types PDI API endpoint."""

    def __init__(self):
        acqtypes_endpoint = "/acquisition_types"
        self.url_acqtypes = self.base_url + acqtypes_endpoint

        super().__init__()

    def get_acquisition_types(self, limit=None):
        """Get a list of Acquisition Types.

        `Args:`
            limit: int
                Specify limit to return.

        `Returns:`
            parsons.Table
                A Parsons table of all the data.
        """

        return self._request(self.url_acqtypes, limit=limit)
