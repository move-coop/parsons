import json
import logging
from typing import Any

from parsons.utilities import check_env
from parsons.utilities.api_connector import APIConnector

logger = logging.getLogger(__name__)

URI = "https://app.periscopedata.com/api/v1/"


class Sisense:
    """
    Instantiate the Sisense class.

    Args:
        site_name:
            The name of the site.
            Not required if the ``SISENSE_SITE_NAME`` environmental variable is set.
        api_key:
            The Sisense API Key.
            Not required if the ``SISENSE_API_KEY`` environmental variable is set.

    """

    def __init__(self, site_name: str | None = None, api_key: str | None = None) -> None:
        self.site_name: str = check_env.check("SISENSE_SITE_NAME", site_name)
        self.api_key: str = check_env.check("SISENSE_API_KEY", api_key)
        self.uri = URI
        self.api = self._api()

    def _api(self) -> APIConnector:
        headers = {"HTTP-X-PARTNER-AUTH": self.site_name + ":" + self.api_key}
        return APIConnector(uri=self.uri, headers=headers)

    def publish_shared_dashboard(
        self, dashboard_id: str | int, chart_id: str | int | None = None, **kwargs
    ) -> dict[str, Any] | int | None:
        """
        This method publishes a dashboard or chart using the provided arguments.
        For available options, see the
        `API documentation <https://dtdocs.sisense.com/article/embed-api-options>`__.

        Args:
            dashboard_id: The ID of the dashboard.
            chart_id:
                The ID of the chart.
                Only required for publishing individual charts.
            `**kwargs`: Optional arguments

        Returns:
            Response (dict containing the URL) or an error

        """
        payload = {"dashboard": dashboard_id, "chart": chart_id, **kwargs}
        return self.api.post_request("shared_dashboard/create", data=json.dumps(payload))

    def list_shared_dashboards(self, dashboard_id: str | int) -> dict[str, Any] | int | None:
        """
        List all shares of a given dashboard.

        Args:
            dashboard_id: The ID the dashboard.

        Returns:
            Response or an error

        """
        payload = {"dashboard": dashboard_id}
        return self.api.post_request("shared_dashboard/list", data=json.dumps(payload))

    def delete_shared_dashboard(self, token: str | int) -> dict[str, Any] | int | None:
        """
        Delete a shared dashboard.

        To delete a shared dashboard you must provide the token for the shared dashboard.
        The token is the last part of the shared dashboard URL.
        i.e. if the shared URL is `https://app.periscopedata.com/shared/9dda9dda-9dda-9dda-9dda-9dda9dda9dda`.
        The token is `9dda9dda-9dda-9dda-9dda-9dda9dda9dda`.

        Args:
            token: The token of the shared dashboard.

        Returns:
            Response or an error

        """
        payload = {"token": token}
        return self.api.post_request("shared_dashboard/delete", data=json.dumps(payload))
