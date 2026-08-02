import logging

from parsons import Table
from parsons.solidarity_tech.solidarity_tech_base import SolidarityTechBase

logger = logging.getLogger(__name__)

EmailSenderData = dict[str, int | str | bool]
EmailSenderMetadata = dict[str, int]


class SolidarityTechEmailSenders(SolidarityTechBase):
    def get_email_senders(
        self,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[Table, EmailSenderMetadata]:
        """
        Returns a list of email senders available for the API key's scope.
        Use these sender IDs when sending emails via the POST /emails endpoint.

        Args:
            limit:
                Limits the number of items returned.
                Default is 20, maximum is 100.
            offset:
                Number of items to skip before starting to return the results.

        Raises:
            :class:`STFailedResponseError`: If the operation fails with a known error code.
            :class:`STUnexpectedResponseError`: If the operation fails with an unexpected status code.

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

        expected_responses = {200: (True, "email senders listed")}
        self._handle_status_codes(res=res, codes=expected_responses)

        data: list[EmailSenderData] = res.json()["data"]
        meta: EmailSenderMetadata = res.json()["meta"]
        return Table(data), meta
