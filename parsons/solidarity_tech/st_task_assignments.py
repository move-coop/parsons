import logging
from datetime import datetime

import numpy as np

from parsons import Table
from parsons.solidarity_tech.solidarity_tech_base import SolidarityTechBase

logger = logging.getLogger(__name__)


class SolidarityTechTaskAssignments(SolidarityTechBase):
    def get_task_assignments(
        self,
        limit: int = 20,
        offset: int = 0,
        since: int | datetime = 0,
        task_id: int = 0,
        agent_user_id: int = 0,
    ) -> Table:
        """
        Retrieve a list of task assignments.

        Args:
            limit:
                Limits the number of items returned.
                Default is 20, maximum is 100.
            offset:
                Number of items to skip before starting to return the results.
            since:
                UTC timestamp in seconds since the Unix epoch to filter calls created after this time.
            task_id:
                Filters task assignments by phonebank or textbank task within the accessible scope.
            agent_user_id:
                Filters task assignments by agent user within the accessible scope.

        Raises:
            :class:`STFailedResponseError`: If the operation fails with a known error code.
            :class:`STUnexpectedResponseError`: If the operation fails with an unexpected status code.

        Returns:
            All the task assignment entries.

        Documentation Reference:
            `<https://www.solidarity.tech/reference/get_task-assignments>`__

        """
        params = {"task_id": task_id, "agent_user_id": agent_user_id}
        res = self._get_resources(
            "task_assignments",
            limit=limit,
            offset=offset,
            since=since,
            params=params,
        )

        expected_responses = {200: (True, "task assignments listed")}
        self._handle_status_codes(res=res, codes=expected_responses)

        return Table(res.json())

    def get_task_assignment(
        self,
        id: int,
    ) -> dict:
        """
        Retrieve a single task assignment.

        Args:
            id:
                ID of the task assignment to retrieve.

        Raises:
            :class:`STFailedResponseError`: If the operation fails with a known error code.
            :class:`STUnexpectedResponseError`: If the operation fails with an unexpected status code.

        Returns:
            A single task assignment entry.

        Documentation Reference:
            `<https://www.solidarity.tech/reference/get_task-assignments-id>`__

        """
        res = self._get_single_resource("task_assignments", id)

        expected_responses = {
            200: (True, "task assignment found"),
            404: (False, "task assignment not found"),
        }
        self._handle_status_codes(res=res, codes=expected_responses)

        return res.json()

    def create_task_assignment(
        self,
        user_id: np.int64,
        task_id: np.int64,
        agent_user_id: np.int64 | None = None,
    ) -> bool:
        """
        Create a task assignment.

        Assigns a user to participate in a phonebank or textbank campaign.

        Args:
            user_id:
                Identifier for the task assignment user.
            task_id:
                Identifier for the phonebank or textbank task.
            agent_user_id:
                Identifier for the agent user who will conduct outreach (volunteer or staff member).

        Raises:
            :class:`STFailedResponseError`: If the operation fails with a known error code.
            :class:`STUnexpectedResponseError`: If the operation fails with an unexpected status code.

        Returns:
            Boolean representing success of the operation.
            True if the operation was successful, False otherwise.

        Documentation Reference:
            `<https://www.solidarity.tech/reference/post_task-assignments>`__

        """
        payload = {
            "user_id": user_id,
            "task_id": task_id,
            "agent_user_id": agent_user_id,
        }
        res = self._post_request(
            "task_assignments",
            payload=payload,
            additional_headers={"content-type": "application/json"},
        )

        expected_responses = {201: (True, "task assignment created")}
        return self._handle_status_codes(res=res, codes=expected_responses)

    def update_task_assignment(
        self,
        id: int,
        agent_user_id: np.int64 | None = None,
    ) -> bool:
        """
        Update an task assignment with the specified details.

        Args:
            id:
                Identifier of the task assignment to update.
            agent_user_id:
                Identifier for the agent user, if applicable.

        Raises:
            :class:`STFailedResponseError`: If the operation fails with a known error code.
            :class:`STUnexpectedResponseError`: If the operation fails with an unexpected status code.

        Returns:
            Boolean representing success of the operation.
            True if the operation was successful, False otherwise.

        Documentation Reference:
            `<https://www.solidarity.tech/reference/put_task-assignments-id>`__

        """
        payload = {
            "agent_user_id": agent_user_id,
        }
        res = self._put_request(
            "scheduled_tasks",
            id,
            payload=payload,
            additional_headers={"content-type": "application/json"},
        )

        expected_responses = {
            200: (True, "task assignment updated"),
            404: (False, "event rsvp not found"),
        }
        return self._handle_status_codes(res=res, codes=expected_responses)

    def delete_task_assignment(
        self,
        id: int,
    ) -> bool:
        """
        Delete a task assignment with the specified ID.

        Args:
            id:
                Identifier of the task assignment to delete.

        Raises:
            :class:`STFailedResponseError`: If the operation fails with a known error code.
            :class:`STUnexpectedResponseError`: If the operation fails with an unexpected status code.

        Returns:
            Boolean representing success of the operation.
            True if the operation was successful, False otherwise.

        Documentation Reference:
            `<https://www.solidarity.tech/reference/put_task-assignments-id>`__

        """
        res = self._del_request("task_assignments", id)

        expected_responses = {404: (False, "task assignment not found")}
        return self._handle_status_codes(res=res, codes=expected_responses)
