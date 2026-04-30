import logging

import requests

from parsons import Table
from parsons.utilities import check_env

logger = logging.getLogger(__name__)

TURBOVOTE_URI = "https://turbovote-admin-http-api.prod.democracy.works/"


class TurboVote:
    """
    Instantiate the TurboVote class.

    Args:
        username:
            A valid TurboVote username.
            Not required if ``TURBOVOTE_USERNAME`` env variable set.
        password:
            A valid TurboVote password.
            Not required if ``TURBOVOTE_PASSWORD`` env variable set.
        subdomain:
            Your TurboVote subdomain (i.e. ``https://MYORG.turbovote.org``).
            Not required if ``TURBOVOTE_SUBDOMAIN`` env variable set.

    """

    def __init__(
        self, username: str | None = None, password: str | None = None, subdomain: str | None = None
    ) -> None:
        self.username: str = check_env.check("TURBOVOTE_USERNAME", username)
        self.password: str = check_env.check("TURBOVOTE_PASSWORD", password)
        self.subdomain: str = check_env.check("TURBOVOTE_SUBDOMAIN", subdomain)
        self.uri = TURBOVOTE_URI

    def _get_token(self):
        """Retrieve a temporary bearer token to access API."""
        url = self.uri + "login"
        payload = {"username": self.username, "password": self.password}
        r = requests.post(url, data=payload)
        logger.debug(r.url)
        r.raise_for_status()

        return r.json()["id-token"]

    def get_users(self) -> Table:
        """Get users."""
        url = self.uri + f"partners/{self.subdomain}.turbovote.org/users"
        headers = {"Authorization": f"Bearer {self._get_token()}"}
        r = requests.get(url, headers=headers)
        logger.debug(r)
        r.raise_for_status()

        tbl = Table.from_csv_string(r.text)
        logger.info(f"{tbl.num_rows} users retrieved.")

        return tbl
