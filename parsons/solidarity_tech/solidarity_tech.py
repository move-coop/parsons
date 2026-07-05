import requests
from pyrate_limiter import Duration, Limiter, Rate

from parsons.utilities import check_env
from parsons.utilities.api_connector import APIConnector

API_URL_BASE = "https://api.solidarity.tech/v1/"


rates = [
    Rate(60, Duration.SECOND * 30),  # 60 requests per 30 seconds
]
limiter = Limiter(rates)


class SolidarityTech:
    def __init__(self, api_token=None) -> None:
        """
        Instantiate the SolidarityTech class.

        Args:
            api_token:
                A valid Bearer token for authorization.
                Not required if the `SOLIDARITY_TECH_TOKEN` env variable is set.

        """
        self.api_token = check_env.check("SOLIDARITY_TECH_TOKEN", api_token)
        self.headers = {
            "accept": "application/json",
            "Authorization": self.api_token,
        }
        self.api_url = API_URL_BASE
        self.api = RateLimitedAPIConnector(self.api_url, headers=self.headers)


class RateLimitedAPIConnector(APIConnector):
    @limiter.as_decorator(name="api_call", weight=1)
    def request(
        self,
        *args,
        **kwargs,
    ) -> requests.Response:
        """Make a request with pyrate-limiter."""
        return super().request(*args, **kwargs)
