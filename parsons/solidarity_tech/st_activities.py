from __future__ import annotations

import logging
from typing import TYPE_CHECKING, TypedDict

from parsons import Table
from parsons.solidarity_tech.base import SolidarityTechBase

if TYPE_CHECKING:
    from datetime import datetime

    from parsons.solidarity_tech.base import ParamsType

logger = logging.getLogger(__name__)


class ActionData(TypedDict):
    id: int
    user_id: int
    agent_user_id: int | None
    field_type: str | None
    old_value: str | None
    new_value: str | None
    data_import_id: int | None
    created_at: str
    updated_at: str


class ActivityData(TypedDict):
    id: int
    user_id: int
    name: str
    actionable_id: int
    actionable_type: str
    action: ActionData
    created_at: str
    updated_at: str


class ActivityMetadata(TypedDict):
    total_count: int | None
    limit: int
    offset: int
    cursor: int | None
    next_cursor: int | None


class SolidarityTechActivities(SolidarityTechBase):
    """Methods for interacting with the SolidarityTech activities endpoint."""

    def get_activities(
        self,
        limit: int = 20,
        cursor: int | None = None,
        since: int | datetime = 0,
        user_id: int | None = None,
        *,
        include_count: bool = False,
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
            user_id:
                User ID to filter activities for a specific user.
            include_count:
                When true, meta.total_count is populated with the full result count.
                Off by default because counting an entire history is expensive.
                Omit it for normal paging.

        Raises:
            :class:`STFailedResponseError`: If the operation fails with a known error code.
            :class:`STUnexpectedResponseError`: If the operation fails with an unexpected status code.

        Returns:
            All the activities entries, along with request metadata.

        Documentation Reference:
            `<https://www.solidarity.tech/reference/get_activities>`__

        """
        params: ParamsType = {}
        self._add_if_field_not_empty(params, "user_id", user_id)

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
