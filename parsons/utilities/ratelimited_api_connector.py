import requests
from pyrate_limiter import Limiter, Rate

from parsons.utilities.api_connector import APIConnector


class RateLimitedAPIConnector(APIConnector):
    """A wrapper around :class:`APIConnector` that adds rate limiting."""

    def __init__(self, *args, ratelimit: Rate, **kwargs) -> None:
        """
        Initialize the RateLimitedAPIConnector.

        Accepts and passes through all the args and kwargs of :class:`APIConnector`.

        Args:
            ratelimit:
                The rate limit to apply to API calls,
                as a pyrate-limiter :class:`pyrate_limiter.abstracts.Rate` object.

        """
        self.limiter = Limiter(ratelimit)
        super().__init__(*args, **kwargs)

    def request(
        self,
        *args,
        **kwargs,
    ) -> requests.Response:
        """
        Make a rate limited request.

        If the rate limit has been exceeded, the request will be held for the next available opportunity.
        All args will be passed through to :class:`APIConnector`.

        """
        self.limiter.try_acquire("api_call")
        return super().request(*args, **kwargs)
