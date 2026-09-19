"""Authentication classes for APIs that use bearer token."""

from __future__ import annotations

import logging
import warnings
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from requests.auth import AuthBase

if TYPE_CHECKING:
    from collections.abc import Callable

    import requests

logger = logging.getLogger(__name__)


class BearerAuth(AuthBase):
    """
    Requests authentication handler to add bearer token header to :class:`requests.Session` instances.

    .. code-block:: python

        from requests import Session

        from parsons.utilities.bearer_auth import BearerAuth

        session = Session(auth=BearerAuth("YOUR API KEY HERE"))

    """

    api_key: str
    token_divider: str | None
    header_name: str
    token_name: str | None
    expires: datetime | None
    refresh_callback: Callable[[], tuple[str, datetime]] | None

    def __init__(
        self,
        api_key: str,
        *,
        header_name: str = "Authorization",
        token_name: str | None = "Bearer",
        token_divider: str | None = " ",
        expires: datetime | None = None,
        refresh_callback: Callable[[], tuple[str, datetime]] | None = None,
    ) -> None:
        """
        Initialize handler with the API key.

        Args:
            api_key: The API key to use for authentication.
            header_name:
                Header name to use in authentication header key.
                Defaults to "Authorization".
            token_name:
                Token name to use in authentication header value, before `api_key`.
                Defaults to "Bearer". Can be set to ``None`` to omit the token name and use `api_key` directly.
            token_divider:
                Divider to use in authentication header value, between `token_name` and `api_key`.
                Defaults to " ". If `token_name` is ``None``, this is ignored.
            expires: Optional expiration datetime for the API key.
            refresh_callback:
                Optional callback function / method to refresh the API key.
                Should return a tuple of new API key and expiration datetime.

        """
        self.api_key = api_key.strip()
        self.header_name = header_name
        self.token_name = token_name
        self.token_divider = token_divider
        self.expires = expires
        self.refresh_callback = refresh_callback

    def __eq__(self, other: object) -> bool:
        """Check if two instances have the same API key."""
        same_api_key = self.api_key == getattr(other, "api_key", None)
        same_header_name = self.header_name == getattr(other, "header_name", None)
        same_token_name = self.token_name == getattr(other, "token_name", None)
        same_token_divider = self.token_divider == getattr(other, "token_divider", None)
        same_expires = self.expires == getattr(other, "expires", None)
        same_callback = self.refresh_callback == getattr(other, "refresh_callback", None)

        return (
            same_api_key
            and same_header_name
            and same_token_name
            and same_token_divider
            and same_expires
            and same_callback
        )

    def __hash__(self) -> int:
        """Ensure that two instsances with the same configuration have the same hash."""
        return hash(
            self.api_key
            + self.header_name
            + str(self.token_name)
            + str(self.token_divider)
            + str(self.expires)
            + str(self.refresh_callback)
        )

    def __repr__(self) -> str:
        """Return a string representation of the instance."""
        representation = f"api_key={self.api_key}"
        representation += f" header_name={self.header_name}"
        if self.token_name:
            representation += f" token_name={self.token_name}"
        if self.token_divider:
            representation += f" token_divider={self.token_divider}"
        if self.expires:
            representation += f" expires={self.expires!s}"
        if self.refresh_callback:
            representation += f" refresh_callback={self.refresh_callback!s}"

        return f"<BearerAuth {representation}>"

    def _check_expiration(self) -> None:
        """Check if the token has expired and refresh if necessary."""
        if self.expires is None:
            return

        if datetime.now(timezone.utc) <= self.expires:
            return

        if self.refresh_callback is not None:
            self.api_key, self.expires = self.refresh_callback()
            logger.info("API Token refreshed, will expire at %s.", self.expires)
            return

        log_msg = f"API token expired at {self.expires}. Please re-authenticate."
        warnings.warn(
            log_msg,
            TokenTimeoutWarning,
            stacklevel=3,
        )

    def __call__(self, r: requests.PreparedRequest) -> requests.PreparedRequest:
        """
        Add authorization header to the supplied request.

        Header key is determined by `self.header_name`.
        Header value is determined by `self.token_name` and `self.api_key`, separated by

        """
        self._check_expiration()

        header_value = (
            f"{self.token_name}{self.token_divider}{self.api_key}"
            if self.token_name
            else self.api_key
        )
        r.headers[self.header_name] = header_value

        return r


class TokenTimeoutWarning(Warning):
    """Warning raised when an expired API token is used."""
