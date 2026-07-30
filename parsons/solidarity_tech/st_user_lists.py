import logging
import numbers
from datetime import datetime

import numpy as np
from requests.exceptions import HTTPError

from parsons.solidarity_tech.exceptions import STUnexpectedResponseCodeError
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
    ) -> str:
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

        if res.status_code != 200:
            raise STUnexpectedResponseCodeError(res)

        return res.text

    def get_user_list(
        self,
        id: int,
    ) -> str:
        """
        Retrieve a single user list.

        Args:
            id:
                ID of the user list to retrieve.

        Returns:
            A single user list.

        Raises:
            STUnexpectedResponseCodeError: If the operation fails with an unexpected status code.

        Documentation Reference:
            `<https://www.solidarity.tech/reference/get_user-lists-id>`__

        """
        res = self._get_single_resource("user_lists", id)

        if res.status_code not in (200, 404):
            raise STUnexpectedResponseCodeError(res)

        return res.text

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

        Returns:
            Boolean representing success of the operation.
            True if the operation was successful, False otherwise.

        Raises:
            HTTPError: If the operation fails with a 422 status code.
            STUnexpectedResponseCodeError: If the operation fails with an unexpected status code.

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

        if res.status_code not in (201, 422):
            raise STUnexpectedResponseCodeError(res)

        if res.status_code == 422:
            raise HTTPError("Unprocessable request, likely issue with parameters", response=res)

        return res.status_code == 201

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


        Returns:
            Boolean representing success of the operation.
            True if the operation was successful, False otherwise.

        Raises:
            STUnexpectedResponseCodeError: If the operation fails with an unexpected status code.

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

        if res.status_code not in (200, 404):
            raise STUnexpectedResponseCodeError(res)

        return res.status_code == 200

    def delete_user_list(
        self,
        id: str,
    ) -> bool:
        """
        Delete a user list with the specified ID.

        Args:
            id:
                Identifier of the user list to delete

        Returns:
            Boolean representing success of the operation.
            True if the operation was successful, False otherwise.

        Raises:
            STUnexpectedResponseCodeError: If the operation fails with an unexpected status code.

        Documentation Reference:
            `<https://www.solidarity.tech/reference/delete_user-lists-id>`__

        """
        res = self._del_request(
            "user_lists",
            id,
        )

        if res.status_code not in (200, 404):
            raise STUnexpectedResponseCodeError(res)

        return res.status_code == 200
