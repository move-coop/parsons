"""Tests for the Calls methods of :class:`~parsons.solidarity_tech.SolidarityTech`."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from parsons import Table

if TYPE_CHECKING:
    from requests_mock import Mocker

    from parsons.solidarity_tech import SolidarityTech

ENDPOINT = "calls"


class TestGetCalls:
    @pytest.mark.vcr
    def test_get_calls_live(self, st: SolidarityTech) -> None:
        """Verify that :meth:`~parsons.solidarity_tech.SolidarityTech.get_calls` returns both a Table of results and the associated metadata."""
        calls, calls_meta = st.get_calls()

        assert isinstance(calls, Table)
        assert calls.name == "Solidarity Tech Calls"
        assert len(calls) > 0
        assert isinstance(calls[0], dict)

        assert isinstance(calls_meta, dict)
        assert calls_meta["total_count"] > 0
        assert calls_meta["limit"] == 20
        assert calls_meta["offset"] == 0

    def test_get_calls_minimal(self, st: SolidarityTech, requests_mock: Mocker) -> None:
        """Verify that :meth:`~parsons.solidarity_tech.SolidarityTech.get_calls` makes the appropriate calls."""
        endpoint_url = f"{st.api_url}{ENDPOINT}?_limit=20&_offset=0&_since=0"
        _ = requests_mock.get(endpoint_url, json={"data": [{}], "meta": {}})

        _ = st.get_calls()

        assert requests_mock.call_count == 1
        assert requests_mock.last_request is not None
        assert requests_mock.last_request.method == "GET"
        assert requests_mock.last_request.url == endpoint_url

    def test_get_calls_maximal(self, st: SolidarityTech, requests_mock: Mocker) -> None:
        """Verify that :meth:`~parsons.solidarity_tech.SolidarityTech.get_calls` makes the appropriate calls."""
        user_id = 1191722
        limit = 30
        offset = 5
        since = 1788075104
        endpoint_url = f"{st.api_url}{ENDPOINT}?_limit={limit}&_offset={offset}&_since={since}&user_id={user_id}"
        _ = requests_mock.get(endpoint_url, json={"data": [{}], "meta": {}})

        _ = st.get_calls(user_id=user_id, limit=limit, offset=offset, since=since)

        assert requests_mock.call_count == 1
        assert requests_mock.last_request is not None
        assert requests_mock.last_request.method == "GET"
        assert requests_mock.last_request.url == endpoint_url
