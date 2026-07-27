import logging
from datetime import datetime

from parsons.solidarity_tech.solidarity_tech_base import SolidarityTechBase
from parsons.solidarity_tech.solidarity_tech_exceptions import STUnexpectedResponseCodeError

logger = logging.getLogger(__name__)


class SolidarityTechActivities(SolidarityTechBase):
    def get_activities(
        self,
        limit: int = 20,
        cursor: int | None = None,
        since: int | datetime | None = 0,
        include_count: bool = False,
        user_id: int | None = None,
    ) -> str:
        """
        Retrieve a list of activities.

        Args:
            limit:
                Limits the number of items returned.
                Default is 20, maximum is 100.
            cursor:
                Keyset pagination cursor.
                Pass the meta.next_cursor value from the previous response to fetch the next (older) page.
                This is the recommended way to paginate; it stays fast at any depth.
                Records are returned newest first (descending id).
            since:
                UTC timestamp in seconds since the Unix epoch to filter calls created after this time.
            include_count:
                When true, meta.total_count is populated with the full result count.
                Off by default because counting an entire history is expensive.
                Omit it for normal paging.
            user_id:
                User ID to filter activities for a specific user.

        Returns:
            All the activities entries.

        Raises:
            STUnexpectedResponseCodeError: If the operation fails with an unexpected status code.

        Documentation Reference:
            `<https://www.solidarity.tech/reference/get_activities>`__

        """
        res = self._get_resources(
            "activities",
            limit=limit,
            cursor=cursor,
            since=since,
            include_count=include_count or None,
            user_id=user_id,
            additional_headers={"accept": "application/json"},
        )

        if res.status_code != 200:
            raise STUnexpectedResponseCodeError(res)

        return res.text
