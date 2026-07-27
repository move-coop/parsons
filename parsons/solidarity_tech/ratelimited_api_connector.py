import requests
from pyrate_limiter import Duration, Limiter, Rate

from parsons.utilities.api_connector import APIConnector

rates = [
    Rate(60, Duration.SECOND * 30),  # 60 requests per 30 seconds
]
limiter = Limiter(rates)


class RateLimitedAPIConnector(APIConnector):
    @limiter.as_decorator(name="api_call", weight=1)
    def request(
        self,
        *args,
        **kwargs,
    ) -> requests.Response:
        """Make a request with pyrate-limiter."""
        return super().request(*args, **kwargs)
