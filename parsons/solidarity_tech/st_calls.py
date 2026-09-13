"""Connector class for interacting with the SolidarityTech Calls endpoint."""

from __future__ import annotations

import logging
from http import HTTPStatus
from typing import TYPE_CHECKING

from parsons import Table
from parsons.solidarity_tech.base import SolidarityTechBase

if TYPE_CHECKING:
    from datetime import datetime

    from parsons.solidarity_tech.datatypes import CallData, Metadata
    from parsons.utilities.api_connector import _JsonType

logger = logging.getLogger(__name__)


class SolidarityTechCalls(SolidarityTechBase):
    """Methods for interacting with the SolidarityTech calls endpoint."""

    def get_calls(
        self,
        user_id: int | None = None,
        limit: int = 20,
        offset: int = 0,
        since: int | datetime = 0,
    ) -> tuple[Table, Metadata]:
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
        params: dict[str, _JsonType] = {"user_id": user_id}

        res = self._get_resources(
            "calls",
            limit=limit,
            offset=offset,
            since=since,
            params=params,
            additional_headers={"accept": "application/json"},
        )

        expected_responses = {HTTPStatus.OK: (True, "successful")}
        self._handle_status_codes(res=res, codes=expected_responses)

        data: list[CallData] = res.json()["data"]
        meta: Metadata = res.json()["meta"]

        return Table(data, name="Solidarity Tech Calls"), meta
