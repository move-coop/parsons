from typing import Literal


class AcquisitionTypes:
    """A class to access the Acquisition Types PDI API endpoint."""

    def __init__(self):
        acqtypes_endpoint = "/acquisition_types"
        self.url_acqtypes = self.base_url + acqtypes_endpoint

        super().__init__()

    def get_acquisition_types(self, limit: int = None):
        """
        Get a list of Acquisition Types.

        Args:
            limit (int, optional): Specify limit to return. Defaults to None.

        Returns:
            parsons.Table: A Parsons table of all the data.

        """
        return self._request(self.url_acqtypes, limit=limit)

    def create_acquisition_type(
        self,
        acquisition_type: str,
        acquisition_description: str,
        acquisition_method: Literal[
            "Phone",
            "Canvass",
            "Mail",
            "IVR",
            "Text Message",
            "Email",
            "Event",
            "Online",
            "Social",
            "Site",
            "Other Method",
        ],
        page_default: Literal[
            "Lookup", "WalkList", "PhoneList", "PhoneBank", "Canvassing", "Import"
        ]
        | None = None,
    ):
        """
        Create a new Acquisition Type.

        Args:
            acquisition_type (str)
            acquisition_description (str)
            acquisition_method (Literal["Phone", "Canvass", "Mail", "IVR", "Text Message", "Email", "Event",
                "Online", "Social", "Site", "Other Method", ]): "Online", "Social", "Site", "Other Method"]):
            page_default (Literal["Lookup", "WalkList", "PhoneList", "PhoneBank", "Canvassing", "Import"] | None,
                optional): Defaults to None.

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

        Args:
            id (str): The Acquisition Type id.

        Returns:
            parsons.Table: A Parsons table of all the data.

        """
        return self._request(f"{self.url_acqtypes}/{id}")

    def delete_acquisition_type(self, id: str):
        """
        Delete a Acquisition Type by id.

        Args:
            id (str): The Acquisition Type id.

        """
        return self._request(f"{self.url_acqtypes}/{id}", req_type="DELETE")

    def update_acquisition_type(
        self,
        id: str,
        acquisition_type: str,
        acquisition_description: str,
        acquisition_method: Literal[
            "Phone",
            "Canvass",
            "Mail",
            "IVR",
            "Text Message",
            "Email",
            "Event",
            "Online",
            "Social",
            "Site",
            "Other Method",
        ],
        page_default: Literal[
            "Lookup", "WalkList", "PhoneList", "PhoneBank", "Canvassing", "Import"
        ]
        | None = None,
    ):
        """
        Update Acquisition Type.

        Args:
            id (str)
            acquisition_type (str)
            acquisition_description (str)
            acquisition_method (Literal["Phone", "Canvass", "Mail", "IVR", "Text Message", "Email", "Event",
                "Online", "Social", "Site", "Other Method", ]): "Online", "Social", "Site", "Other Method"]):
                Options are:

                - "Phone"
                - "Canvass"
                - "Mail"
                - "IVR"
                - "Text Message"
                - "Email"
                - "Event"
                - "Online"
                - "Social"
                - "Site"
                - "Other Method".

            page_default (Literal["Lookup", "WalkList", "PhoneList", "PhoneBank", "Canvassing", "Import"] | None,
                optional): Defaults to None.

                - "Lookup" (Lookup Page)
                - "WalkList" (Create Lists & Files - Walk List)
                - "PhoneList" (Create Lists & Files - Phone List)
                - "PhoneBank" (Online Phone Bank)
                - "Canvassing" (Mobile Canvassing Device)
                - "Import" (Imports)

        """
        payload = {
            "acquisitionType": acquisition_type,
            "acquisitionDescription": acquisition_description,
            "acquisitionMethod": acquisition_method,
            "pageDefault": page_default,
        }
        return self._request(f"{self.url_acqtypes}/{id}", req_type="PUT", post_data=payload)
