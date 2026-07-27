import logging
from datetime import datetime

from parsons.solidarity_tech.solidarity_tech_base import SolidarityTechBase
from parsons.solidarity_tech.solidarity_tech_exceptions import STUnexpectedResponseCodeError

logger = logging.getLogger(__name__)


class SolidarityTechChapterPhoneNumbers(SolidarityTechBase):
    def get_chapter_phone_numbers(
        self,
        limit: int = 20,
        offset: int = 0,
        since: int | datetime | None = 0,
        chapter_id: int = 0,
    ) -> str:
        """
        Retrieve a list of chapter phone numbers.

        Args:
            limit:
                Limits the number of items returned.
                Default is 20, maximum is 100.
            offset:
                Number of items to skip before starting to return the results.
            since:
                UTC timestamp in seconds since the Unix epoch to filter calls created after this time.
            chapter_id:
                Filters chapter phone numbers by chapter_id within the accessible scope.

        Returns:
            All the chapter phone numbers entries.

        Raises:
            STUnexpectedResponseCodeError: If the operation fails with an unexpected status code.

        Documentation Reference:
            `<https://www.solidarity.tech/reference/get_chapter-phone-numbers>`__

        """
        res = self._get_resources(
            "chapter_phone_numbers",
            limit=limit,
            offset=offset,
            since=since,
            chapter_id=chapter_id,
        )

        if res.status_code != 200:
            raise STUnexpectedResponseCodeError(res)

        return res.text
