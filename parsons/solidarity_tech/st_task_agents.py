import logging
from datetime import datetime

import numpy as np

from parsons.solidarity_tech.exceptions import STUnexpectedResponseCodeError
from parsons.solidarity_tech.solidarity_tech_base import SolidarityTechBase

logger = logging.getLogger(__name__)


class SolidarityTechTaskAgents(SolidarityTechBase):
    def get_task_agents(
        self,
        limit: int = 20,
        offset: int = 0,
        since: int | datetime | None = 0,
        task_id: int | None = None,
    ) -> str:
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

        if res.status_code != 200:
            raise STUnexpectedResponseCodeError(res)

        return res.text

    def get_task_agent(
        self,
        id: int,
    ) -> str:
        """
        Retrieve a single task agent.

        Args:
            id:
                ID of the task agent to retrieve.

        Returns:
            A single task agent entry.

        Raises:
            STUnexpectedResponseCodeError: If the operation fails with an unexpected status code.

        Documentation Reference:
            `<https://www.solidarity.tech/reference/get_task-agents-id>`__

        """
        res = self._get_single_resource("task_agents", id)

        if res.status_code not in (200, 404):
            raise STUnexpectedResponseCodeError(res)

        return res.text

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

        Returns:
            Boolean representing success of the operation.
            True if the operation was successful, False otherwise.

        Raises:
            STUnexpectedResponseCodeError: If the operation fails with an unexpected status code.

        Documentation Reference:
            `<https://www.solidarity.tech/reference/post_task-agents>`__

        """
        payload = {
            "user_id": user_id,
            "task_id": task_id,
        }
        res = self._post_request(
            "task_agents", payload, additional_headers={"content-type": "application/json"}
        )

        if res.status_code not in (201, 404):
            raise STUnexpectedResponseCodeError(res)

        return res.status_code == 201

    def delete_task_agent(
        self,
        id: int,
    ) -> bool:
        """
        Delete a task agent with the specified ID.

        Args:
            id:
                Identifier for the task agent to delete.

        Returns:
            Boolean representing success of the operation.
            True if the operation was successful, False otherwise.

        Raises:
            STUnexpectedResponseCodeError: If the operation fails with an unexpected status code.

        Documentation Reference:
            `<https://www.solidarity.tech/reference/delete_task-agents-id>`__

        """
        res = self._del_request("task_agents", id)

        if res and res.status_code != 404:
            raise STUnexpectedResponseCodeError(res)

        return not res.status_code
