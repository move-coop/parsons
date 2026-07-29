import logging
from datetime import datetime

from parsons.solidarity_tech.exceptions import STUnexpectedResponseCodeError
from parsons.solidarity_tech.solidarity_tech_base import SolidarityTechBase

logger = logging.getLogger(__name__)


class SolidarityTechTexts(SolidarityTechBase):
    def get_texts(
        self,
        user_id: int | None = None,
        limit: int = 20,
        offset: int = 0,
        since: int | datetime = 0,
    ) -> str:
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

        if res.status_code != 200:
            raise STUnexpectedResponseCodeError(res)

        return res.text

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

        Returns:
            Boolean representing success of the operation.
            True if the operation was successful, False otherwise.

        Raises:
            STUnexpectedResponseCodeError: If the operation fails with an unexpected status code.

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

        if res.status_code not in (201, 404):
            raise STUnexpectedResponseCodeError(res)

        return res.status_code == 201
