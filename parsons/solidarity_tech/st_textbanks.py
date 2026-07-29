import logging
from datetime import datetime

from parsons.solidarity_tech.exceptions import STUnexpectedResponseCodeError
from parsons.solidarity_tech.solidarity_tech_base import SolidarityTechBase

logger = logging.getLogger(__name__)


class SolidarityTechTextbanks(SolidarityTechBase):
    def get_textbanks(
        self,
        limit: int = 20,
        offset: int = 0,
        since: int | datetime = 0,
        event_id: int = 0,
        ids: str | None = None,
        include_stats: bool = False,
    ) -> str:
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

        Returns:
            All the textbanks.

        Documentation Reference:
            `<https://www.solidarity.tech/reference/get_textbanks>`__

        """
        params = {"event_id": event_id, "ids": ids, "include_stats": include_stats}
        res = self._get_resources(
            "textbanks",
            limit=limit,
            offset=offset,
            since=since,
            params=params,
        )

        if res.status_code != 200:
            raise STUnexpectedResponseCodeError(res)

        return res.text

    def get_textbank(
        self,
        id: int,
    ) -> str:
        """
        Retrieve a single textbank.

        Args:
            id:
                ID of the textbank to retrieve.

        Returns:
            A single textbank.

        Raises:
            STUnexpectedResponseCodeError: If the operation fails with an unexpected status code.

        Documentation Reference:
            `<https://www.solidarity.tech/reference/get_textbanks-id>`__

        """
        res = self._get_single_resource("textbanks", id)

        if res.status_code not in (200, 404):
            raise STUnexpectedResponseCodeError(res)

        return res.text
