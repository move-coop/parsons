import logging
from datetime import datetime

import numpy as np

from parsons import Table
from parsons.solidarity_tech.solidarity_tech_base import SolidarityTechBase

logger = logging.getLogger(__name__)


class SolidarityTechScheduledTasks(SolidarityTechBase):
    def get_scheduled_tasks(
        self,
        limit: int = 20,
        offset: int = 0,
        since: int | datetime = 0,
        user_id: int | None = None,
        agent_user_id: int | None = None,
    ) -> Table:
        """
        Retrieve a list of scheduled tasks.

        Args:
            limit:
                Limits the number of items returned.
                Default is 20, maximum is 100.
            offset:
                Number of items to skip before starting to return the results.
            since:
                UTC timestamp in seconds since the Unix epoch to filter calls created after this time.
            user_id:
                User ID to filter scheduled tasks related to a specific user.
            agent_user_id:
                Agent User ID to filter agent user assignments related to a specific agent user.

        Raises:
            :class:`STFailedResponseError`: If the operation fails with a known error code.
            :class:`STUnexpectedResponseError`: If the operation fails with an unexpected status code.

        Returns:
            All the scheduled task entries.

        Documentation Reference:
            `<https://www.solidarity.tech/reference/get_scheduled-tasks>`__

        """
        params = {"user_id": user_id, "agent_user_id": agent_user_id}
        res = self._get_resources(
            "scheduled_tasks",
            limit=limit,
            offset=offset,
            since=since,
            params=params,
        )

        expected_responses = {200: (True, "scheduled tasks listed")}
        self._handle_status_codes(res=res, codes=expected_responses)

        return Table(res.json())

    def get_scheduled_task(
        self,
        id: int,
    ) -> dict:
        """
        Retrieve a single scheduled task.

        Args:
            id:
                ID of the scheduled task to retrieve.

        Raises:
            :class:`STFailedResponseError`: If the operation fails with a known error code.
            :class:`STUnexpectedResponseError`: If the operation fails with an unexpected status code.

        Returns:
            A single scheduled task entry.

        Documentation Reference:
            `<https://www.solidarity.tech/reference/get_scheduled-tasks-id>`__

        """
        res = self._get_single_resource("scheduled_tasks", id)

        expected_responses = {
            200: (True, "scheduled task found"),
            404: (False, "scheduled task not found"),
        }
        self._handle_status_codes(res=res, codes=expected_responses)

        return res.json()

    def create_scheduled_task(
        self,
        due_at: str | int | datetime,
        remind_at: str | int | datetime | None = None,
        agent_user_id: np.int64 | None = None,
        user_id: np.int64 | None = None,
        notes: str | None = None,
        marked_as_completed: bool | None = None,
    ) -> bool:
        """
        Create an scheduled task with specified details.

        Args:
            due_at:
                The date and time when the task is due.
                Accepts either an ISO 8601 formatted date-time string
                or a UNIX timestamp as a string or integer.
            remind_at:
                The date and time when a reminder for the task should be sent.
                Accepts either an ISO 8601 formatted date-time string
                or a UNIX timestamp as a string or integer.
            agent_user_id:
                Identifier for the agent user assigned to the task.
            user_id:
                Identifier for the user who created the task.
            ``notes``:
                Additional notes or details about the task.
            marked_as_completed:
                Indicates if the task has been marked as completed.

        Raises:
            :class:`STFailedResponseError`: If the operation fails with a known error code.
            :class:`STUnexpectedResponseError`: If the operation fails with an unexpected status code.

        Returns:
            Boolean representing success of the operation.
            True if the operation was successful, False otherwise.

        Documentation Reference:
            `<https://www.solidarity.tech/reference/post_scheduled-tasks>`__

        """
        payload = {
            "due_at": due_at.timestamp() if isinstance(due_at, datetime) else due_at,
            "remind_at": remind_at.timestamp() if isinstance(remind_at, datetime) else remind_at,
            "agent_user_id": agent_user_id,
            "user_id": user_id,
            "notes": notes,
            "marked_as_completed": marked_as_completed,
        }
        res = self._post_request(
            "scheduled_tasks",
            payload=payload,
            additional_headers={"content-type": "application/json"},
        )

        expected_responses = {
            201: (True, "scheduled task created"),
            404: (False, "agent or user agent not in organization"),
        }
        return self._handle_status_codes(res=res, codes=expected_responses)

    def update_scheduled_task(
        self,
        id: int,
        due_at: str | int | datetime | None = None,
        remind_at: str | int | datetime | None = None,
        agent_user_id: np.int64 | None = None,
        user_id: np.int64 | None = None,
        notes: str | None = None,
        marked_as_completed: bool | None = None,
    ) -> bool:
        """
        Update a scheduled task with specified details.

        Args:
            id:
                Identifier for the scheduled task to update.
            due_at:
                The date and time when the task is due.
                Accepts either an ISO 8601 formatted date-time string
                or a UNIX timestamp as a string or integer.
            remind_at:
                Reminder time for the task.
            agent_user_id:
                Identifier for the agent user.
            user_id:
                Identifier for the user.
            ``notes``:
                Additional notes or details about the task.
            marked_as_completed:
                Indicates if the task has been marked as completed.

        Raises:
            :class:`STFailedResponseError`: If the operation fails with a known error code.
            :class:`STUnexpectedResponseError`: If the operation fails with an unexpected status code.

        Returns:
            Boolean representing success of the operation.
            True if the operation was successful, False otherwise.

        Documentation Reference:
            `<https://www.solidarity.tech/reference/put_scheduled-tasks-id>`__

        """
        payload = {
            "due_at": due_at.timestamp() if isinstance(due_at, datetime) else due_at,
            "remind_at": remind_at.timestamp() if isinstance(remind_at, datetime) else remind_at,
            "agent_user_id": agent_user_id,
            "user_id": user_id,
            "notes": notes,
            "marked_as_completed": marked_as_completed,
        }
        res = self._put_request(
            "scheduled_tasks",
            id,
            payload=payload,
            additional_headers={"content-type": "application/json"},
        )

        expected_responses = {
            200: (True, "scheduled task updated"),
            404: (False, "scheduled task not found"),
            422: (False, "unprocessable entity"),
        }
        return self._handle_status_codes(res=res, codes=expected_responses)

    def delete_scheduled_task(
        self,
        id: int,
    ) -> bool:
        """
        Delete a scheduled task with the specified ID.

        Args:
            id:
                Identifier for the scheduled task to delete.

        Raises:
            :class:`STFailedResponseError`: If the operation fails with a known error code.
            :class:`STUnexpectedResponseError`: If the operation fails with an unexpected status code.

        Returns:
            Boolean representing success of the operation.
            True if the operation was successful, False otherwise.

        Documentation Reference:
            `<https://www.solidarity.tech/reference/delete_scheduled-tasks-id>`__

        """
        res = self._del_request("scheduled_tasks", id)

        expected_responses = {404: (False, "scheduled task not found")}
        return self._handle_status_codes(res=res, codes=expected_responses)
