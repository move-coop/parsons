import logging
from datetime import datetime

import numpy as np

from parsons import Table
from parsons.solidarity_tech.solidarity_tech_base import SolidarityTechBase

logger = logging.getLogger(__name__)


class SolidarityTechTaskAgents(SolidarityTechBase):
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
        params = {"task_id": task_id}
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
        id: int,
    ) -> dict:
        """
        Retrieve a single task agent.

        Args:
            id:
                ID of the task agent to retrieve.

        Raises:
            :class:`STFailedResponseError`: If the operation fails with a known error code.
            :class:`STUnexpectedResponseError`: If the operation fails with an unexpected status code.

        Returns:
            A single task agent entry.

        Documentation Reference:
            `<https://www.solidarity.tech/reference/get_task-agents-id>`__

        """
        res = self._get_single_resource("task_agents", id)

        expected_responses = {
            200: (True, "task agent found"),
            404: (False, "task agent not found"),
        }
        self._handle_status_codes(res=res, codes=expected_responses)

        return res.json()

    def create_task_agent(
        self,
        user_id: np.int64,
        task_id: np.int64,
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
        payload = {
            "user_id": user_id,
            "task_id": task_id,
        }
        res = self._post_request(
            "task_agents", payload=payload, additional_headers={"content-type": "application/json"}
        )

        expected_responses = {201: (True, "task agent created")}
        return self._handle_status_codes(res=res, codes=expected_responses)

    def delete_task_agent(
        self,
        id: int,
    ) -> bool:
        """
        Delete a task agent with the specified ID.

        Args:
            id:
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
        res = self._del_request("task_agents", id)

        expected_responses = {404: (False, "task agent not found")}
        return self._handle_status_codes(res=res, codes=expected_responses)
