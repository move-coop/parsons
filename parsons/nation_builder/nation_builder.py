import logging
import time
from typing import Optional
from urllib.parse import parse_qs, urlparse

from parsons import Table
from parsons.utilities import check_env
from parsons.utilities.api_connector import APIConnector

logger = logging.getLogger(__name__)


class NationBuilder:
    """
    Instantiate the NationBuilder class

    `Args:`
        slug: str
            The Nation Builder slug Not required if ``NB_SLUG`` env variable set. The slug is the
            nation slug of the nation from which your application is requesting approval to retrieve
            data via the NationBuilder API. For example, your application's user could provide this
            slug via a text field in your application.
        access_token: str
            The Nation Builder access_token Not required if ``NB_ACCESS_TOKEN`` env variable set.
    """

    def __init__(
        self, slug: Optional[str] = None, access_token: Optional[str] = None
    ) -> None:
        self.slug = check_env.check("NB_SLUG", slug)
        self.access_token = check_env.check("NB_ACCESS_TOKEN", access_token)

        self.uri = f"https://{self.slug}.nationbuilder.com/api/v1"

        self.client = APIConnector(
            self.uri, headers={"authorization": f"Bearer {self.access_token}"}
        )

    def get_people(self):
        """
        `Returns:`
            A Table of all people stored in Nation Builder.
        """
        data = []
        original_url = "people?limit=100"

        url = f"{original_url}"

        while True:
            try:
                logging.debug("sending request %s" % url)
                response = self.client.get_request(url)

                res = response["results"]
                logging.debug("response got %s records" % len(res))

                data.extend(res)

                if response["next"]:
                    next_params = parse_qs(urlparse(response["next"]).query)
                    nonce = next_params["__nonce"][0]
                    token = next_params["__token"][0]
                    url = f"{original_url}&__nonce={nonce}&__token={token}"
                else:
                    break
            except Exception as error:
                logging.error("error requesting data from Nation Builder: %s" % error)
                wait_time = 30
                time.sleep(wait_time)

        return Table(data)
