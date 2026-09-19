"""Connector class for interacting with the SolidarityTech Scheduled Calls endpoint."""

from __future__ import annotations

import logging
from http import HTTPStatus
from typing import TYPE_CHECKING

from parsons import Table
from parsons.solidarity_tech.base import SolidarityTechBase

if TYPE_CHECKING:
    from datetime import datetime

    from parsons.solidarity_tech.datatypes import Metadata, ScheduledCallData
    from parsons.utilities.api_connector import _JsonType

logger = logging.getLogger(__name__)


class SolidarityTechScheduledCalls(SolidarityTechBase):
    """Methods for interacting with the SolidarityTech scheduled calls endpoint."""

    def get_scheduled_calls(
        self,
        limit: int = 20,
        offset: int = 0,
        since: int | datetime = 0,
        user_id: int | None = None,
        agent_user_id: int | None = None,
    ) -> tuple[Table, Metadata]:
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
            A list of scheduled call entries, along with requested metadata.

        Documentation Reference:
            `<https://www.solidarity.tech/reference/get_scheduled-calls>`__

        """
        params: dict[str, _JsonType] = {}
        _ = user_id is not None and params.update({"user_id": user_id})
        _ = agent_user_id is not None and params.update({"agent_user_id": agent_user_id})

        res = self._get_resources(
            "scheduled_calls",
            limit=limit,
            offset=offset,
            since=since,
            params=params,
        )

        expected_responses = {HTTPStatus.OK: (True, "scheduled calls listed")}
        self._handle_status_codes(res=res, codes=expected_responses)

        data: list[ScheduledCallData] = res.json()["data"]
        meta: Metadata = res.json()["meta"]

        return Table(data, name="Solidarity Tech Scheduled Calls"), meta

    def get_scheduled_call(
        self,
        resource_id: int,
    ) -> tuple[ScheduledCallData, Metadata]:
        """
        Retrieve a single scheduled call.

        Args:
            resource_id:
                ID of the scheduled call to retrieve.

        Raises:
            :class:`STFailedResponseError`: If the operation fails with a known error code.
            :class:`STUnexpectedResponseError`: If the operation fails with an unexpected status code.

        Returns:
            A single scheduled call entry, along with requested metadata.

        Documentation Reference:
            `<https://www.solidarity.tech/reference/get_scheduled-calls-id>`__

        """
        res = self._get_single_resource("scheduled_calls", resource_id)

        expected_responses = {
            HTTPStatus.OK: (True, "scheduled call found"),
            HTTPStatus.NOT_FOUND: (False, "scheduled call not found"),
        }
        self._handle_status_codes(res=res, codes=expected_responses)

        data: ScheduledCallData = res.json()["data"]
        meta: Metadata = res.json()["meta"]

        return data, meta
