import logging

from parsons.solidarity_tech.exceptions import STUnexpectedResponseCodeError
from parsons.solidarity_tech.solidarity_tech_base import SolidarityTechBase

logger = logging.getLogger(__name__)


class SolidarityTechEmailSenders(SolidarityTechBase):
    def get_email_senders(
        self,
        limit: int = 20,
        offset: int = 0,
    ) -> str:
        """
        Returns a list of email senders available for the API key's scope.
        Use these sender IDs when sending emails via the POST /emails endpoint.

        Args:
            limit:
                Limits the number of items returned.
                Default is 20, maximum is 100.
            offset:
                Number of items to skip before starting to return the results.

        Returns:
            All the email senders.

        Documentation Reference:
            `<https://www.solidarity.tech/reference/get_email-senders>`__

        """
        res = self._get_resources(
            "email_senders",
            limit=limit,
            offset=offset,
            additional_headers={"accept": "application/json"},
        )

        if res.status_code != 200:
            raise STUnexpectedResponseCodeError(res)

        return res.text
