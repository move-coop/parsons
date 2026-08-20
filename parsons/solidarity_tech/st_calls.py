from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from parsons import Table
from parsons.solidarity_tech.base import SolidarityTechBase

if TYPE_CHECKING:
    from datetime import datetime

    from parsons.solidarity_tech.base import ParamsType

logger = logging.getLogger(__name__)

TranscriptData = dict[str, str | int]
CallData = dict[str, int | str | bool | TranscriptData]
CallMetadata = dict[str, int]


class SolidarityTechCalls(SolidarityTechBase):
    def get_calls(
        self,
        user_id: int | None = None,
        limit: int = 20,
        offset: int = 0,
        since: int | datetime = 0,
    ) -> tuple[Table, CallMetadata]:
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

        Raises:
            :class:`STFailedResponseError`: If the operation fails with a known error code.
            :class:`STUnexpectedResponseError`: If the operation fails with an unexpected status code.

        Returns:
            All the calls entries.

        Documentation Reference:
            `<https://www.solidarity.tech/reference/get_calls>`__

        """
        params: ParamsType = {"user_id": user_id}

        res = self._get_resources(
            "calls",
            limit=limit,
            offset=offset,
            since=since,
            params=params,
            additional_headers={"accept": "application/json"},
        )

        expected_responses = {200: (True, "successful")}
        self._handle_status_codes(res=res, codes=expected_responses)

        data: list[CallData] = res.json()["data"]
        meta: CallMetadata = res.json()["meta"]

        return Table(data), meta
