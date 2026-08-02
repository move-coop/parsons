import logging
from datetime import datetime

from parsons import Table
from parsons.solidarity_tech.solidarity_tech_base import SolidarityTechBase

logger = logging.getLogger(__name__)


class SolidarityTechTextbanks(SolidarityTechBase):
    def get_textbanks(
        self,
        limit: int = 20,
        offset: int = 0,
        since: int | datetime = 0,
        event_id: int = 0,
        ids: list[int] | str | None = None,
        include_stats: bool = False,
    ) -> Table:
        """
        Retrieve a list of textbanks.

        Args:
            limit:
                Limits the number of items returned.
                Default is 20, maximum is 100.
            offset:
                Number of items to skip before starting to return the results.
            since:
                UTC timestamp in seconds since the Unix epoch to filter calls created after this time.
            event_id:
                Filters textbanks by event_id within the accessible scope.
            ids:
                Filters to specific textbank ids.
                Accepts a comma-separated string (e.g. "12,34").
            include_stats:
                If True, each textbank row also includes aggregate funnel numbers
                ``attempts`` (contact attempts), ``contacted`` (distinct people attempted),
                and ``replies`` (distinct attempts that got a response).
                Default is False.

        Raises:
            :class:`STFailedResponseError`: If the operation fails with a known error code.
            :class:`STUnexpectedResponseError`: If the operation fails with an unexpected status code.

        Returns:
            All the textbanks.

        Documentation Reference:
            `<https://www.solidarity.tech/reference/get_textbanks>`__

        """
        if isinstance(ids, list):
            ids = ",".join(str(id) for id in ids)

        params = {"event_id": event_id, "ids": ids, "include_stats": include_stats}
        res = self._get_resources(
            "textbanks",
            limit=limit,
            offset=offset,
            since=since,
            params=params,
        )

        expected_responses = {200: (True, "textbanks listed")}
        self._handle_status_codes(res=res, codes=expected_responses)

        return Table(res.json())

    def get_textbank(
        self,
        id: int,
    ) -> dict:
        """
        Retrieve a single textbank.

        Args:
            id:
                ID of the textbank to retrieve.

        Raises:
            :class:`STFailedResponseError`: If the operation fails with a known error code.
            :class:`STUnexpectedResponseError`: If the operation fails with an unexpected status code.

        Returns:
            A single textbank.

        Documentation Reference:
            `<https://www.solidarity.tech/reference/get_textbanks-id>`__

        """
        res = self._get_single_resource("textbanks", id)

        expected_responses = {
            200: (True, "textbank found"),
            404: (False, "textbank not found"),
        }
        self._handle_status_codes(res=res, codes=expected_responses)

        return res.json()
