import logging

from parsons.solidarity_tech.solidarity_tech_base import SolidarityTechBase

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
    ) -> bool:
        """
        Sends a single transactional email to a user.
        Supports Liquid templating for personalization (e.g., {{ first_name }}).

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

        Raises:
            :class:`STFailedResponseError`: If the operation fails with a known error code.
            :class:`STUnexpectedResponseError`: If the operation fails with an unexpected status code.

        Returns:
            Boolean representing success of the operation.
            True if the operation was successful, False otherwise.

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

        expected_responses = {
            201: (True, "email sent successfully"),
            404: (False, "user not found"),
            422: (False, "missing required parameters"),
        }
        return self._handle_status_codes(res=res, codes=expected_responses)
