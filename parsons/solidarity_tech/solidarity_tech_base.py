import logging
from collections.abc import Mapping
from datetime import datetime

import requests

from parsons.solidarity_tech.ratelimited_api_connector import RateLimitedAPIConnector
from parsons.utilities import check_env

logger = logging.getLogger(__name__)


class SolidarityTechBase:
    def __init__(self, api_token: str | None = None) -> None:
        """
        Instantiate the SolidarityTech class.

        Args:
            api_token:
                A valid Bearer token for authorization.
                Not required if the `SOLIDARITY_TECH_TOKEN` env variable is set.

        """
        self.api_token: str = check_env.check("SOLIDARITY_TECH_TOKEN", api_token)
        self.headers = {"authorization": f"Bearer {self.api_token}"}
        self.api_url = "https://api.solidarity.tech/v1/"
        self.api = RateLimitedAPIConnector(self.api_url, headers=self.headers)

    def _get_resources(self, endpoint: str, limit: int, **kwargs) -> requests.Response:
        """Process parameters and handle GET requests for lists of resources."""
        since = kwargs.get("since")
        if isinstance(since, datetime):
            kwargs["since"] = int(since.timestamp())

        param_mapping = {
            "limit": "_limit",
            "cursor": "_cursor",
            "offset": "_offset",
            "since": "_since",
            "include_count": "_include_count",
        }
        params = {"_limit": limit}
        for key, value in kwargs.items():
            if value is None:
                continue
            query_key = param_mapping.get(key, key)
            params[query_key] = value
            del kwargs[key]

        logger.debug("Processing GET request at endpoint: %s", endpoint, extra=params)
        return self.api.request(url=endpoint, req_type="GET", params=params, **kwargs)

    def _get_single_resource(self, endpoint: str, id: int, **kwargs) -> requests.Response:
        """Handle GET requests for single resources."""
        complete_endpoint = f"{endpoint}/{id}"
        logger.debug("Processing GET request at endpoint: %s", complete_endpoint)
        return self.api.request(url=complete_endpoint, req_type="GET", **kwargs)

    def _post_request(
        self, endpoint: str, payload: Mapping[str, str | int] | None = None, **kwargs
    ) -> requests.Response:
        """Handle POST requests."""
        logger.debug("Processing POST request at endpoint: %s", endpoint, extra=payload)
        return self.api.request(url=endpoint, req_type="POST", json=payload, **kwargs)

    def _put_request(
        self, endpoint: str, id: int, payload: Mapping[str, str | int] | None = None, **kwargs
    ) -> requests.Response:
        """Handle PUT requests."""
        complete_endpoint = f"{endpoint}/{id}"
        logger.debug("Processing PUT request at endpoint: %s", complete_endpoint, extra=payload)
        return self.api.request(url=complete_endpoint, req_type="PUT", json=payload, **kwargs)

    def _del_request(self, endpoint: str, id: int | str, **kwargs) -> requests.Response:
        """Handle DEL requests."""
        complete_endpoint = f"{endpoint}/{id}"
        logger.debug("Processing DEL request at endpoint: %s", complete_endpoint)
        return self.api.request(url=complete_endpoint, req_type="DEL", **kwargs)
