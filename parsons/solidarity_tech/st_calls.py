import logging
from datetime import datetime

from parsons.solidarity_tech.exceptions import STUnexpectedResponseCodeError
from parsons.solidarity_tech.solidarity_tech_base import SolidarityTechBase

logger = logging.getLogger(__name__)


class SolidarityTechCalls(SolidarityTechBase):
    def get_calls(
        self,
        user_id: int | None = None,
        limit: int = 20,
        offset: int = 0,
        since: int | datetime | None = 0,
    ) -> str:
        """
        Retrieve a list of calls.

        Args:
            user_id:
                User ID to filter calls related to a specific user.
            limit:
                Limits the number of items returned.
                Default is 20, maximum is 100.
            offset:
                Number of items to skip before starting to return the results.
            since:
                UTC timestamp in seconds since the Unix epoch to filter calls created after this time.

        Returns:
            All the calls entries.

        Raises:
            STUnexpectedResponseCodeError: If the operation fails with an unexpected status code.

        Documentation Reference:
            `<https://www.solidarity.tech/reference/get_calls>`__

        """
        res = self._get_resources(
            "calls",
            user_id=user_id,
            limit=limit,
            offset=offset,
            since=since,
            additional_headers={"accept": "application/json"},
        )

        if res.status_code != 200:
            raise STUnexpectedResponseCodeError(res)

        return res.text
