"""Authentication classes for APIs that use bearer token."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from requests.auth import AuthBase

if TYPE_CHECKING:
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

    def __init__(
        self,
        api_key: str,
        *,
        header_name: str = "Authorization",
        token_name: str | None = "Bearer",
        token_divider: str | None = " ",
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

        """
        self.api_key = api_key.strip()
        self.header_name = header_name
        self.token_name = token_name
        self.token_divider = token_divider

    def __eq__(self, other: object) -> bool:
        """Check if two instances have the same API key."""
        same_api_key = self.api_key == getattr(other, "api_key", None)
        same_header_name = self.header_name == getattr(other, "header_name", None)
        same_token_name = self.token_name == getattr(other, "token_name", None)
        same_token_divider = self.token_divider == getattr(other, "token_divider", None)

        return same_api_key and same_header_name and same_token_name and same_token_divider

    def __hash__(self) -> int:
        """Ensure that two instsances with the same configuration have the same hash."""
        return hash(
            self.api_key + self.header_name + str(self.token_name) + str(self.token_divider)
        )

    def __repr__(self) -> str:
        """Return a string representation of the instance."""
        representation = f"api_key={self.api_key}"
        representation += f" header_name={self.header_name}"
        if self.token_name:
            representation += f" token_name={self.token_name}"
        if self.token_divider:
            representation += f" token_divider={self.token_divider}"

        return f"<BearerAuth {representation}>"

    def __call__(self, r: requests.PreparedRequest) -> requests.PreparedRequest:
        """
        Add authorization header to the supplied request.

        Header key is determined by `self.header_name`.
        Header value is determined by `self.token_name` and `self.api_key`, separated by `self.token_divider`.
        If `self.token_name` is not available, `self.api_key` is used as the header value and `self.token_divider` is not used.

        """
        header_value = (
            f"{self.token_name}{self.token_divider}{self.api_key}"
            if self.token_name
            else self.api_key
        )
        r.headers[self.header_name] = header_value

        return r
