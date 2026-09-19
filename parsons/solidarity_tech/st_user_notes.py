"""Connector class for interacting with the SolidarityTech User Notes endpoint."""

from __future__ import annotations

import logging
from http import HTTPStatus
from typing import TYPE_CHECKING

from parsons.solidarity_tech.base import SolidarityTechBase

if TYPE_CHECKING:
    from parsons.solidarity_tech.datatypes import InteractionType
    from parsons.utilities.api_connector import _JsonType

logger = logging.getLogger(__name__)


class SolidarityTechUserNotes(SolidarityTechBase):
    """Methods for interacting with the SolidarityTech user notes endpoint."""

    def create_user_note(
        self,
        user_id: int,
        content: str,
        agent_id: int | None = None,
        created_at: int | None = None,
        interaction_method: InteractionType | None = None,
        *,
        restricted: bool = False,
    ) -> bool:
        """
        Create a user note with the specified details.

        Args:
            user_id:
                Identifier for the user the note refers to.
            agent_id:
                Identifier for the agent to whom the note
                is attributed, if applicable.
            content:
                Content of the user note.
            created_at:
                Timestamp for when the note was created.
            interaction_method:
                Interaction type that produced the note.
            restricted:
                If True, the note is only visible to team members
                with the View Restricted Properties permission.

        Raises:
            :class:`STFailedResponseError`: If the operation fails with a known error code.
            :class:`STUnexpectedResponseError`: If the operation fails with an unexpected status code.

        Returns:
            Boolean representing success of the operation.
            True if the operation was successful, False otherwise.

        Documentation Reference:
            `<https://www.solidarity.tech/reference/post_user-notes>`__

        """
        params: dict[str, _JsonType] = {
            "user_id": user_id,
            "content": content,
            "restricted": restricted,
        }
        _ = agent_id is not None and params.update({"agent_id": agent_id})
        _ = created_at is not None and params.update({"created_at": created_at})
        _ = interaction_method is not None and params.update(
            {"interaction_method": interaction_method}
        )

        res = self._post_request("user_notes", params=params)

        expected_responses = {
            HTTPStatus.CREATED: (True, "user note created successfully"),
            HTTPStatus.NOT_FOUND: (False, "unprocessable entity"),
            HTTPStatus.UNPROCESSABLE_ENTITY: (False, "unprocessable entity"),
        }
        return self._handle_status_codes(res=res, codes=expected_responses)

    def delete_user_note(
        self,
        resource_id: int,
        user_id: int,
        agent_id: int | None = None,
    ) -> bool:
        """
        Delete a user note with the specified ID.

        Args:
            resource_id:
                Identifier of the user note to delete
            user_id:
                Identifier for the user the note refers to.
            agent_id:
                Identifier for the agent to whom the note
                is attributed, if applicable.

        Raises:
            :class:`STFailedResponseError`: If the operation fails with a known error code.
            :class:`STUnexpectedResponseError`: If the operation fails with an unexpected status code.

        Returns:
            Boolean representing success of the operation.
            True if the operation was successful, False otherwise.

        Documentation Reference:
            `<https://www.solidarity.tech/reference/delete_user-notes-id>`__

        """
        params: dict[str, _JsonType] = {"user_id": user_id}
        _ = agent_id is not None and params.update({"agent_id": agent_id})

        res = self._delete_request("user_notes", resource_id, params=params)

        expected_responses = {
            HTTPStatus.OK: (True, "user note deleted"),
            HTTPStatus.NOT_FOUND: (False, "user note not found"),
        }
        return self._handle_status_codes(res=res, codes=expected_responses)
