import json
import logging

from parsons.utilities import check_env
from parsons.utilities.api_connector import APIConnector

logger = logging.getLogger(__name__)

URI = "https://app.periscopedata.com/api/v1/"


class Sisense:
    """
    Instantiate the Sisense class.

    Args:
        site_name (str, optional): The name of the site. Not required if the ``SISENSE_SITE_NAME`` environmental
            variable is set. Defaults to None.
        api_key (str, optional): The Sisense API Key. Not required if the ``SISENSE_API_KEY`` environmental variable
            is set. Defaults to None.

    Returns:
        Sisense class

    """

    def __init__(self, site_name=None, api_key=None):
        self.site_name = check_env.check("SISENSE_SITE_NAME", site_name)
        self.api_key = check_env.check("SISENSE_API_KEY", api_key)
        self.uri = URI
        self.api = self._api()

    def _api(self):
        headers = {"HTTP-X-PARTNER-AUTH": self.site_name + ":" + self.api_key}
        return APIConnector(uri=self.uri, headers=headers)

    def publish_shared_dashboard(self, dashboard_id, chart_id=None, **kwargs):
        """
        Publish a dashboard or chart using the provided arguments.

        For available options, see the `API documentation
        <https://dtdocs.sisense.com/article/embed-api-options>`_.

        Args:
            dashboard_id (str | int): The ID of the dashboard (required).
            chart_id (str | int, optional): The ID of the chart. Only required for publishing individual charts.
                Defaults to None.
            **kwargs: Optional arguments.

        Returns:
            Response (dict containing the URL)

        """
        payload = {"dashboard": dashboard_id, "chart": chart_id, **kwargs}
        return self.api.post_request("shared_dashboard/create", data=json.dumps(payload))

    def list_shared_dashboards(self, dashboard_id):
        """
        List all shares of a given dashboard.

        Args:
            dashboard_id (str | int): The ID the dashboard (required).

        Returns:
            Response or an error

        """
        payload = {"dashboard": dashboard_id}
        return self.api.post_request("shared_dashboard/list", data=json.dumps(payload))

    def delete_shared_dashboard(self, token):
        """
        To delete a shared dashboard you must provide the token for the shared dashboard.

        The token is the last part of the shared dashboard URL. i.e. if the shared URL is:

        https://app.periscopedata.com/shared/9dda9dda-9dda-9dda-9dda-9dda9dda9dda

        The token is '9dda9dda-9dda-9dda-9dda-9dda9dda9dda'.

        Args:
            token (str | int): The token of the shared dashboard (required).

        Returns:
            Response or an error

        """
        payload = {"token": token}
        return self.api.post_request("shared_dashboard/delete", data=json.dumps(payload))
