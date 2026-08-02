import logging
from datetime import datetime

from parsons import Table
from parsons.solidarity_tech.solidarity_tech_base import SolidarityTechBase

logger = logging.getLogger(__name__)


class SolidarityTechEmailBlasts(SolidarityTechBase):
    def get_email_blasts(
        self,
        limit: int = 20,
        offset: int = 0,
        since: int | datetime = 0,
    ) -> Table:
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

        Raises:
            :class:`STFailedResponseError`: If the operation fails with a known error code.
            :class:`STUnexpectedResponseError`: If the operation fails with an unexpected status code.

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

        expected_responses = {200: (True, "email blasts listed")}
        self._handle_status_codes(res=res, codes=expected_responses)

        return Table(res.json())

    def get_email_blast(
        self,
        id: int,
    ) -> dict:
        """
        Retrieve a single email blast.

        Args:
            id:
                ID of the email blast to retrieve.

        Raises:
            :class:`STFailedResponseError`: If the operation fails with a known error code.
            :class:`STUnexpectedResponseError`: If the operation fails with an unexpected status code.

        Returns:
            A single email blast entry.

        Documentation Reference:
            `<https://www.solidarity.tech/reference/get_email-blasts-id>`__

        """
        res = self._get_single_resource("email_blasts", id)

        expected_responses = {
            200: (True, "email blast found"),
            422: (False, "email blast not found"),
        }
        self._handle_status_codes(res=res, codes=expected_responses)

        return res.json()
