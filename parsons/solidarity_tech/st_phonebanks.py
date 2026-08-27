from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from parsons import Table
from parsons.solidarity_tech.base import SolidarityTechBase

if TYPE_CHECKING:
    from datetime import datetime

    from parsons.solidarity_tech.base import ParamsType

logger = logging.getLogger(__name__)


class SolidarityTechPhonebanks(SolidarityTechBase):
    """Methods for interacting with the SolidarityTech phonebanks endpoint."""

    def get_phonebanks(
        self,
        limit: int = 20,
        offset: int = 0,
        since: int | datetime = 0,
        event_id: int = 0,
        ids: list[int] | str | None = None,
        *,
        include_stats: bool = False,
    ) -> Table:
        """
        Retrieve a list of phonebanks.

        Args:
            limit:
                Limits the number of items returned.
                Default is 20, maximum is 100.
            offset:
                Number of items to skip before starting to return the results.
            since:
                UTC timestamp in seconds since the Unix epoch to filter calls created after this time.
            event_id:
                Filters phonebanks by event_id within the accessible scope.
            ids:
                Filters to specific phonebank ids.
                Accepts a comma-separated string (e.g. "12,34").
            include_stats:
                If True, each phonebank row also includes aggregate funnel numbers
                ``attempts`` (contact attempts), ``contacted`` (distinct people attempted),
                and ``reached`` (distinct people on answered calls).
                Default is False.

        Raises:
            :class:`STFailedResponseError`: If the operation fails with a known error code.
            :class:`STUnexpectedResponseError`: If the operation fails with an unexpected status code.

        Returns:
            All the phonebanks.

        Documentation Reference:
            `<https://www.solidarity.tech/reference/get_phonebanks>`__

        """
        if isinstance(ids, list):
            ids = ",".join(str(phonebank_id) for phonebank_id in ids)

        params: ParamsType = {"event_id": event_id, "include_stats": include_stats}
        self._add_if_field_not_empty(params, "ids", ids)

        res = self._get_resources(
            "phonebanks",
            limit=limit,
            offset=offset,
            since=since,
            params=params,
        )

        expected_responses = {200: (True, "phonebanks listed")}
        self._handle_status_codes(res=res, codes=expected_responses)

        return Table(res.json())

    def get_phonebank(
        self,
        resource_id: int,
    ) -> dict:
        """
        Retrieve a single phonebank.

        Args:
            resource_id:
                ID of the phonebank to retrieve.

        Raises:
            :class:`STFailedResponseError`: If the operation fails with a known error code.
            :class:`STUnexpectedResponseError`: If the operation fails with an unexpected status code.

        Returns:
            A single phonebank entry.

        Documentation Reference:
            `<https://www.solidarity.tech/reference/get_phonebanks-id>`__

        """
        res = self._get_single_resource("phonebanks", resource_id)

        expected_responses = {
            200: (True, "phonebank found"),
            404: (False, "phonebank not found"),
        }
        self._handle_status_codes(res=res, codes=expected_responses)

        return res.json()
