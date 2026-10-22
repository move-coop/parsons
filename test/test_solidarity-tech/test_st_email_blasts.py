"""Tests for the Email Blasts methods of :class:`~parsons.solidarity_tech.SolidarityTech`."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from parsons import Table

if TYPE_CHECKING:
    from requests_mock import Mocker

    from parsons.solidarity_tech import SolidarityTech

ENDPOINT = "email_blasts"


class TestGetEmailBlasts:
    @pytest.mark.vcr
    def test_get_email_blasts_live(self, st: SolidarityTech) -> None:
        """Verify that :meth:`~parsons.solidarity_tech.SolidarityTech.get_email_blasts` returns both a Table of results and the associated metadata."""
        email_blasts, email_blasts_meta = st.get_email_blasts()

        assert isinstance(email_blasts, Table)
        assert email_blasts.name == "Solidarity Tech Email Blasts"
        assert len(email_blasts) > 0
        assert isinstance(email_blasts[0], dict)

        assert isinstance(email_blasts_meta, dict)
        assert email_blasts_meta["total_count"] > 0
        assert email_blasts_meta["limit"] == 20
        assert email_blasts_meta["offset"] == 0

    def test_get_email_blasts_minimal(self, st: SolidarityTech, requests_mock: Mocker) -> None:
        """Verify that :meth:`~parsons.solidarity_tech.SolidarityTech.get_email_blasts` makes the appropriate calls."""
        endpoint_url = f"{st.api_url}{ENDPOINT}?_limit=20&_offset=0&_since=0"
        _ = requests_mock.get(endpoint_url, json={"data": [{}], "meta": {}})

        _, _ = st.get_email_blasts()

        assert requests_mock.call_count == 1
        assert requests_mock.last_request is not None
        assert requests_mock.last_request.method == "GET"
        assert requests_mock.last_request.url == endpoint_url

    def test_get_email_blasts_maximal(self, st: SolidarityTech, requests_mock: Mocker) -> None:
        """Verify that :meth:`~parsons.solidarity_tech.SolidarityTech.get_email_blasts` makes the appropriate calls."""
        limit = 30
        offset = 5
        since = 1788075104
        endpoint_url = f"{st.api_url}{ENDPOINT}?_limit={limit}&_offset={offset}&_since={since}"
        _ = requests_mock.get(endpoint_url, json={"data": [{}], "meta": {}})

        _, _ = st.get_email_blasts(limit=limit, offset=offset, since=since)

        assert requests_mock.call_count == 1
        assert requests_mock.last_request is not None
        assert requests_mock.last_request.method == "GET"
        assert requests_mock.last_request.url == endpoint_url


class TestGetEmailBlast:
    @pytest.mark.vcr
    def test_get_email_blast_live(self, st: SolidarityTech) -> None:
        """Verify that :meth:`~parsons.solidarity_tech.SolidarityTech.get_email_blast` returns both the specific result and the associated metadata."""
        resource_id = 3617
        email_blast, email_blast_meta = st.get_email_blast(resource_id=resource_id)

        assert isinstance(email_blast, dict)
        assert email_blast["id"] == resource_id

        assert isinstance(email_blast_meta, dict)
        assert email_blast_meta["total_count"] > 0
        assert email_blast_meta["limit"] == 1
        assert email_blast_meta["offset"] == 0

    def test_get_email_blast(self, st: SolidarityTech, requests_mock: Mocker) -> None:
        """Verify that :meth:`~parsons.solidarity_tech.SolidarityTech.get_email_blast` makes the appropriate calls."""
        resource_id = 3617
        endpoint_url = f"{st.api_url}{ENDPOINT}/{resource_id}"
        _ = requests_mock.get(endpoint_url, json={"data": {}, "meta": {}})

        _, _ = st.get_email_blast(resource_id=resource_id)

        assert requests_mock.call_count == 1
        assert requests_mock.last_request is not None
        assert requests_mock.last_request.method == "GET"
        assert requests_mock.last_request.url == endpoint_url
