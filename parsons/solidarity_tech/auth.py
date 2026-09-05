"""Authentication classes for Parsons Solidarity Tech API."""

from __future__ import annotations

from typing import TYPE_CHECKING

from requests.auth import AuthBase

if TYPE_CHECKING:
    import requests


class SolidarityTechAuth(AuthBase):
    """Attaches API key / bearer token to the given Request object."""

    api_key: str | bytes

    def __init__(self, api_key: str | bytes) -> None:
        self.api_key = api_key

    def __eq__(self, other: object) -> bool:
        """Check if two instances have the same API key."""
        return self.api_key == getattr(other, "api_key", None)

    def __hash__(self) -> int:
        """Ensure that two instsances with the same key have the same hash."""
        return hash(self.api_key)

    def __repr__(self) -> str:
        """Return a string representation of the instance."""
        return f"<SolidarityTechAuth api_key={self.api_key}>"

    def __call__(self, r: requests.PreparedRequest) -> requests.PreparedRequest:
        """Add authorization header to the supplied request."""
        r.headers["authorization"] = f"Bearer {self.api_key}"
        return r
