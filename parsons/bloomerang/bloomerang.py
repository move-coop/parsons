import json
import logging
from typing import Any, Literal

import requests

from parsons import Table
from parsons.utilities import check_env
from parsons.utilities.api_connector import APIConnector

logger = logging.getLogger(__name__)

URI = "https://api.bloomerang.co/v2/"
URI_AUTH = "https://crm.bloomerang.co/authorize/"


class Bloomerang:
    """
    Instantiate Bloomerang class

    Args:
        api_key:
            The Bloomerang API key.
            Not required if the ``BLOOMERANG_API_KEY`` environment variable is set
            or if the OAuth2 authentication parameters
            ``client_id`` and ``client_secret`` are set.
        client_id:
            The Bloomerang client ID for OAuth2 authentication.
            Not required if the ``BLOOMERANG_CLIENT_ID`` environment variable is set
            or if the ``api_key`` parameter is set.
            Note that the ``client_secret`` parameter must also be set
            in order to use OAuth2 authentication.
        client_secret:
            The Bloomerang client secret for OAuth2 authetication.
            Not required if the ``BLOOMERANG_CLIENT_SECRET`` environment variable is set
            or if the ``api_key`` parameter is set.
            Note that the ``client_id`` parameter must also be set
            in order to use OAuth2 authentication.

    """

    def __init__(
        self,
        api_key: str | None = None,
        client_id: str | None = None,
        client_secret: str | None = None,
    ) -> None:
        self.api_key = check_env.check("BLOOMERANG_API_KEY", api_key, optional=True)
        self.client_id = check_env.check("BLOOMERANG_CLIENT_ID", client_id, optional=True)
        self.client_secret = check_env.check(
            "BLOOMERANG_CLIENT_SECRET", client_secret, optional=True
        )
        self.uri = URI
        self.uri_auth = URI_AUTH
        self.conn = self._conn()

    def _conn(self) -> APIConnector:
        # Instantiate APIConnector with authentication credentials
        headers = {"accept": "application/json", "Content-Type": "application/json"}
        if self.api_key is not None:
            logger.info("Using API key authentication.")
            headers["X-API-KEY"] = f"{self.api_key}"
        elif (self.client_id is not None) & (self.client_secret is not None):
            logger.info("Using OAuth2 authentication.")
            self._generate_authorization_code()
            self._generate_access_token()
            headers["Authorization"] = f"Bearer {self.access_token}"
        else:
            raise Exception("Missing authorization credentials.")
        return APIConnector(uri=self.uri, headers=headers)

    def _generate_authorization_code(self) -> None:
        data = {"client_id": self.client_id, "response_type": "code"}
        r = requests.post(url=self.uri_auth, json=data)
        self.authorization_code = r.json().get("code", None)

    def _generate_access_token(self) -> None:
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "authorization_code",
            "code": self.authorization_code,
        }
        r = requests.post(url=self.uri + "oauth/token", json=data)
        self.access_token = r.json().get("access_token", None)

    def _base_endpoint(self, endpoint: str, entity_id: str | int | None = None) -> str:
        url = f"{self.uri}{endpoint}/"
        return url + (f"{entity_id}/" if entity_id else "")

    @staticmethod
    def _base_pagination_params(page_number: int = 1, page_size: int = 50) -> dict[str, int]:
        return {"skip": page_size * (page_number - 1), "take": min(page_size, 50)}

    @staticmethod
    def _base_ordering_params(
        order_by: Literal["Id", "CreatedDate", "LastModifiedDate"] | None = None,
        order_direction: Literal["Asc", "Desc"] | None = None,
    ) -> dict[str, str]:
        params = {}

        if order_by:
            params["orderBy"] = order_by

        if order_direction:
            params["orderDirection"] = order_direction

        return params

    def _base_create(
        self, endpoint: str, entity_id: str | int | None = None, **kwargs
    ) -> dict[str, Any] | int | None:
        return self.conn.post_request(
            url=self._base_endpoint(endpoint, entity_id), json=json.dumps({**kwargs})
        )

    def _base_update(self, endpoint, entity_id=None, **kwargs) -> dict[str, Any] | int | None:
        return self.conn.put_request(
            url=self._base_endpoint(endpoint, entity_id), json=json.dumps({**kwargs})
        )

    def _base_get(
        self, endpoint, entity_id: str | int | None = None, params: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        return self.conn.get_request(url=self._base_endpoint(endpoint, entity_id), params=params)

    def _base_delete(
        self, endpoint: str, entity_id: str | int | None = None
    ) -> dict[str, Any] | int | None:
        return self.conn.delete_request(url=self._base_endpoint(endpoint, entity_id))

    def create_constituent(self, **kwargs) -> dict[str, Any] | int | None:
        """
        Args:
            `**kwargs`:
                Fields to include, e.g., ``FirstName = 'Rachel'``.
                See the `Bloomerang post_constituent documentation`_ for a full list of fields.

        """
        return self._base_create("constituent", **kwargs)

    def update_constituent(
        self, constituent_id: str | int, **kwargs
    ) -> dict[str, Any] | int | None:
        """
        Args:
            constituent_id: Constituent ID to update
            `**kwargs`:
                Fields to update, e.g., ``FirstName = 'RJ'``.
                See the `Bloomerang put_constituent__id_ documentation`_ for a full list of fields.

        """
        return self._base_update("constituent", entity_id=constituent_id, **kwargs)

    def get_constituent(self, constituent_id: str | int) -> dict[str, Any]:
        """
        Args:
            constituent_id: Constituent ID to get fields for

        Returns:
            A JSON of the entry or an error.

        """
        return self._base_get("constituent", entity_id=constituent_id)

    def delete_constituent(self, constituent_id: str | int) -> dict[str, Any] | int | None:
        """
        Args:
            constituent_id: Constituent ID to delete

        """
        return self._base_delete("constituent", entity_id=constituent_id)

    def get_constituents(
        self,
        page_number: int = 1,
        page_size: int = 50,
        order_by: Literal["Id", "CreatedDate", "LastModifiedDate"] = "Id",
        order_direction: Literal["Asc", "Desc"] | None = None,
        last_modified: str | None = None,
    ) -> Table:
        """
        Args:
            page_number:
                Number of the page to fetch
            page_size:
                Number of records per page (maximum allowed is 50)
            order_by:
                Sorts by ``Id``, ``CreatedDate``, or ``LastModifiedDate`` (default ``Id``).
            order_direction:
                Sorts the order_by in ``Asc`` or ``Desc`` order.
            last_modified:
                Filters to constituents last modified after the specified date (ISO-8601 format).

        Returns:
            A Table of the entries.

        """
        params: dict[str, int | str] = self._base_pagination_params(page_number, page_size)
        params.update(self._base_ordering_params(order_by, order_direction))

        if last_modified:
            params["lastModified"] = last_modified

        response = self._base_get("constituents", params=params)
        return Table(response["Results"])

    def create_transaction(self, **kwargs) -> dict[str, Any] | int | None:
        """
        Args:
            `**kwargs`:
                Fields to include, e.g., ``CreditCardType = 'Visa'``.
                See the `Bloomerang post_transaction documentation`_ for a full list of fields.

        """
        return self._base_create("transaction", **kwargs)

    def update_transaction(
        self, transaction_id: str | int, **kwargs
    ) -> dict[str, Any] | int | None:
        """
        Args:
            transaction_id: Transaction ID to update
            `**kwargs`:
                Fields to update, e.g., ``CreditCardType = 'Visa'``.
                See the `Bloomerang put_transaction__id_ documentation`_ for a full list of fields.

        """
        return self._base_update("transaction", entity_id=transaction_id, **kwargs)

    def get_transaction(self, transaction_id: str | int) -> dict[str, Any]:
        """
        Args:
            transaction_id: Transaction ID to get fields for

        Returns:
            A JSON of the entry or an error.

        """
        return self._base_get("transaction", entity_id=transaction_id)

    def delete_transaction(self, transaction_id: str | int) -> dict[str, Any] | int | None:
        """
        Args:
            transaction_id: Transaction ID to delete

        """
        return self._base_delete("transaction", entity_id=transaction_id)

    def get_transactions(
        self,
        page_number: int = 1,
        page_size: int = 50,
        order_by: Literal["Date", "CreatedDate", "LastModifiedDate"] = "Date",
        order_direction: Literal["Asc", "Desc"] = "Desc",
    ) -> Table:
        """
        Args:
            page_number: Number of the page to fetch
            page_size: Number of records per page (maximum allowed is 50)
            order_by:
                Sorts by ``Date``, ``CreatedDate``, or ``LastModifiedDate``.
                Default is ``Date``.
            order_direction:
                Sorts the order_by in ``Asc`` or ``Desc`` order.
                Default is ``Desc``.

        Returns:
            A JSON of the entry or an error.

        """
        params: dict[str, int | str] = self._base_pagination_params(page_number, page_size)
        params.update(self._base_ordering_params(order_by, order_direction))

        response = self._base_get("transactions", params=params)
        return Table(response["Results"])

    def get_transaction_designation(self, designation_id: str | int) -> dict[str, Any]:
        """
        Args:
            designation_id: Transaction Designation ID to get fields for

        Returns:
            A JSON of the entry or an error.

        """
        return self._base_get("transaction/designation", entity_id=designation_id)

    def get_transaction_designations(
        self,
        page_number: int = 1,
        page_size: int = 50,
        order_by: Literal["Date", "CreatedDate", "LastModifiedDate"] = "Date",
        order_direction: Literal["Asc", "Desc"] = "Desc",
    ) -> Table:
        """
        Args:
            page_number: Number of the page to fetch
            page_size: Number of records per page (maximum allowed is 50)
            order_by:
                Sorts by ``Date``, ``CreatedDate``, or ``LastModifiedDate``.
                Defaults to ``Date``.
            order_direction:
                Sorts the order_by in ``Asc`` or ``Desc`` order.
                Defaults to ``Desc``.

        Returns:
            A JSON of the entry or an error.

        """
        params: dict[str, int | str] = self._base_pagination_params(page_number, page_size)
        params.update(self._base_ordering_params(order_by, order_direction))

        response = self._base_get("transactions/designations", params=params)
        return Table(response["Results"])

    def create_interaction(self, **kwargs):
        """
        Args:
            `**kwargs`:
                Fields to include, e.g., ``Channel = "Email"``.
                See the `Bloomerang post_interaction documentation`_ for a full list of fields.

        """
        return self._base_create("interaction", **kwargs)

    def update_interaction(
        self, interaction_id: str | int, **kwargs
    ) -> dict[str, Any] | int | None:
        """
        Args:
            interaction_id: Interaction ID to update
            `**kwargs`:
                Fields to update, e.g., ``EmailAddress = "user@example.com"``.
                See the `Bloomerang put_interaction__id_ documentation`_ for a full list of fields.

        """
        return self._base_update("interaction", entity_id=interaction_id, **kwargs)

    def get_interaction(self, interaction_id: str | int) -> dict[str, Any]:
        """
        Args:
            interaction_id: Interaction ID to get fields for

        Returns:
            A JSON of the entry or an error.

        """
        return self._base_get("interaction", entity_id=interaction_id)

    def delete_interaction(self, interaction_id: str | int) -> dict[str, Any] | int | None:
        """
        Args:
            interaction_id: Interaction ID to delete

        """
        return self._base_delete("interaction", entity_id=interaction_id)

    def get_interactions(self, page_number: int = 1, page_size: int = 50) -> Table:
        """
        Args:
            page_number: Number of the page to fetch
            page_size: Number of records per page (maximum allowed is 50)

        Returns:
            A JSON of the entry or an error.

        """
        params = self._base_pagination_params(page_number, page_size)
        response = self._base_get("interactions", params=params)
        return Table(response["Results"])
