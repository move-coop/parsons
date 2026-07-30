import logging
import numbers

from requests.exceptions import HTTPError

from parsons.solidarity_tech.exceptions import STUnexpectedResponseCodeError
from parsons.solidarity_tech.solidarity_tech_base import SolidarityTechBase

CompareValueType = str | numbers.Rational | bool
QueryParamType = dict[
    str, str | bool | list[dict[str, CompareValueType | list[dict[str, CompareValueType]]]]
]

logger = logging.getLogger(__name__)


class SolidarityTechUserRelationships(SolidarityTechBase):
    def get_user_relationships(
        self,
        user_id: int,
    ) -> str:
        """
        Retrieve a list of user relationships.

        Args:
            user_id:
                ID of the user to retrieve relationships for.

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

        if res.status_code != 200:
            raise STUnexpectedResponseCodeError(res)

        return res.text

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

        Returns:
            Boolean representing success of the operation.
            True if the operation was successful, False otherwise.

        Raises:
            HTTPError: If the operation fails with a 422 status code.
            STUnexpectedResponseCodeError: If the operation fails with an unexpected status code.

        Documentation Reference:
            `<https://www.solidarity.tech/reference/post_user-relationships>`__

        """
        params = {
            "user_id": user_id,
            "related_user_id": related_user_id,
            "relationship_type": relationship_type,
        }
        res = self._post_request("user_relationships", params=params)

        if res.status_code not in (201, 422):
            raise STUnexpectedResponseCodeError(res)

        if res.status_code == 422:
            raise HTTPError("Invalid request", response=res)

        return res.status_code == 201

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

        Returns:
            Boolean representing success of the operation.
            True if the operation was successful, False otherwise.

        Raises:
            STUnexpectedResponseCodeError: If the operation fails with an unexpected status code.

        Documentation Reference:
            `<https://www.solidarity.tech/reference/delete_user-relationships-id>`__

        """
        params = {"user_id": user_id}
        res = self._del_request(
            "user_relationships",
            id,
            params=params,
        )

        if res.status_code not in (200, 404):
            raise STUnexpectedResponseCodeError(res)

        return res.status_code == 200
