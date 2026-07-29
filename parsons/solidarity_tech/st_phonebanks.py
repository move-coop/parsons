import logging
from datetime import datetime

from requests.exceptions import HTTPError

from parsons.solidarity_tech.exceptions import STUnexpectedResponseCodeError
from parsons.solidarity_tech.solidarity_tech_base import SolidarityTechBase

logger = logging.getLogger(__name__)


class SolidarityTechPhonebanks(SolidarityTechBase):
    def get_phonebanks(
        self,
        limit: int = 20,
        offset: int = 0,
        since: int | datetime = 0,
        event_id: int = 0,
        ids: list[int] | None = None,
        include_stats: bool = False,
    ) -> str:
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
                Filters to specific phonebank ids. Accepts a comma-separated string (e.g. "12,34").
            include_stats:
                If True, each phonebank row also includes aggregate funnel numbers
                ``attempts`` (contact attempts), ``contacted`` (distinct people attempted),
                and ``reached`` (distinct people on answered calls).
                Default is False.

        Returns:
            All the phonebanks.

        Documentation Reference:
            `<https://www.solidarity.tech/reference/get_phonebanks>`__

        """
        params = {"event_id": event_id, "ids": ids, "include_stats": include_stats}
        res = self._get_resources(
            "phonebanks",
            limit=limit,
            offset=offset,
            since=since,
            params=params,
        )

        if res.status_code != 200:
            raise STUnexpectedResponseCodeError(res)

        return res.text

    def get_phonebank(
        self,
        id: int,
    ) -> str:
        """
        Retrieve a single phonebank.

        Args:
            id:
                ID of the phonebank to retrieve.

        Returns:
            A single phonebank entry.

        Raises:
            HTTPError: If the phonebank is not found.
            STUnexpectedResponseCodeError: If the operation fails with an unexpected status code.

        Documentation Reference:
            `<https://www.solidarity.tech/reference/get_phonebanks-id>`__

        """
        res = self._get_single_resource("phonebanks", id)

        if res.status_code not in (200, 404):
            raise STUnexpectedResponseCodeError(res)

        if res.status_code == 404:
            raise HTTPError("Phonebank not found.", response=res)

        return res.text
