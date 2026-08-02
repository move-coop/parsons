import logging
from datetime import datetime

from parsons import Table
from parsons.solidarity_tech.solidarity_tech_base import SolidarityTechBase

logger = logging.getLogger(__name__)

ActionData = dict[str, int | str]
ActivityData = dict[str, int | str | ActionData]
ActivityMetadata = dict[str, int]


class SolidarityTechActivities(SolidarityTechBase):
    def get_activities(
        self,
        limit: int = 20,
        cursor: int | None = None,
        since: int | datetime = 0,
        include_count: bool = False,
        user_id: int | None = None,
    ) -> tuple[Table, ActivityMetadata]:
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

        Raises:
            :class:`STFailedResponseError`: If the operation fails with a known error code.
            :class:`STUnexpectedResponseError`: If the operation fails with an unexpected status code.

        Returns:
            All the activities entries.

        Documentation Reference:
            `<https://www.solidarity.tech/reference/get_activities>`__

        """
        params = {"user_id": user_id}
        res = self._get_resources(
            "activities",
            limit=limit,
            cursor=cursor,
            since=since,
            include_count=include_count or None,
            params=params,
            additional_headers={"accept": "application/json"},
        )

        expected_responses = {200: (True, "successful")}
        self._handle_status_codes(res=res, codes=expected_responses)

        data: list[ActivityData] = res.json()["data"]
        meta: ActivityMetadata = res.json()["meta"]

        return Table(data), meta
