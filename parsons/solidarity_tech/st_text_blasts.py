import logging
from datetime import datetime

from parsons.solidarity_tech.exceptions import STUnexpectedResponseCodeError
from parsons.solidarity_tech.solidarity_tech_base import SolidarityTechBase

logger = logging.getLogger(__name__)


class SolidarityTechTextBlasts(SolidarityTechBase):
    def get_text_blasts(
        self,
        limit: int = 20,
        offset: int = 0,
        since: int | datetime = 0,
    ) -> str:
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

        if res.status_code != 200:
            raise STUnexpectedResponseCodeError(res)

        return res.text

    def get_text_blast(
        self,
        id: int,
    ) -> str:
        """
        Retrieve a single text blast.

        Args:
            id:
                ID of the text blast to retrieve.

        Returns:
            A single text blast entry.

        Raises:
            STUnexpectedResponseCodeError: If the operation fails with an unexpected status code.

        Documentation Reference:
            `<https://www.solidarity.tech/reference/get_text-blasts-id>`__

        """
        res = self._get_single_resource("text_blasts", id)

        if res.status_code not in (200, 404):
            raise STUnexpectedResponseCodeError(res)

        return res.text
