"""Connector class for interacting with the SolidarityTech Scheduled Tasks endpoint."""

from __future__ import annotations

import logging
from datetime import datetime
from http import HTTPStatus
from typing import TYPE_CHECKING

from parsons import Table
from parsons.solidarity_tech.base import SolidarityTechBase

if TYPE_CHECKING:
    from parsons.solidarity_tech.datatypes import Metadata, ScheduledTaskData
    from parsons.utilities.api_connector import _JsonType

logger = logging.getLogger(__name__)


class SolidarityTechScheduledTasks(SolidarityTechBase):
    """Methods for interacting with the SolidarityTech scheduled tasks endpoint."""

    def get_scheduled_tasks(
        self,
        limit: int = 20,
        offset: int = 0,
        since: int | datetime = 0,
        user_id: int | None = None,
        agent_user_id: int | None = None,
    ) -> tuple[Table, Metadata]:
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
            A list of scheduled task entries, along with requested metadata.

        Documentation Reference:
            `<https://www.solidarity.tech/reference/get_scheduled-tasks>`__

        """
        params: dict[str, _JsonType] = {}
        _ = user_id is not None and params.update({"user_id": user_id})
        _ = agent_user_id is not None and params.update({"agent_user_id": agent_user_id})

        res = self._get_resources(
            "scheduled_tasks",
            limit=limit,
            offset=offset,
            since=since,
            params=params,
        )

        expected_responses = {HTTPStatus.OK: (True, "scheduled tasks listed")}
        self._handle_status_codes(res=res, codes=expected_responses)

        data: list[ScheduledTaskData] = res.json()["data"]
        meta: Metadata = res.json()["meta"]

        return Table(data, name="Solidarity Tech Scheduled Tasks"), meta

    def get_scheduled_task(
        self,
        resource_id: int,
    ) -> tuple[ScheduledTaskData, Metadata]:
        """
        Retrieve a single scheduled task.

        Args:
            resource_id:
                ID of the scheduled task to retrieve.

        Raises:
            :class:`STFailedResponseError`: If the operation fails with a known error code.
            :class:`STUnexpectedResponseError`: If the operation fails with an unexpected status code.

        Returns:
            A single scheduled task entry, along with requested metadata.

        Documentation Reference:
            `<https://www.solidarity.tech/reference/get_scheduled-tasks-id>`__

        """
        res = self._get_single_resource("scheduled_tasks", resource_id)

        expected_responses = {
            HTTPStatus.OK: (True, "scheduled task found"),
            HTTPStatus.NOT_FOUND: (False, "scheduled task not found"),
        }
        self._handle_status_codes(res=res, codes=expected_responses)

        return res.json()

    def create_scheduled_task(
        self,
        due_at: str | int | float | datetime,
        remind_at: str | int | float | datetime | None = None,
        agent_user_id: int | None = None,
        user_id: int | None = None,
        notes: str | None = None,
        *,
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
        if isinstance(due_at, datetime):
            due_at = due_at.timestamp()
        if isinstance(remind_at, datetime):
            remind_at = remind_at.timestamp()

        payload: dict[str, _JsonType] = {"due_at": due_at}
        _ = remind_at is not None and payload.update({"remind_at": remind_at})
        _ = agent_user_id is not None and payload.update({"agent_user_id": agent_user_id})
        _ = user_id is not None and payload.update({"user_id": user_id})
        _ = notes is not None and payload.update({"notes": notes})
        _ = marked_as_completed is not None and payload.update(
            {"marked_as_completed": marked_as_completed}
        )

        res = self._post_request(
            "scheduled_tasks",
            payload=payload,
            additional_headers={"content-type": "application/json"},
        )

        expected_responses = {
            HTTPStatus.CREATED: (True, "scheduled task created"),
            HTTPStatus.NOT_FOUND: (False, "agent or user agent not in organization"),
        }
        return self._handle_status_codes(res=res, codes=expected_responses)

    def update_scheduled_task(
        self,
        resource_id: int,
        due_at: str | int | float | datetime | None = None,
        remind_at: str | int | float | datetime | None = None,
        agent_user_id: int | None = None,
        user_id: int | None = None,
        notes: str | None = None,
        *,
        marked_as_completed: bool | None = None,
    ) -> bool:
        """
        Update a scheduled task with specified details.

        Args:
            resource_id:
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
        if isinstance(due_at, datetime):
            due_at = due_at.timestamp()
        if isinstance(remind_at, datetime):
            remind_at = remind_at.timestamp()

        payload: dict[str, _JsonType] = {}
        _ = due_at is not None and payload.update({"due_at": due_at})
        _ = remind_at is not None and payload.update({"remind_at": remind_at})
        _ = agent_user_id is not None and payload.update({"agent_user_id": agent_user_id})
        _ = user_id is not None and payload.update({"user_id": user_id})
        _ = notes is not None and payload.update({"notes": notes})
        _ = marked_as_completed is not None and payload.update(
            {"marked_as_completed": marked_as_completed}
        )

        res = self._put_request(
            "scheduled_tasks",
            resource_id,
            payload=payload,
            additional_headers={"content-type": "application/json"},
        )

        expected_responses = {
            HTTPStatus.OK: (True, "scheduled task updated"),
            HTTPStatus.NOT_FOUND: (False, "scheduled task not found"),
            HTTPStatus.UNPROCESSABLE_ENTITY: (False, "unprocessable entity"),
        }
        return self._handle_status_codes(res=res, codes=expected_responses)

    def delete_scheduled_task(
        self,
        resource_id: int,
    ) -> bool:
        """
        Delete a scheduled task with the specified ID.

        Args:
            resource_id:
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
        res = self._delete_request("scheduled_tasks", resource_id)

        expected_responses = {
            HTTPStatus.NOT_FOUND: (False, "scheduled task not found"),
        }
        return self._handle_status_codes(res=res, codes=expected_responses)
