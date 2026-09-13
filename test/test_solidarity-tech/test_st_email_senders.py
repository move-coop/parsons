"""Tests for the Email Senders methods of :class:`~parsons.solidarity_tech.SolidarityTech`."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from parsons import Table

if TYPE_CHECKING:
    from requests_mock import Mocker

    from parsons.solidarity_tech import SolidarityTech

ENDPOINT = "email_senders"


class TestGetEmailSenders:
    @pytest.mark.vcr
    def test_get_email_senders_live(self, st: SolidarityTech) -> None:
        """Verify that :meth:`~parsons.solidarity_tech.SolidarityTech.get_email_senders` returns both a Table of results and the associated metadata."""
        email_senders, email_senders_meta = st.get_email_senders()

        assert isinstance(email_senders, Table)
        assert email_senders.name == "Solidarity Tech Email Senders"
        assert len(email_senders) > 0
        assert isinstance(email_senders[0], dict)

        assert isinstance(email_senders_meta, dict)
        assert email_senders_meta["total_count"] > 0
        assert email_senders_meta["limit"] == 20
        assert email_senders_meta["offset"] == 0

    def test_get_email_senders_minimal(self, st: SolidarityTech, requests_mock: Mocker) -> None:
        """Verify that :meth:`~parsons.solidarity_tech.SolidarityTech.get_email_senders` makes the appropriate calls."""
        endpoint_url = f"{st.api_url}{ENDPOINT}?_limit=20&_offset=0"
        _ = requests_mock.get(endpoint_url, json={"data": [{}], "meta": {}})

        _, _ = st.get_email_senders()

        assert requests_mock.call_count == 1
        assert requests_mock.last_request is not None
        assert requests_mock.last_request.method == "GET"
        assert requests_mock.last_request.url == endpoint_url

    def test_get_email_senders_maximal(self, st: SolidarityTech, requests_mock: Mocker) -> None:
        """Verify that :meth:`~parsons.solidarity_tech.SolidarityTech.get_email_senders` makes the appropriate calls."""
        limit = 30
        offset = 5
        endpoint_url = f"{st.api_url}{ENDPOINT}?_limit={limit}&_offset={offset}"
        _ = requests_mock.get(endpoint_url, json={"data": [{}], "meta": {}})

        _, _ = st.get_email_senders(limit=limit, offset=offset)

        assert requests_mock.call_count == 1
        assert requests_mock.last_request is not None
        assert requests_mock.last_request.method == "GET"
        assert requests_mock.last_request.url == endpoint_url
