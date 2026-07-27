import logging

from requests.exceptions import HTTPError

from parsons.solidarity_tech.solidarity_tech_base import SolidarityTechBase
from parsons.solidarity_tech.solidarity_tech_exceptions import STUnexpectedResponseCodeError

logger = logging.getLogger(__name__)


class SolidarityTechEmails(SolidarityTechBase):
    def send_one_off_email(
        self,
        user_id: int,
        subject: str,
        body_html: str,
        body_plain: str | None = None,
        email_sender_id: int | None = None,
        reply_to: str | None = None,
        attachment_urls: list[str] | None = None,
        track_opens: bool = True,
        track_clicks: bool = True,
    ) -> str:
        """
        Returns a list of email senders available for the API key's scope.
        Use these sender IDs when sending emails via the POST /emails endpoint.

        Args:
            user_id:
                ID of the user to send email to.
            subject:
                Email subject line (supports Liquid templating).
            body_html:
                HTML content of the email (supports Liquid templating).
            body_plain:
                Plain text fallback content.
            email_sender_id:
                ID of configured email sender (uses org default if omitted).
            reply_to:
                Reply-to email address.
            attachment_urls:
                Array of URLs to files to attach (max 5).
            track_opens:
                Enable open tracking. Default is True.
            track_clicks:
                Enable click tracking. Default is True.

        Returns:
            Boolean representing success of the operation.
            True if the operation was successful, False otherwise.

        Raises:
            HTTPError: Missing required parameters.
            STUnexpectedResponseCodeError: If the operation fails with an unexpected status code.

        Documentation Reference:
            `<https://www.solidarity.tech/reference/post_emails>`__

        """
        email_params = {
            "user_id": user_id,
            "subject": subject,
            "body_html": body_html,
            "body_plain": body_plain,
            "email_sender_id": email_sender_id,
            "reply_to": reply_to,
            "attachment_urls": attachment_urls,
            "track_opens": track_opens,
            "track_clicks": track_clicks,
        }

        res = self._post_request("emails", params=email_params)

        if res.status_code not in (201, 404, 422):
            raise STUnexpectedResponseCodeError(res)

        if res.status_code == 404:
            raise HTTPError("User not found")

        if res.status_code == 422:
            raise HTTPError("Missing required parameters")

        return res.text
