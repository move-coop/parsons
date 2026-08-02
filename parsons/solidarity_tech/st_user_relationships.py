import logging
import numbers
from typing import Literal

from parsons import Table
from parsons.solidarity_tech.solidarity_tech_base import SolidarityTechBase

logger = logging.getLogger(__name__)

CompareValueType = str | numbers.Rational | bool
QueryParamType = dict[
    str, str | bool | list[dict[str, CompareValueType | list[dict[str, CompareValueType]]]]
]
UserRelationshipData = dict[Literal["id", "text"], str]


class SolidarityTechUserRelationships(SolidarityTechBase):
    def get_user_relationships(
        self,
        user_id: int,
    ) -> Table:
        """
        Retrieve a list of user relationships.

        Args:
            user_id:
                ID of the user to retrieve relationships for.

        Raises:
            :class:`STFailedResponseError`: If the operation fails with a known error code.
            :class:`STUnexpectedResponseError`: If the operation fails with an unexpected status code.

        Returns:
            All the user relationships.

        Documentation Reference:
            `<https://www.solidarity.tech/reference/get_user-relationships>`__

        """
        params = {"user_id": user_id}
        res = self._get_resources(
            "user_relationships",
            params=params,
            additional_headers={"accept": "application/json"},
        )

        expected_responses = {
            200: (True, "user relationships listed"),
        }
        self._handle_status_codes(res=res, codes=expected_responses)

        data: list[UserRelationshipData] = res.json()
        return Table(data)

    def create_user_relationship(
        self,
        user_id: int,
        related_user_id: int,
        relationship_type: str,
    ) -> bool:
        """
        Create a user relationship between users of the specified type.

        Args:
            user_id:
                Identifier for the user.
            related_user_id:
                Identifier for the related user.
            relationship_type:
                Type of the relationship.

        Raises:
            :class:`STFailedResponseError`: If the operation fails with a known error code.
            :class:`STUnexpectedResponseError`: If the operation fails with an unexpected status code.

        Returns:
            Boolean representing success of the operation.
            True if the operation was successful, False otherwise.

        Documentation Reference:
            `<https://www.solidarity.tech/reference/post_user-relationships>`__

        """
        params = {
            "user_id": user_id,
            "related_user_id": related_user_id,
            "relationship_type": relationship_type,
        }
        res = self._post_request("user_relationships", params=params)

        expected_responses = {
            201: (True, "user relationship created"),
            422: (False, "invalid request"),
        }
        return self._handle_status_codes(res=res, codes=expected_responses)

    def delete_user_relationship(
        self,
        id: int,
        user_id: int,
    ) -> bool:
        """
        Delete a user relationship.

        Args:
            id:
                Identifier of the user relationship to delete.
            user_id:
                Identifier for the user.

        Raises:
            :class:`STFailedResponseError`: If the operation fails with a known error code.
            :class:`STUnexpectedResponseError`: If the operation fails with an unexpected status code.

        Returns:
            Boolean representing success of the operation.
            True if the operation was successful, False otherwise.

        Documentation Reference:
            `<https://www.solidarity.tech/reference/delete_user-relationships-id>`__

        """
        params = {"user_id": user_id}
        res = self._del_request(
            "user_relationships",
            id,
            params=params,
        )

        expected_responses = {
            200: (True, "user relationship deleted"),
            404: (False, "user relationship not found"),
        }
        return self._handle_status_codes(res=res, codes=expected_responses)
