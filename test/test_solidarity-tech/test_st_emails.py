"""Tests for the Emails methods of :class:`~parsons.solidarity_tech.SolidarityTech`."""

from __future__ import annotations

from http import HTTPStatus
from typing import TYPE_CHECKING
from urllib import parse

import pytest

if TYPE_CHECKING:
    from requests_mock import Mocker

    from parsons.solidarity_tech import SolidarityTech

ENDPOINT = "emails"


class TestSendOneOffEmail:
    @pytest.mark.vcr
    def test_send_one_off_email_live(self, st: SolidarityTech) -> None:
        """Verify that :meth:`~parsons.solidarity_tech.SolidarityTech.send_one_off_email` returns both a Table of results and the associated metadata."""
        user_id = 1928273
        subject = "Test Email Subject"
        body_html = "Hi! This email is just a test."

        email = st.send_one_off_email(user_id=user_id, subject=subject, body_html=body_html)
        assert email["message"] == "Email sent successfully"
        assert email["user_id"] == user_id
        assert isinstance(email["to"], str)
        assert email["subject"] == subject
        assert isinstance(email["email_sender_id"], int)

    def test_send_one_off_email_minimal(self, st: SolidarityTech, requests_mock: Mocker) -> None:
        """Verify that :meth:`~parsons.solidarity_tech.SolidarityTech.send_one_off_email` makes the appropriate calls."""
        user_id = 3857
        subject = "Test Email Subject"
        body_html = "<html><body>Hi! This email is just a test.</body></html>"
        endpoint_url = f"{st.api_url}{ENDPOINT}?user_id={user_id}&subject={parse.quote_plus(subject)}&body_html={parse.quote_plus(body_html)}&track_opens={True}&track_clicks={True}"

        _ = requests_mock.post(
            endpoint_url, status_code=HTTPStatus.CREATED, json={"data": [{}], "meta": {}}
        )

        _ = st.send_one_off_email(user_id=user_id, subject=subject, body_html=body_html)

        assert requests_mock.call_count == 1
        assert requests_mock.last_request is not None
        assert requests_mock.last_request.method == "POST"
        assert requests_mock.last_request.url == endpoint_url

    def test_send_one_off_email_maximal(self, st: SolidarityTech, requests_mock: Mocker) -> None:
        """Verify that :meth:`~parsons.solidarity_tech.SolidarityTech.send_one_off_email` makes the appropriate calls."""
        user_id = 3857
        subject = "Test Email Subject"
        body_html = "<html><body>Hi! This email is just a test.</body></html>"
        body_plain = "Hi! This email is just a test."
        email_sender_id = 239
        reply_to = "nobody@example.com"
        attachment_urls = [
            "https://upload.wikimedia.org/wikipedia/commons/5/54/Flynn%2C_Elizabeth_Gurley_Edit.jpg"
        ]
        track_opens = False
        track_clicks = False
        endpoint_url = f"{st.api_url}{ENDPOINT}?user_id={user_id}&subject={parse.quote_plus(subject)}&body_html={parse.quote_plus(body_html)}&track_opens={track_opens}&track_clicks={track_clicks}&body_plain={parse.quote_plus(body_plain)}&email_sender_id={email_sender_id}&reply_to={parse.quote_plus(reply_to)}&attachment_urls={'&attachment_urls='.join([parse.quote_plus(url) for url in attachment_urls])}"

        _ = requests_mock.post(
            endpoint_url, status_code=HTTPStatus.CREATED, json={"data": [{}], "meta": {}}
        )

        _ = st.send_one_off_email(
            user_id=user_id,
            subject=subject,
            body_html=body_html,
            body_plain=body_plain,
            email_sender_id=email_sender_id,
            reply_to=reply_to,
            attachment_urls=attachment_urls,
            track_opens=track_opens,
            track_clicks=track_clicks,
        )

        assert requests_mock.call_count == 1
        assert requests_mock.last_request is not None
        assert requests_mock.last_request.method == "POST"
        assert requests_mock.last_request.url == endpoint_url
