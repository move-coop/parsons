import logging
from datetime import datetime

from parsons.solidarity_tech.solidarity_tech_base import SolidarityTechBase
from parsons.solidarity_tech.solidarity_tech_exceptions import STUnexpectedResponseCodeError

logger = logging.getLogger(__name__)


class SolidarityTechChapters(SolidarityTechBase):
    def get_chapters(
        self,
        limit: int = 20,
        offset: int = 0,
        since: int | datetime | None = 0,
    ) -> str:
        """
        Retrieve a list of chapters.

        Args:
            limit:
                Limits the number of items returned.
                Default is 20, maximum is 100.
            offset:
                Number of items to skip before starting to return the results.
            since:
                UTC timestamp in seconds since the Unix epoch to filter chapters created after this time.

        Returns:
            All the chapters entries.

        Raises:
            STUnexpectedResponseCodeError: If the operation fails with an unexpected status code.

        Documentation Reference:
            `<https://www.solidarity.tech/reference/get_chapters>`__

        """
        res = self._get_resources(
            "chapters",
            limit=limit,
            offset=offset,
            since=since,
            additional_headers={"accept": "application/json"},
        )

        if res.status_code != 200:
            raise STUnexpectedResponseCodeError(res)

        return res.text
