import logging
from datetime import datetime

from requests import HTTPError

from parsons.solidarity_tech.exceptions import STUnexpectedResponseCodeError
from parsons.solidarity_tech.solidarity_tech_base import SolidarityTechBase

logger = logging.getLogger(__name__)


class SolidarityTechScheduledCalls(SolidarityTechBase):
    def get_scheduled_calls(
        self,
        limit: int = 20,
        offset: int = 0,
        since: int | datetime | None = 0,
        user_id: int | None = None,
        agent_user_id: int | None = None,
    ) -> str:
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

        if res.status_code != 200:
            raise STUnexpectedResponseCodeError(res)

        return res.text

    def get_scheduled_call(
        self,
        id: int,
    ) -> str:
        """
        Retrieve a single scheduled call.

        Args:
            id:
                ID of the scheduled call to retrieve.

        Returns:
            A single scheduled call entry.

        Raises:
            HTTPError: If the scheduled call is not found.
            STUnexpectedResponseCodeError: If the operation fails with an unexpected status code.

        Documentation Reference:
            `<https://www.solidarity.tech/reference/get_scheduled-calls-id>`__

        """
        res = self._get_single_resource("scheduled_calls", id)

        if res and res.status_code != 404:
            raise STUnexpectedResponseCodeError(res)

        if res.status_code == 404:
            raise HTTPError("Scheduled call not found.", response=res)

        return res.text
