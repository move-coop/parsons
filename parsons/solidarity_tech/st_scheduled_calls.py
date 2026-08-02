import logging
from datetime import datetime

from parsons import Table
from parsons.solidarity_tech.solidarity_tech_base import SolidarityTechBase

logger = logging.getLogger(__name__)


class SolidarityTechScheduledCalls(SolidarityTechBase):
    def get_scheduled_calls(
        self,
        limit: int = 20,
        offset: int = 0,
        since: int | datetime = 0,
        user_id: int | None = None,
        agent_user_id: int | None = None,
    ) -> Table:
        """
        Retrieve a list of scheduled calls.

        Args:
            limit:
                Limits the number of items returned.
                Default is 20, maximum is 100.
            offset:
                Number of items to skip before starting to return the results.
            since:
                UTC timestamp in seconds since the Unix epoch to filter calls created after this time.
            user_id:
                User ID to filter scheduled calls related to a specific user.
            agent_user_id:
                Agent User ID to filter agent user assignments related to a specific agent user.

        Raises:
            :class:`STFailedResponseError`: If the operation fails with a known error code.
            :class:`STUnexpectedResponseError`: If the operation fails with an unexpected status code.

        Returns:
            All the scheduled calls.

        Documentation Reference:
            `<https://www.solidarity.tech/reference/get_scheduled-calls>`__

        """
        params = {"user_id": user_id, "agent_user_id": agent_user_id}
        res = self._get_resources(
            "scheduled_calls",
            limit=limit,
            offset=offset,
            since=since,
            params=params,
        )

        expected_responses = {200: (True, "scheduled calls listed")}
        self._handle_status_codes(res=res, codes=expected_responses)

        return Table(res.json())

    def get_scheduled_call(
        self,
        id: int,
    ) -> dict:
        """
        Retrieve a single scheduled call.

        Args:
            id:
                ID of the scheduled call to retrieve.

        Raises:
            :class:`STFailedResponseError`: If the operation fails with a known error code.
            :class:`STUnexpectedResponseError`: If the operation fails with an unexpected status code.

        Returns:
            A single scheduled call entry.

        Documentation Reference:
            `<https://www.solidarity.tech/reference/get_scheduled-calls-id>`__

        """
        res = self._get_single_resource("scheduled_calls", id)

        expected_responses = {
            200: (True, "scheduled call found"),
            404: (False, "scheduled call not found"),
        }
        self._handle_status_codes(res=res, codes=expected_responses)

        return res.json()
