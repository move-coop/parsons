import logging
from datetime import datetime

from requests.exceptions import HTTPError

from parsons.solidarity_tech.exceptions import STUnexpectedResponseCodeError
from parsons.solidarity_tech.solidarity_tech_base import SolidarityTechBase

logger = logging.getLogger(__name__)


class SolidarityTechEmailBlasts(SolidarityTechBase):
    def get_email_blasts(
        self,
        limit: int = 20,
        offset: int = 0,
        since: int | datetime = 0,
    ) -> str:
        """
        Retrieve a list of email blasts.

        Args:
            limit:
                Limits the number of items returned.
                Default is 20, maximum is 100.
            offset:
                Number of items to skip before starting to return the results.
            since:
                UTC timestamp in seconds since the Unix epoch to filter calls created after this time.

        Returns:
            All the email blasts.

        Documentation Reference:
            `<https://www.solidarity.tech/reference/get_email-blasts>`__

        """
        res = self._get_resources(
            "email_blasts",
            limit=limit,
            offset=offset,
            since=since,
        )

        if res.status_code != 200:
            raise STUnexpectedResponseCodeError(res)

        return res.text

    def get_email_blast(
        self,
        id: int,
    ) -> str:
        """
        Retrieve a single email blast.

        Args:
            id:
                ID of the email blast to retrieve.

        Returns:
            A single email blast entry.

        Raises:
            STUnexpectedResponseCodeError: If the operation fails with an unexpected status code.

        Documentation Reference:
            `<https://www.solidarity.tech/reference/get_email-blasts-id>`__

        """
        res = self._get_single_resource("email_blasts", id)

        if res.status_code not in (200, 404):
            raise STUnexpectedResponseCodeError(res)

        if res.status_code == 404:
            raise HTTPError("Email blast not found", response=res)

        return res.text
