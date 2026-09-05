from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from parsons import Table
from parsons.solidarity_tech.base import SolidarityTechBase

if TYPE_CHECKING:
    from datetime import datetime

    from parsons.utilities.api_connector import _JsonType

logger = logging.getLogger(__name__)


class SolidarityTechTaskAgents(SolidarityTechBase):
    """Methods for interacting with the SolidarityTech task agents endpoint."""

    def get_task_agents(
        self,
        limit: int = 20,
        offset: int = 0,
        since: int | datetime = 0,
        task_id: int | None = None,
    ) -> Table:
        """
        Retrieve a list of task agents.

        Args:
            limit:
                Limits the number of items returned.
                Default is 20, maximum is 100.
            offset:
                Number of items to skip before starting to return the results.
            since:
                UTC timestamp in seconds since the Unix epoch to filter calls created after this time.
            task_id:
                Filters task agents by task within the accessible scope.

        Raises:
            :class:`STFailedResponseError`: If the operation fails with a known error code.
            :class:`STUnexpectedResponseError`: If the operation fails with an unexpected status code.

        Returns:
            All the task agent entries.

        Documentation Reference:
            `<https://www.solidarity.tech/reference/get_task-agents>`__

        """
        params: _JsonType = {}
        self._add_if_field_not_empty(params, "task_id", task_id)

        res = self._get_resources(
            "task_agents",
            limit=limit,
            offset=offset,
            since=since,
            params=params,
        )

        expected_responses = {200: (True, "task agents listed")}
        self._handle_status_codes(res=res, codes=expected_responses)

        return Table(res.json())

    def get_task_agent(
        self,
        resource_id: int,
    ) -> dict:
        """
        Retrieve a single task agent.

        Args:
            resource_id:
                ID of the task agent to retrieve.

        Raises:
            :class:`STFailedResponseError`: If the operation fails with a known error code.
            :class:`STUnexpectedResponseError`: If the operation fails with an unexpected status code.

        Returns:
            A single task agent entry.

        Documentation Reference:
            `<https://www.solidarity.tech/reference/get_task-agents-id>`__

        """
        res = self._get_single_resource("task_agents", resource_id)

        expected_responses = {
            200: (True, "task agent found"),
            404: (False, "task agent not found"),
        }
        self._handle_status_codes(res=res, codes=expected_responses)

        return res.json()

    def create_task_agent(
        self,
        user_id: int,
        task_id: int,
    ) -> bool:
        """
        Create an task agent with specified details.

        Args:
            user_id:
                Identifier for the task agent.
            task_id:
                Identifier for the task.

        Raises:
            :class:`STFailedResponseError`: If the operation fails with a known error code.
            :class:`STUnexpectedResponseError`: If the operation fails with an unexpected status code.

        Returns:
            Boolean representing success of the operation.
            True if the operation was successful, False otherwise.

        Documentation Reference:
            `<https://www.solidarity.tech/reference/post_task-agents>`__

        """
        payload: dict[str, Any] = {"user_id": user_id, "task_id": task_id}

        res = self._post_request(
            "task_agents", payload=payload, additional_headers={"content-type": "application/json"}
        )

        expected_responses = {201: (True, "task agent created")}
        return self._handle_status_codes(res=res, codes=expected_responses)

    def delete_task_agent(
        self,
        resource_id: int,
    ) -> bool:
        """
        Delete a task agent with the specified ID.

        Args:
            resource_id:
                Identifier for the task agent to delete.

        Raises:
            :class:`STFailedResponseError`: If the operation fails with a known error code.
            :class:`STUnexpectedResponseError`: If the operation fails with an unexpected status code.

        Returns:
            Boolean representing success of the operation.
            True if the operation was successful, False otherwise.

        Documentation Reference:
            `<https://www.solidarity.tech/reference/delete_task-agents-id>`__

        """
        res = self._del_request("task_agents", resource_id)

        expected_responses = {404: (False, "task agent not found")}
        return self._handle_status_codes(res=res, codes=expected_responses)
