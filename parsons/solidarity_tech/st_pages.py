import logging
from datetime import datetime

from requests.exceptions import HTTPError

from parsons.solidarity_tech.exceptions import STUnexpectedResponseCodeError
from parsons.solidarity_tech.solidarity_tech_base import SolidarityTechBase

logger = logging.getLogger(__name__)


class SolidarityTechPages(SolidarityTechBase):
    def get_pages(
        self,
        limit: int = 20,
        offset: int = 0,
        since: int | datetime = 0,
        include_action_counts: bool = False,
    ) -> str:
        """
        Retrieve a list of pages.

        Args:
            limit:
                Limits the number of items returned.
                Default is 20, maximum is 100.
            offset:
                Number of items to skip before starting to return the results.
            since:
                UTC timestamp in seconds since the Unix epoch to filter calls created after this time.
            include_action_counts:
                If True, each page includes ``action_count`` (total submissions) and ``action_goal``
                (the next milestone the public progress bar would display for that count).
                Default is False.

        Returns:
            All the pages.

        Documentation Reference:
            `<https://www.solidarity.tech/reference/get_pages>`__

        """
        params = {"include_action_counts": include_action_counts}
        res = self._get_resources(
            "pages",
            limit=limit,
            offset=offset,
            since=since,
            params=params,
        )

        if res.status_code != 200:
            raise STUnexpectedResponseCodeError(res)

        return res.text

    def get_page(
        self,
        id: int,
        include_action_counts: bool = False,
    ) -> str:
        """
        Retrieve a single page.

        Args:
            id:
                ID of the page to retrieve.
            include_action_counts:
                If True, the page includes ``action_count`` (total submissions) and ``action_goal``
                (the next milestone the public progress bar would display for that count).
                Default is False.

        Returns:
            A single page entry.

        Raises:
            HTTPError: If the page is not found.
            STUnexpectedResponseCodeError: If the operation fails with an unexpected status code.

        Documentation Reference:
            `<https://www.solidarity.tech/reference/get_pages-id>`__

        """
        res = self._get_single_resource("pages", id)

        if res.status_code not in (200, 404):
            raise STUnexpectedResponseCodeError(res)

        if res.status_code == 404:
            raise HTTPError("page not found.", response=res)

        return res.text
