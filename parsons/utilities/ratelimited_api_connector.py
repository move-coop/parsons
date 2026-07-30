import requests
from pyrate_limiter import Limiter, Rate

from parsons.utilities.api_connector import APIConnector


class RateLimitedAPIConnector(APIConnector):
    """A wrapper around APIConnector that adds rate limiting using pyrate-limiter."""

    def __init__(self, *args, ratelimit: Rate, **kwargs) -> None:
        self.limiter = Limiter(ratelimit)
        super().__init__(*args, **kwargs)

    def request(
        self,
        *args,
        **kwargs,
    ) -> requests.Response:
        """Make a request with pyrate-limiter."""
        self.limiter.try_acquire("api_call")
        return super().request(*args, **kwargs)
