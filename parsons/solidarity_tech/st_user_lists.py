import logging
import numbers
from datetime import datetime

import numpy as np

from parsons import Table
from parsons.solidarity_tech.solidarity_tech_base import SolidarityTechBase
from parsons.solidarity_tech.solidarity_tech_literals import ScopeType

CompareValueType = str | numbers.Rational | bool
QueryParamType = dict[
    str, str | bool | list[dict[str, CompareValueType | list[dict[str, CompareValueType]]]]
]

logger = logging.getLogger(__name__)


class SolidarityTechUserLists(SolidarityTechBase):
    def get_user_lists(
        self,
        limit: int = 20,
        offset: int = 0,
        since: int | datetime = 0,
    ) -> Table:
        """
        Retrieve a list of user lists.

        Args:
            limit:
                Limits the number of items returned.
                Default is 20, maximum is 100.
            offset:
                Number of items to skip before starting to return the results.
            since:
                UTC timestamp in seconds since the Unix epoch to filter calls created after this time.

        Raises:
            :class:`STFailedResponseError`: If the operation fails with a known error code.
            :class:`STUnexpectedResponseError`: If the operation fails with an unexpected status code.

        Returns:
            All the user lists.

        Documentation Reference:
            `<https://www.solidarity.tech/reference/get_user-lists>`__

        """
        res = self._get_resources(
            "user_lists",
            limit=limit,
            offset=offset,
            since=since,
        )

        expected_responses = {200: (True, "user lists listed")}
        self._handle_status_codes(res=res, codes=expected_responses)

        return Table(res.json())

    def get_user_list(
        self,
        id: int,
    ) -> dict:
        """
        Retrieve a single user list.

        Args:
            id:
                ID of the user list to retrieve.

        Raises:
            :class:`STFailedResponseError`: If the operation fails with a known error code.
            :class:`STUnexpectedResponseError`: If the operation fails with an unexpected status code.

        Returns:
            A single user list.

        Documentation Reference:
            `<https://www.solidarity.tech/reference/get_user-lists-id>`__

        """
        res = self._get_single_resource("user_lists", id)

        expected_responses = {
            200: (True, "user list found"),
            404: (False, "user list not found"),
        }
        self._handle_status_codes(res=res, codes=expected_responses)

        return res.json()

    def create_user_list(
        self,
        name: str,
        scope_id: np.int64,
        scope_type: ScopeType,
        event_id: np.int64 | None = None,
        user_id: np.int64 | None = None,
        parameters: QueryParamType | None = None,
    ) -> bool:
        """
        Create a user list with the specified details.

        The parameters field must conform to the QueryBuilder format.
        For documentation, see `<https://querybuilder.js.org/#filters>`__.

        Args:
            name:
                Name of the user list.
            scope_id:
                Identifier for the scope.
            scope_type:
                Type of the scope.
            event_id:
                Identifier for the associated event, if applicable.
            user_id:
                Identifier for the associated user.
            ``parameters``:
                Parameters for filtering users in QueryBuilder format.

        Raises:
            :class:`STFailedResponseError`: If the operation fails with a known error code.
            :class:`STUnexpectedResponseError`: If the operation fails with an unexpected status code.

        Returns:
            Boolean representing success of the operation.
            True if the operation was successful, False otherwise.

        Documentation Reference:
            `<https://www.solidarity.tech/reference/post_user-lists>`__

        """
        payload = {
            "name": name,
            "scope_id": scope_id,
            "scope_type": scope_type,
            "event_id": event_id,
            "user_id": user_id,
            "parameters": parameters,
        }
        res = self._post_request(
            "user_lists", payload=payload, additional_headers={"content-type": "application/json"}
        )

        expected_responses = {
            201: (True, "user list created"),
            422: (False, "unprocessable entity"),
        }
        return self._handle_status_codes(res=res, codes=expected_responses)

    def update_user_list(
        self,
        id: int,
        name: str | None = None,
        scope_id: np.int64 | None = None,
        scope_type: str | None = None,
        parameters: QueryParamType | None = None,
        event_id: np.int64 | None = None,
    ) -> bool:
        """
        Update a user list with the specified details.

        The parameters field must conform to the QueryBuilder format.
        For documentation, see `<https://querybuilder.js.org/#filters>`__.

        Args:
            id:
                Identifier of the user list to update.
            name:
                Name of the user list.
            scope_id:
                Identifier of the scope.
            scope_type:
                Type of the scope.
            ``parameters``:
                Parameters for filtering users in QueryBuilder format.
            event_id:
                Identifier for the associated event, if applicable.

        Raises:
            :class:`STFailedResponseError`: If the operation fails with a known error code.
            :class:`STUnexpectedResponseError`: If the operation fails with an unexpected status code.

        Returns:
            Boolean representing success of the operation.
            True if the operation was successful, False otherwise.

        Documentation Reference:
            `<https://www.solidarity.tech/reference/put_user-lists-id>`__

        """
        payload = {
            "name": name,
            "scope_id": scope_id,
            "scope_type": scope_type,
            "parameters": parameters,
            "event_id": event_id,
        }
        res = self._put_request(
            "user_lists",
            id,
            payload=payload,
            additional_headers={"content-type": "application/json"},
        )

        expected_responses = {
            200: (True, "user list updated"),
            404: (False, "user list not found"),
        }
        return self._handle_status_codes(res=res, codes=expected_responses)

    def delete_user_list(
        self,
        id: str,
    ) -> bool:
        """
        Delete a user list with the specified ID.

        Args:
            id:
                Identifier of the user list to delete

        Raises:
            :class:`STFailedResponseError`: If the operation fails with a known error code.
            :class:`STUnexpectedResponseError`: If the operation fails with an unexpected status code.

        Returns:
            Boolean representing success of the operation.
            True if the operation was successful, False otherwise.

        Documentation Reference:
            `<https://www.solidarity.tech/reference/delete_user-lists-id>`__

        """
        res = self._del_request(
            "user_lists",
            id,
        )

        expected_responses = {
            200: (True, "user list deleted"),
            404: (False, "user list not found"),
        }
        return self._handle_status_codes(res=res, codes=expected_responses)
