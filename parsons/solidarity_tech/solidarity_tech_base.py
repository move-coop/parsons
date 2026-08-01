import logging
from collections.abc import Mapping
from datetime import datetime
from typing import cast

import numpy as np
import requests
from pyrate_limiter import Duration, Rate

from parsons.utilities import check_env
from parsons.utilities.ratelimited_api_connector import RateLimitedAPIConnector

logger = logging.getLogger(__name__)

ParamTypes = str | int | np.int64 | float | None


class SolidarityTechBase:
    def __init__(self, api_token: str | None = None) -> None:
        """
        Instantiate the SolidarityTech class.

        Args:
            api_token:
                A valid Bearer token for authorization.
                Not required if the `SOLIDARITY_TECH_TOKEN` env variable is set.

        """
        self.api_token = cast("str", check_env.check("SOLIDARITY_TECH_TOKEN", api_token))
        self.headers = {"authorization": f"Bearer {self.api_token}"}
        self.api_url = "https://api.solidarity.tech/v1/"
        self.api = RateLimitedAPIConnector(
            self.api_url, headers=self.headers, ratelimit=Rate(60, Duration.SECOND * 30)
        )

    def _get_resources(self, endpoint: str, **kwargs) -> requests.Response:
        """
        Process parameters and handle GET requests for lists of resources.

        If provided as keyword args, ``limit``, ``cursor``, ``offset``, ``since``, and ``include_count``
        will be added to params, prefaced with an underscore, and removed from kwargs.
        If the ``params`` kwarg contains pairs with a value of None, they will be removed from ``params``.

        Args:
            endpoint:
                The url request string.
                If ``url`` is a relative URL,
                it will be joined with the ``uri`` of the :class:`parsons.utilities.APIConnector`.
                If ``url`` is an absolute URL,
                it will be used as is.
            **kwargs:
                Additional parameters to pass to :meth:`parsons.utilities.APIConnector.request`.

        Returns:
            The response from the API.

        Raises:
            KeyError:
                If one of the previously-mentioned parameters is provided as
                a discrete kwarg AND via the ``params`` kwarg.

        """
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
        params: dict[str, ParamTypes] = {}
        for key, value in param_mapping.items():
            if key in kwargs:
                params[key] = value
                del kwargs[key]

        if "params" in kwargs:
            for key, value in kwargs.get("params", {}).items():
                if key in params:
                    err_msg = f"Request param '{key}' already exists."
                    raise KeyError(err_msg)
                if value is None:
                    continue
                params[key] = value

        logger.debug("Processing GET request at endpoint: %s", endpoint, extra=params)
        return self.api.request(url=endpoint, req_type="GET", params=params, **kwargs)

    def _get_single_resource(self, endpoint: str, id: int, **kwargs) -> requests.Response:
        """Handle GET requests for single resources."""
        complete_endpoint = f"{endpoint}/{id}"
        logger.debug("Processing GET request at endpoint: %s", complete_endpoint)
        return self.api.request(url=complete_endpoint, req_type="GET", **kwargs)

    def _post_request(
        self,
        endpoint: str,
        payload: Mapping[str, ParamTypes] | None = None,
        **kwargs,
    ) -> requests.Response:
        """Handle POST requests."""
        logger.debug("Processing POST request at endpoint: %s", endpoint, extra=payload)
        return self.api.request(url=endpoint, req_type="POST", json=payload, **kwargs)

    def _put_request(
        self,
        endpoint: str,
        id: int,
        payload: Mapping[str, ParamTypes] | None = None,
        **kwargs,
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
