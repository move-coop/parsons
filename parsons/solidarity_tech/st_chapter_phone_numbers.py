import logging
from datetime import datetime

from parsons import Table
from parsons.solidarity_tech.solidarity_tech_base import SolidarityTechBase

logger = logging.getLogger(__name__)


class SolidarityTechChapterPhoneNumbers(SolidarityTechBase):
    def get_chapter_phone_numbers(
        self,
        limit: int = 20,
        offset: int = 0,
        since: int | datetime = 0,
        chapter_id: int = 0,
    ) -> Table:
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

        Raises:
            :class:`STFailedResponseError`: If the operation fails with a known error code.
            :class:`STUnexpectedResponseError`: If the operation fails with an unexpected status code.

        Returns:
            All the chapter phone numbers entries.

        Documentation Reference:
            `<https://www.solidarity.tech/reference/get_chapter-phone-numbers>`__

        """
        params = {"chapter_id": chapter_id}
        res = self._get_resources(
            "chapter_phone_numbers",
            limit=limit,
            offset=offset,
            since=since,
            params=params,
        )

        expected_responses = {200: (True, "chapter phone numbers listed")}
        self._handle_status_codes(res=res, codes=expected_responses)

        return Table(res.json())
