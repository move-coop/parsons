class AcquisitionTypes:
    """A class to access the Acquisition Types PDI API endpoint."""

    def __init__(self):
        acqtypes_endpoint = "/acquisition_types"
        self.url_acqtypes = self.base_url + acqtypes_endpoint

        super().__init__()

    def get_acquisition_types(self, limit: int = None):
        """Get a list of Acquisition Types.
        `Args:`
            limit: int
                Specify limit to return.

        `Returns:`
            parsons.Table
                A Parsons table of all the data.
        """
        return self._request(self.url_acqtypes, limit=limit)

    def create_acquisition_type(
        self,
        acquisition_type: str,
        acquisition_description: str,
        acquisition_method: str,
        page_default: str = None,
    ):
        """
        Create a new Acquisition Type
        `Args:`
            acquisition_type (string): The acquisition type
            acquisition_description (string): The acquisition description
            acquisition_method (string): The acquisition method
            Options are:
                "Phone"
                "Canvass"
                "Mail"
                "IVR"
                "Text Message"
                "Email"
                "Event"
                "Online"
                "Social"
                "Site"
                "Other Method" ,
            pageDefault (string, optional): The page default.
                "Lookup" (Lookup Page)
                "WalkList" (Create Lists & Files - Walk List)
                "PhoneList" (Create Lists & Files - Phone List)
                "PhoneBank" (Online Phone Bank)
                "Canvassing" (Mobile Canvassing Device)
                "Import" (Imports)
            }
        """
        payload = {
            "acquisitionType": acquisition_type,
            "acquisitionDescription": acquisition_description,
            "acquisitionMethod": acquisition_method,
            "pageDefault": page_default,
        }
        return self._request(self.url_acqtypes, req_type="POST", post_data=payload)

    def get_acquisition_type(self, id: str):
        """
        Get a Acquisition Type by id.
        `Args:`
            id: str
                The Acquisition Type id
        `Returns:`
            parsons.Table
                A Parsons table of all the data.
        """
        return self._request(f"{self.url_acqtypes}/{id}")

    def delete_acquisition_type(self, id: str):
        """
        Delete a Acquisition Type by id.
        `Args:`
            id: str
                The Acquisition Type id
        """
        return self._request(f"{self.url_acqtypes}/{id}", req_type="DELETE")

    def update_acquisition_type(
        self,
        id: str,
        acquisition_type: str,
        acquisition_description: str,
        acquisition_method: str,
        page_default: str = None,
    ):
        """
        Update Acquisition Type
        `Args:`
            acquisition_type (string): The acquisition type
            acquisition_description (string): The acquisition description
            acquisition_method (string): The acquisition method
            Options are:
                "Phone"
                "Canvass"
                "Mail"
                "IVR"
                "Text Message"
                "Email"
                "Event"
                "Online"
                "Social"
                "Site"
                "Other Method" ,
            pageDefault (string, optional): The page default.
                "Lookup" (Lookup Page)
                "WalkList" (Create Lists & Files - Walk List)
                "PhoneList" (Create Lists & Files - Phone List)
                "PhoneBank" (Online Phone Bank)
                "Canvassing" (Mobile Canvassing Device)
                "Import" (Imports)
            }
        """
        payload = {
            "acquisitionType": acquisition_type,
            "acquisitionDescription": acquisition_description,
            "acquisitionMethod": acquisition_method,
            "pageDefault": page_default,
        }
        return self._request(f"{self.url_acqtypes}/{id}", req_type="PUT", post_data=payload)
