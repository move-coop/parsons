import logging
from datetime import datetime

from parsons import Table
from parsons.solidarity_tech.solidarity_tech_base import SolidarityTechBase

logger = logging.getLogger(__name__)


class SolidarityTechTexts(SolidarityTechBase):
    def get_texts(
        self,
        user_id: int | None = None,
        limit: int = 20,
        offset: int = 0,
        since: int | datetime = 0,
    ) -> Table:
        """
        Retrieve a list of texts.

        Args:
            user_id:
                The ID of the user to retrieve texts for.
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
            All the texts.

        Documentation Reference:
            `<https://www.solidarity.tech/reference/get_texts>`__

        """
        params = {"user_id": user_id}
        res = self._get_resources(
            "texts",
            limit=limit,
            offset=offset,
            since=since,
            params=params,
            additional_headers={"accept": "application/json"},
        )

        expected_responses = {200: (True, "texts listed")}
        self._handle_status_codes(res=res, codes=expected_responses)

        return Table(res.json())

    def send_text(
        self,
        user_id: int,
        body: str,
        media_urls: list[str] | None = None,
        attach_contact_card: bool | None = None,
        shorten_urls: bool | None = None,
    ) -> bool:
        """
        Sends a text to a specific user.

        Args:
            user_id:
                The ID of the user to send a text to.
            body:
                The text body to send.
            media_urls:
                List of media to include in the text.
            attach_contact_card:
                Whether to attach the contact card to the text.
            shorten_urls:
                Whether to shorten URLs in the text.

        Raises:
            :class:`STFailedResponseError`: If the operation fails with a known error code.
            :class:`STUnexpectedResponseError`: If the operation fails with an unexpected status code.

        Returns:
            Boolean representing success of the operation.
            True if the operation was successful, False otherwise.

        Documentation Reference:
            `<https://www.solidarity.tech/reference/post_texts>`__

        """
        params = {
            "user_id": user_id,
            "body": body,
            "media_urls": media_urls,
            "attach_contact_card": attach_contact_card,
            "shorten_urls": shorten_urls,
        }
        res = self._post_request(
            "texts",
            params=params,
        )

        expected_responses = {201: (True, "text sent")}
        return self._handle_status_codes(res=res, codes=expected_responses)
