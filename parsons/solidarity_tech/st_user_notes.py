from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from parsons.solidarity_tech.base import SolidarityTechBase

if TYPE_CHECKING:
    from parsons.solidarity_tech.base import ParamsType
    from parsons.solidarity_tech.enums import InteractionType

logger = logging.getLogger(__name__)


class SolidarityTechUserNotes(SolidarityTechBase):
    """Methods for interacting with the SolidarityTech user notes endpoint."""

    def create_user_note(
        self,
        user_id: int,
        content: str,
        agent_id: int | None = None,
        created_at: int | None = None,
        restricted: bool = False,
        interaction_method: InteractionType | None = None,
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
            restricted:
                If True, the note is only visible to team members
                with the View Restricted Properties permission.
            interaction_method:
                Interaction type that produced the note.

        Raises:
            :class:`STFailedResponseError`: If the operation fails with a known error code.
            :class:`STUnexpectedResponseError`: If the operation fails with an unexpected status code.

        Returns:
            Boolean representing success of the operation.
            True if the operation was successful, False otherwise.

        Documentation Reference:
            `<https://www.solidarity.tech/reference/post_user-notes>`__

        """
        params: ParamsType = {
            "user_id": user_id,
            "content": content,
            "restricted": restricted,
        }
        self._add_if_field_not_empty(params, "agent_id", agent_id)
        self._add_if_field_not_empty(params, "created_at", created_at)
        self._add_if_field_not_empty(params, "interaction_method", interaction_method)

        res = self._post_request("user_notes", params=params)

        expected_responses = {
            201: (True, "user note created successfully"),
            404: (False, "unprocessable entity"),
            422: (False, "unprocessable entity"),
        }
        return self._handle_status_codes(res=res, codes=expected_responses)

    def delete_user_note(
        self,
        id: str,
        user_id: int,
        agent_id: int | None = None,
    ) -> bool:
        """
        Delete a user note with the specified ID.

        Args:
            id:
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
        params: ParamsType = {"user_id": user_id}
        self._add_if_field_not_empty(params, "agent_id", agent_id)

        res = self._del_request("user_notes", id, params=params)

        expected_responses = {
            200: (True, "user note deleted"),
            404: (False, "user note not found"),
        }
        return self._handle_status_codes(res=res, codes=expected_responses)
