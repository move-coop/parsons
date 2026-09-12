import json
import logging
import time
from typing import Any, Literal, cast
from urllib.parse import parse_qs, urlparse

from typing_extensions import (
    deprecated,  # TODO(bmos): import from warnings when Python >= 3.13
)

from parsons.etl.table import Table
from parsons.utilities import check_env
from parsons.utilities.api_connector import APIConnector
from parsons.utilities.bearer_auth import BearerAuth

logger = logging.getLogger(__name__)


class NationBuilder:
    """
    Instantiate the NationBuilder class.

    Args:
        slug: str
            The Nation Builder slug Not required if ``NB_SLUG`` env variable set. The slug is the
            nation slug of the nation from which your application is requesting approval to retrieve
            data via the NationBuilder API. For example, your application's user could provide this
            slug via a text field in your application.
        access_token: str
            The Nation Builder access_token Not required if ``NB_ACCESS_TOKEN`` env variable set.

    """

    def __init__(self, slug: str | None = None, access_token: str | None = None) -> None:
        slug = check_env.check("NB_SLUG", slug)
        token = check_env.check("NB_ACCESS_TOKEN", access_token)
        headers = {"Content-Type": "application/json", "Accept": "application/json"}
        auth = BearerAuth(NationBuilder.validate_auth(token))

        self.client = APIConnector(NationBuilder.get_uri(slug), headers=headers, auth=auth)

    @classmethod
    def get_uri(cls, slug: str | None) -> str:
        """
        Get the NationBuilder API URI for a given slug.

        Raises:
            TypeError: If slug is not a string or None.
            ValueError: If slug is an empty string.

        """
        if slug is None:
            err_msg = "slug can't be None"
            raise TypeError(err_msg)

        if not isinstance(slug, str):
            err_msg = "slug must be an str"
            raise TypeError(err_msg)

        if len(slug.strip()) == 0:
            err_msg = "slug can't be an empty str"
            raise ValueError(err_msg)

        return f"https://{slug}.nationbuilder.com/api/v1"

    @classmethod
    @deprecated("Auth headers are now handled automatically by requests.")
    def get_auth_headers(cls, access_token: str | None) -> dict[Literal["authorization"], str]:
        """
        Return authorization headers for a given access token.

        Deprecated: Use `validate_auth` instead.

        Raises:
            TypeError: If access token is None or not a string.
            ValueError: If access token is an empty string.

        """
        return {"authorization": f"Bearer {access_token}"}

    @classmethod
    def validate_auth(cls, access_token: str | None) -> str:
        """
        Check that `access_token` is a valid string.

        Raises:
            TypeError: If access token is None or not a string.
            ValueError: If access token is an empty string.

        """
        if access_token is None:
            err_msg = "access_token can't be None"
            raise TypeError(err_msg)

        if not isinstance(access_token, str):
            err_msg = "access_token must be an str"
            raise TypeError(err_msg)

        if len(access_token.strip()) == 0:
            err_msg = "access_token can't be an empty str"
            raise ValueError(err_msg)

        return access_token

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
        """
        Returns:
            A Table of all people stored in Nation Builder.

        """
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
        Update a person with the provided id to have the provided data.

        It returns a full representation of the updated person.

        Args:
            person_id: str
                Nation Builder person id.
            data: dict
                Nation builder person object.
                For example {"email": "user@example.com", "tags": ["foo", "bar"]}
                Docs: https://nationbuilder.com/people_api

        Returns:
            A person object with the updated data.

        """
        if person_id is None:
            raise ValueError("person_id can't be None")

        if not isinstance(person_id, str):
            raise ValueError("person_id must be a str")

        if len(person_id.strip()) == 0:
            raise ValueError("person_id can't be an empty str")

        if not isinstance(person, dict):
            raise ValueError("person must be a dict")

        url = f"people/{person_id}"
        response = self.client.put_request(url=url, data=json.dumps({"person": person}))
        response = cast("dict[str, Any]", response)

        return response

    def upsert_person(self, person: dict[str, Any]) -> tuple[bool, dict[str, Any] | None]:
        """
        Updates a matched person or creates a new one if the person doesn't exist.

        This method attempts to match the input person resource to a person already in the
        nation. If a match is found, the matched person is updated. If a match is not found, a new
        person is created. Matches are found by including one of the following IDs in the request:

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
            data: dict
                Nation builder person object.
                For example {"email": "user@example.com", "tags": ["foo", "bar"]}
                Docs: https://nationbuilder.com/people_api
        Returns:
            A tuple of `created` and `person` object with the updated data. If the request fails
            the method will return a tuple of `False` and `None`.

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
        response = self.client.request(url=url, req_type="PUT", data=json.dumps({"person": person}))

        self.client.validate_response(response)

        if response.status_code == 200 and self.client.json_check(response):
            return (False, response.json())

        if response.status_code == 201 and self.client.json_check(response):
            return (True, response.json())

        return (False, None)
