import json
import logging
import time
from typing import Any
from urllib.parse import parse_qs, urlparse

from parsons import Table
from parsons.utilities import check_env
from parsons.utilities.api_connector import APIConnector

logger = logging.getLogger(__name__)


class NationBuilder:
    """
    Instantiate the NationBuilder class

    Args:
        slug:
            The Nation Builder slug.
            The slug is the nation slug of the nation from which your application is
            requesting approval to retrieve data via the NationBuilder API.
            For example, your application's user could provide this slug via a text field in your application.
            Not required if ``NB_SLUG`` env variable set.
        access_token:
            The Nation Builder access_token.
            Not required if ``NB_ACCESS_TOKEN`` env variable set.

    """

    def __init__(self, slug: str | None = None, access_token: str | None = None) -> None:
        self.slug: str = check_env.check("NB_SLUG", slug)
        self.token: str = check_env.check("NB_ACCESS_TOKEN", access_token)

        headers = {"Content-Type": "application/json", "Accept": "application/json"}
        headers.update(self.get_auth_headers(self.token))

        self.client = APIConnector(NationBuilder.get_uri(self.slug), headers=headers)

    @classmethod
    def get_uri(cls, slug: str | None) -> str:
        if slug is None:
            raise ValueError("slug can't be None")

        if not isinstance(slug, str):
            raise ValueError("slug must be an str")

        if len(slug.strip()) == 0:
            raise ValueError("slug can't be an empty str")

        return f"https://{slug}.nationbuilder.com/api/v1"

    @classmethod
    def get_auth_headers(cls, access_token: str | None) -> dict[str, str]:
        if access_token is None:
            raise ValueError("access_token can't be None")

        if not isinstance(access_token, str):
            raise ValueError("access_token must be an str")

        if len(access_token.strip()) == 0:
            raise ValueError("access_token can't be an empty str")

        return {"authorization": f"Bearer {access_token}"}

    @classmethod
    def parse_next_params(cls, next_value: str) -> tuple[str, str]:
        next_params = parse_qs(urlparse(next_value).query)

        if "__nonce" not in next_params:
            raise ValueError("__nonce param not found")

        if "__token" not in next_params:
            raise ValueError("__token param not found")

        nonce = next_params["__nonce"][0]
        token = next_params["__token"][0]

        return nonce, token

    @classmethod
    def make_next_url(cls, original_url: str, nonce: str, token: str) -> str:
        return f"{original_url}?limit=100&__nonce={nonce}&__token={token}"

    def get_people(self) -> Table:
        """Get the data of all people stored in Nation Builder."""
        data = []
        original_url = "people"

        url = f"{original_url}"

        while True:
            try:
                logging.debug(f"sending request {url}")
                response = self.client.get_request(url=url)

                res = response.get("results", None)

                if res is None:
                    break

                logging.debug(f"response got {len(res)} records")

                data.extend(res)

                if response.get("next", None):
                    nonce, token = NationBuilder.parse_next_params(response["next"])
                    url = NationBuilder.make_next_url(original_url, nonce, token)
                else:
                    break
            except Exception as error:
                logging.error(f"error requesting data from Nation Builder: {error}")

                wait_time = 30
                logging.info("waiting %s seconds before retrying", wait_time)
                time.sleep(wait_time)

        return Table(data)

    def update_person(self, person_id: str, person: dict[str, Any]) -> dict[str, Any]:
        """
        This method updates a person with the provided id to have the provided data.

        It returns a full representation of the updated person.

        Args:
            person_id: Nation Builder person id.
            data:
                Nation builder person object.
                For example ``{"email": "user@example.com", "tags": ["foo", "bar"]}``
                Docs: `<https://nationbuilder.com/people_api>`__

        Returns:
            All of the data for the updated person.

        Raises:
            ValueError: If `person` is not a dictionary.
            ValueError: If `person_id` is ``None``, not a string, or empty.

        """
        if not isinstance(person, dict):
            raise ValueError("person must be a dict")

        if person_id is None:
            raise ValueError("person_id can't be None")

        if not isinstance(person_id, str):
            raise ValueError("person_id must be a str")

        if len(person_id.strip()) == 0:
            raise ValueError("person_id can't be an empty str")

        url = f"people/{person_id}"
        return self.client.put_request(url, data=json.dumps({"person": person}))

    def upsert_person(self, person: dict[str, Any]) -> tuple[bool, dict[str, Any] | None]:
        """
        Updates a matched person or creates a new one if the person doesn't exist.

        This method attempts to match the input person resource to a person already in the nation.
        If a match is found, the matched person is updated.
        If a match is not found, a new person is created.

        Matches are found by including one of the following IDs in the request:

        - civicrm_id
        - county_file_id
        - dw_id
        - external_id
        - email
        - facebook_username
        - ngp_id
        - salesforce_id
        - twitter_login
        - van_id

        Args:
            data:
                Nation builder person object.
                For example ``{"email": "user@example.com", "tags": ["foo", "bar"]}``
                Docs: `<https://nationbuilder.com/people_api>`__

        Returns:
            A tuple of ``created`` and ``person`` objects with the updated data.
            If the request fails the method will return a tuple of ``False`` and ``None``.

        Raises:
            ValueError: If the person argument is not a dict.
            ValueError: If the person dict is missing required keys.

        """

        _required_keys = [
            "civicrm_id",
            "county_file_id",
            "dw_id",
            "external_id",
            "email",
            "facebook_username",
            "ngp_id",
            "salesforce_id",
            "twitter_login",
            "van_id",
        ]

        if not isinstance(person, dict):
            raise ValueError("person must be a dict")

        has_required_key = any(x in person for x in _required_keys)

        if not has_required_key:
            _keys = ", ".join(_required_keys)
            raise ValueError(f"person dict must contain at least one key of {_keys}")

        url = "people/push"
        response = self.client.request(url, "PUT", data=json.dumps({"person": person}))

        self.client.validate_response(response)

        if response.status_code == 200 and self.client.json_check(response):
            return (False, response.json())

        if response.status_code == 201 and self.client.json_check(response):
            return (True, response.json())

        return (False, None)
