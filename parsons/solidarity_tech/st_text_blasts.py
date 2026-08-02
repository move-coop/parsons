import logging
from datetime import datetime

from parsons import Table
from parsons.solidarity_tech.solidarity_tech_base import SolidarityTechBase

logger = logging.getLogger(__name__)


class SolidarityTechTextBlasts(SolidarityTechBase):
    def get_text_blasts(
        self,
        limit: int = 20,
        offset: int = 0,
        since: int | datetime = 0,
    ) -> Table:
        """
        Retrieve a list of text blasts.

        Args:
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
            All the text blast entries.

        Documentation Reference:
            `<https://www.solidarity.tech/reference/get_text-blasts>`__

        """
        res = self._get_resources(
            "text_blasts",
            limit=limit,
            offset=offset,
            since=since,
        )

        expected_responses = {200: (True, "text blasts listed")}
        self._handle_status_codes(res=res, codes=expected_responses)

        return Table(res.json())

    def get_text_blast(
        self,
        id: int,
    ) -> dict:
        """
        Retrieve a single text blast.

        Args:
            id:
                ID of the text blast to retrieve.

        Raises:
            :class:`STFailedResponseError`: If the operation fails with a known error code.
            :class:`STUnexpectedResponseError`: If the operation fails with an unexpected status code.

        Returns:
            A single text blast entry.

        Documentation Reference:
            `<https://www.solidarity.tech/reference/get_text-blasts-id>`__

        """
        res = self._get_single_resource("text_blasts", id)

        expected_responses = {
            200: (True, "text blast found"),
            404: (False, "text blast not found"),
        }
        self._handle_status_codes(res=res, codes=expected_responses)

        return res.json()
