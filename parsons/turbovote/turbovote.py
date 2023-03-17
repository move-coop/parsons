from parsons.etl import Table
import requests
import logging
from parsons.utilities import check_env

logger = logging.getLogger(__name__)

TURBOVOTE_URI = "https://turbovote-admin-http-api.prod.democracy.works/"


class TurboVote(object):
    """
    Instantiate the TurboVote class

    `Args:`
        username: str
            A valid TurboVote username. Not required if ``TURBOVOTE_USERNAME``
            env variable set.
        password: str
            A valid TurboVote password. Not required if ``TURBOVOTE_PASSWORD``
            env variable set.
        subdomain: str
            Your TurboVote subdomain (i.e. ``https://MYORG.turbovote.org``). Not
            required if ``TURBOVOTE_SUBDOMAIN`` env variable set.
    `Returns:`
        class
    """

    def __init__(self, username=None, password=None, subdomain=None):

        self.username = check_env.check("TURBOVOTE_USERNAME", username)
        self.password = check_env.check("TURBOVOTE_PASSWORD", password)
        self.subdomain = check_env.check("TURBOVOTE_SUBDOMAIN", subdomain)
        self.uri = TURBOVOTE_URI

    def _get_token(self):
        # Retrieve a temporary bearer token to access API

        url = self.uri + "login"
        payload = {"username": self.username, "password": self.password}
        r = requests.post(url, data=payload)
        logger.debug(r.url)
        r.raise_for_status()

        return r.json()["id-token"]

    def get_users(self):
        """
        Get users.

        `Returns:`
            Parsons Table
                See :ref:`parsons-table` for output options.
        """

        url = self.uri + f"partners/{self.subdomain}.turbovote.org/users"

        headers = {"Authorization": f"Bearer {self._get_token()}"}
        r = requests.get(url, headers=headers)
        logger.debug(r)
        r.raise_for_status()
        tbl = Table.from_csv_string(r.text)
        logger.info(f"{tbl.num_rows} users retrieved.")

        return tbl
