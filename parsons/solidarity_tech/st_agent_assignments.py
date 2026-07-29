import logging
from datetime import datetime

import numpy as np

from parsons.solidarity_tech.exceptions import STUnexpectedResponseCodeError
from parsons.solidarity_tech.solidarity_tech_base import SolidarityTechBase

logger = logging.getLogger(__name__)


class SolidarityTechAgentAssignments(SolidarityTechBase):
    def get_agent_assignments(
        self,
        limit: int = 20,
        offset: int = 0,
        since: int | datetime | None = 0,
        user_id: int | None = None,
        agent_user_id: int | None = None,
    ) -> str:
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

        if res.status_code not in (200, 404):
            raise STUnexpectedResponseCodeError(res)

        return res.text

    def get_agent_assignment(
        self,
        id: int,
    ) -> str:
        """
        Retrieve a single agent assignment.

        Args:
            id:
                ID of the agent assignment to retrieve.

        Returns:
            A single agent assignment entry.

        Raises:
            STUnexpectedResponseCodeError: If the operation fails with an unexpected status code.

        Documentation Reference:
            `<https://www.solidarity.tech/reference/get_agent-assignments-id>`__

        """
        res = self._get_single_resource("agent_assignments", id)

        if res.status_code not in (200, 404):
            raise STUnexpectedResponseCodeError(res)

        return res.text

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

        Returns:
            Boolean representing success of the operation.
            True if the operation was successful, False otherwise.

        Raises:
            STUnexpectedResponseCodeError: If the operation fails with an unexpected status code.

        Documentation Reference:
            `<https://www.solidarity.tech/reference/post_agent-assignments>`__

        """
        payload = {"user_id": user_id, "agent_user_id": agent_user_id, "is_active": is_active}
        res = self._post_request(
            "agent_assignments", payload, additional_headers={"content-type": "application/json"}
        )

        if res.status_code not in (201, 404):
            raise STUnexpectedResponseCodeError(res)

        return res.status_code == 201

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

        Returns:
            Boolean representing success of the operation.
            True if the operation was successful, False otherwise.

        Raises:
            STUnexpectedResponseCodeError: If the operation fails with an unexpected status code.

        Documentation Reference:
            `<https://www.solidarity.tech/reference/put_agent-assignments-id>`__

        """
        payload = {"user_id": user_id, "agent_user_id": agent_user_id, "is_active": is_active}
        res = self._put_request(
            "agent_assignments",
            id,
            payload,
            additional_headers={"content-type": "application/json"},
        )

        if res.status_code not in (200, 404, 422):
            raise STUnexpectedResponseCodeError(res)

        return res.status_code == 200

    def delete_agent_assignment(
        self,
        id: int,
    ) -> bool:
        """
        Delete an agent assignment with specified ID.

        Args:
            id:
                Identifier for the agent assignment to update.

        Returns:
            Boolean representing success of the operation.
            True if the operation was successful, False otherwise.

        Raises:
            STUnexpectedResponseCodeError: If the operation fails with an unexpected status code.

        Documentation Reference:
            `<https://www.solidarity.tech/reference/delete_agent-assignments-id>`__

        """
        res = self._del_request("agent_assignments", id)

        if res and res.status_code != 404:
            raise STUnexpectedResponseCodeError(res)

        return not res.status_code
