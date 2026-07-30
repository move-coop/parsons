import logging

from requests.exceptions import HTTPError

from parsons.solidarity_tech.exceptions import STUnexpectedResponseCodeError
from parsons.solidarity_tech.solidarity_tech_base import SolidarityTechBase
from parsons.solidarity_tech.solidarity_tech_literals import InteractionType

logger = logging.getLogger(__name__)


class SolidarityTechUserNotes(SolidarityTechBase):
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

        Returns:
            Boolean representing success of the operation.
            True if the operation was successful, False otherwise.

        Raises:
            HTTPError: If the operation fails with a 422 status code.
            STUnexpectedResponseCodeError: If the operation fails with an unexpected status code.

        Documentation Reference:
            `<https://www.solidarity.tech/reference/post_user-notes>`__

        """
        params = {
            "user_id": user_id,
            "agent_id": agent_id,
            "content": content,
            "created_at": created_at,
            "restricted": restricted,
            "interaction_method": interaction_method,
        }
        res = self._post_request("user_notes", params=params)

        if res.status_code not in (201, 404, 422):
            raise STUnexpectedResponseCodeError(res)

        if res.status_code == 422:
            raise HTTPError(
                "Unprocessable request, perhaps interaction_method is invalid?", response=res
            )

        return res.status_code == 201

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

        Returns:
            Boolean representing success of the operation.
            True if the operation was successful, False otherwise.

        Raises:
            STUnexpectedResponseCodeError: If the operation fails with an unexpected status code.

        Documentation Reference:
            `<https://www.solidarity.tech/reference/delete_user-notes-id>`__

        """
        params = {"user_id": user_id, "agent_id": agent_id}
        res = self._del_request("user_notes", id, params=params)

        if res.status_code not in (200, 404):
            raise STUnexpectedResponseCodeError(res)

        return res.status_code == 200
