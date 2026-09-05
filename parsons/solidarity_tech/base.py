"""Connector-wide classes for Parsons Solidarity Tech API."""

from __future__ import annotations

import logging
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Any, TypedDict

import pyrate_limiter
import requests_ratelimiter

from parsons.solidarity_tech.auth import SolidarityTechAuth
from parsons.solidarity_tech.exceptions import (
    STFailedAuthenticationError,
    STFailedResponseError,
    STUnexpectedResponseError,
)
from parsons.utilities import check_env
from parsons.utilities.api_connector import APIConnector, _JsonType

if TYPE_CHECKING:
    from collections.abc import Mapping

    import requests

logger = logging.getLogger(__name__)


class Metadata(TypedDict):
    """Standard metadata dictionary returned by the SolidarityTech API."""

    total_count: int
    limit: int
    offset: int


class SolidarityTechBase:
    """Base class for interacting with the SolidarityTech API."""

    def __init__(
        self, api_token: str | None = None, *, session: requests.Session | None = None
    ) -> None:
        """
        Instantiate the SolidarityTech class.

        Args:
            api_token:
                A valid Bearer token for authorization.
                Not required if the `SOLIDARITY_TECH_BEARER_KEY` env variable is set.
            session:
                A custom :class:`requests.Session` instance for advanced configuration.
                Providing your own :class:`~requests.Session` will bypass
                built-in rate limiting, so you will need to provide your own solution.

        """
        api_token = str(check_env.check("SOLIDARITY_TECH_BEARER_KEY", api_token)).strip()
        self.api_url = "https://api.solidarity.tech/v1/"
        self.api = APIConnector(
            uri=self.api_url,
            auth=SolidarityTechAuth(api_token),
            ratelimiter=requests_ratelimiter.Limiter(
                requests_ratelimiter.HostBucketFactory(
                    rates=[pyrate_limiter.Rate(60, pyrate_limiter.Duration.SECOND * 30)]
                )
            )
            if not session
            else None,
            session=session,
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

        Raises:
            KeyError:
                If one of the previously-mentioned parameters is provided as
                a discrete kwarg AND via the ``params`` kwarg.

        Returns:
            The response from the API.

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
        params: dict[str, _JsonType] = {}
        for key, value in param_mapping.items():
            if key in kwargs:
                params[value] = kwargs[key]
                del kwargs[key]

        if "params" in kwargs:
            for key, value in kwargs.get("params", {}).items():
                if key in params:
                    err_msg = f"Request param '{key}' already exists."
                    raise KeyError(err_msg)
                if value is None:
                    continue
                params[key] = value

        if params:
            kwargs["params"] = params

        logger.debug("Processing GET request at endpoint: %s", endpoint, extra=params)
        return self.api.request(url=endpoint, req_type="GET", raise_on_error=False, **kwargs)

    def _get_single_resource(self, endpoint: str, resource_id: int, **kwargs) -> requests.Response:
        """Handle GET requests for single resources."""
        complete_endpoint = f"{endpoint}/{resource_id}"

        logger.debug("Processing GET request at endpoint: %s", complete_endpoint)
        return self.api.request(
            url=complete_endpoint, req_type="GET", raise_on_error=False, **kwargs
        )

    def _post_request(
        self,
        endpoint: str,
        payload: Mapping[str, _JsonType] | None = None,
        **kwargs,
    ) -> requests.Response:
        """Handle POST requests."""
        logger.debug("Processing POST request at endpoint: %s", endpoint, extra=payload)
        return self.api.request(
            url=endpoint, req_type="POST", json=payload, raise_on_error=False, **kwargs
        )

    def _put_request(
        self,
        endpoint: str,
        resource_id: int,
        payload: Mapping[str, _JsonType] | None = None,
        **kwargs,
    ) -> requests.Response:
        """Handle PUT requests."""
        complete_endpoint = f"{endpoint}/{resource_id}"
        logger.debug("Processing PUT request at endpoint: %s", complete_endpoint, extra=payload)
        return self.api.request(
            url=complete_endpoint, req_type="PUT", json=payload, raise_on_error=False, **kwargs
        )

    def _del_request(self, endpoint: str, resource_id: int | str, **kwargs) -> requests.Response:
        """Handle DEL requests."""
        complete_endpoint = f"{endpoint}/{resource_id}"
        logger.debug("Processing DEL request at endpoint: %s", complete_endpoint)
        return self.api.request(
            url=complete_endpoint, req_type="DELETE", raise_on_error=False, **kwargs
        )

    def _handle_status_codes(
        self, res: requests.Response, codes: dict[int, tuple[bool, str]]
    ) -> bool:
        """
        Handle status codes.

        Args:
            res: The response object.
            codes: Expected status codes and their corresponding pass/fail status and descriptive messages.

        Raises:
            :class:`STFailedAuthenticationError`: If the operation fails with HTTP error 401 (Unauthorized).
            :class:`STFailedResponseError`: If the operation fails with a known error code.
            :class:`STUnexpectedResponseError`: If the operation fails with an unexpected status code.

        Returns:
            bool: True if the status code indicates success, False otherwise.

        """
        if res.status_code == 401:
            raise STFailedAuthenticationError(response=res)

        if res.status_code in codes:
            success = codes[res.status_code][0]
            result_message = res.reason or codes[res.status_code][1]
            if success is True:
                logger.debug(result_message, extra={"status_code": res.status_code})
                return success
            raise STFailedResponseError(result_message, response=res)

        raise STUnexpectedResponseError(response=res)

    def _add_if_field_not_empty(
        self, receiving_dict: dict, key: str, value: Any | None, *, overwrite: bool = False
    ) -> dict:
        """
        Add a key/value pair to a dictionary if the value is not None.

        Args:
            receiving_dict:
                The dictionary to add the key/value pair to.
            key:
                The key to add.
            value:
                The value to add.
            overwrite:
                Whether to overwrite the value if the key already exists.

        Raises:
            KeyError: If the key already exists in the dictionary and overwrite is not True.

        Returns:
            The updated dictionary.

        """
        if overwrite is not True and key in receiving_dict:
            err_msg = f"'{key}' already exists."
            raise KeyError(err_msg)

        if value:
            receiving_dict[key] = value.value if isinstance(value, Enum) else value
            logger.debug(
                "Added '%s' with value '%s' to payload or parameters dictionary", key, value
            )
        else:
            logger.debug(
                "Skipping adding '%s' to payload or parameters dictionary as value is None",
                key,
            )

        return receiving_dict
