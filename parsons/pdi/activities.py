class Activities:
    """A class to access the Activities PDI API endpoint."""

    def __init__(self):
        activites_endpoint = "/activities"
        self.url_activites = self.base_url + activites_endpoint
        super().__init__()

    def get_activities(self, limit: int = None):
        """Get a list of Activities.
        `Args:`
            limit: int
                Specify limit to return.

        `Returns:`
            parsons.Table
                A Parsons table of all the data.
        """
        return self._request(self.url_activites, limit=limit)

    def create_activity(self, activity_name: str, canvassing_shift: bool):
        """
        Create a New Activity
        `Args:`
            activity_name str: The activity name
            canvassing_shift bool: The canvassing shift
        """
        payload = {"activityName": activity_name, "canvassingShift": canvassing_shift}
        return self._request(self.url_activites, req_type="POST", post_data=payload)

    def get_activity(self, id: str):
        """
        Get a Activity by id.
        `Args:`
            id: str
                The Activity id
        `Returns:`
            parsons.Table
                A Parsons table of all the data.
        """
        return self._request(f"{self.url_activites}/{id}")

    def update_activity(self, id: str, activity_name: str, canvassing_shift: str):
        """
        Update an Activity
        `Args:`
            id: Activity id
            activity_name str: The activity name
            canvassing_shift bool: The canvassing shift
        """
        payload = {"activityName": activity_name, "canvassingShift": canvassing_shift}
        return self._request(f"{self.url_activites}/{id}", req_type="PUT", post_data=payload)
