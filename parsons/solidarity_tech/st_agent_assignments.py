import logging
from datetime import datetime

import numpy as np

from parsons import Table
from parsons.solidarity_tech.solidarity_tech_base import SolidarityTechBase

logger = logging.getLogger(__name__)


class SolidarityTechAgentAssignments(SolidarityTechBase):
    def get_agent_assignments(
        self,
        limit: int = 20,
        offset: int = 0,
        since: int | datetime = 0,
        user_id: int | None = None,
        agent_user_id: int | None = None,
    ) -> Table:
        """
        Retrieve a list of agent assignments.

        Args:
            limit:
                Limits the number of items returned.
                Default is 20, maximum is 100.
            offset:
                Number of items to skip before starting to return the results.
            since:
                UTC timestamp in seconds since the Unix epoch to filter calls created after this time.
            user_id:
                User ID to filter agent assignments related to a specific user.
            agent_user_id:
                Agent User ID to filter agent user assignments related to a specific agent user.

        Raises:
            :class:`STFailedResponseError`: If the operation fails with a known error code.
            :class:`STUnexpectedResponseError`: If the operation fails with an unexpected status code.

        Returns:
            All the agent assignment entries.

        Documentation Reference:
            `<https://www.solidarity.tech/reference/get_agent-assignments>`__

        """
        params = {"user_id": user_id, "agent_user_id": agent_user_id}
        res = self._get_resources(
            "agent_assignments",
            limit=limit,
            offset=offset,
            since=since,
            params=params,
        )

        expected_responses = {200: (True, "successful")}
        self._handle_status_codes(res=res, codes=expected_responses)

        return Table(res.json())

    def get_agent_assignment(
        self,
        id: int,
    ) -> dict:
        """
        Retrieve a single agent assignment.

        Args:
            id:
                ID of the agent assignment to retrieve.

        Raises:
            :class:`STFailedResponseError`: If the operation fails with a known error code.
            :class:`STUnexpectedResponseError`: If the operation fails with an unexpected status code.

        Returns:
            A single agent assignment entry.

        Documentation Reference:
            `<https://www.solidarity.tech/reference/get_agent-assignments-id>`__

        """
        res = self._get_single_resource("agent_assignments", id)

        expected_responses = {
            200: (True, "agent assignment found"),
            404: (False, "agent assignment not found"),
        }
        self._handle_status_codes(res=res, codes=expected_responses)

        return res.json()

    def create_agent_assignment(
        self,
        user_id: np.int64,
        agent_user_id: np.int64,
        is_active: bool | None = None,
    ) -> bool:
        """
        Create an agent assignment with specified details.

        Args:
            user_id:
                Identifier for the user.
            agent_user_id:
                Identifier for the agent user.
            is_active:
                Whether the assignment is currently active.

        Raises:
            :class:`STFailedResponseError`: If the operation fails with a known error code.
            :class:`STUnexpectedResponseError`: If the operation fails with an unexpected status code.

        Returns:
            Boolean representing success of the operation.
            True if the operation was successful, False otherwise.

        Documentation Reference:
            `<https://www.solidarity.tech/reference/post_agent-assignments>`__

        """
        payload = {"user_id": user_id, "agent_user_id": agent_user_id, "is_active": is_active}
        res = self._post_request(
            "agent_assignments",
            payload=payload,
            additional_headers={"content-type": "application/json"},
        )

        expected_responses = {
            201: (True, "agent assignment created"),
            404: (False, "agent or user agent not in organization"),
        }
        return self._handle_status_codes(res=res, codes=expected_responses)

    def update_agent_assignment(
        self,
        id: int,
        user_id: np.int64,
        agent_user_id: np.int64,
        is_active: bool | None = None,
    ) -> bool:
        """
        Update an agent assignment with specified details.

        Args:
            id:
                Identifier for the agent assignment to update.
            user_id:
                Identifier for the user.
            agent_user_id:
                Identifier for the agent user.
            is_active:
                Whether the assignment is currently active.

        Raises:
            :class:`STFailedResponseError`: If the operation fails with a known error code.
            :class:`STUnexpectedResponseError`: If the operation fails with an unexpected status code.

        Returns:
            Boolean representing success of the operation.
            True if the operation was successful, False otherwise.

        Documentation Reference:
            `<https://www.solidarity.tech/reference/put_agent-assignments-id>`__

        """
        payload = {"user_id": user_id, "agent_user_id": agent_user_id, "is_active": is_active}
        res = self._put_request(
            "agent_assignments",
            id,
            payload=payload,
            additional_headers={"content-type": "application/json"},
        )

        expected_responses = {
            200: (True, "agent assignment updated"),
            404: (False, "agent assignment not found"),
            422: (False, "unprocessable entity"),
        }
        return self._handle_status_codes(res=res, codes=expected_responses)

    def delete_agent_assignment(
        self,
        id: int,
    ) -> bool:
        """
        Delete an agent assignment with specified ID.

        Args:
            id:
                Identifier for the agent assignment to update.

        Raises:
            :class:`STFailedResponseError`: If the operation fails with a known error code.
            :class:`STUnexpectedResponseError`: If the operation fails with an unexpected status code.

        Returns:
            Boolean representing success of the operation.
            True if the operation was successful, False otherwise.

        Documentation Reference:
            `<https://www.solidarity.tech/reference/delete_agent-assignments-id>`__

        """
        res = self._del_request("agent_assignments", id)

        expected_responses = {404: (False, "agent assignment not found")}
        return self._handle_status_codes(res=res, codes=expected_responses)
