"""Test cases for the Activities methods of the :class:`~parsons.solidarity_tech.SolidarityTech` client."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from parsons import Table

if TYPE_CHECKING:
    from requests_mock import Mocker

    from parsons.solidarity_tech import SolidarityTech

ENDPOINT = "activities"


class TestGetActivities:
    @pytest.mark.vcr
    def test_get_activities_live(self, st: SolidarityTech) -> None:
        """Verify that :meth:`~parsons.solidarity_tech.SolidarityTech.get_activities` returns both a Table of results and the associated metadata."""
        activities, activities_meta = st.get_activities()

        assert isinstance(activities, Table)
        assert len(activities) > 0
        assert isinstance(activities[0], dict)

        assert isinstance(activities_meta, dict)
        assert activities_meta["total_count"] is None
        assert activities_meta["limit"] == 20
        assert activities_meta["offset"] == 0
        assert activities_meta["cursor"] is None
        assert activities_meta["next_cursor"] == 16640151

    def test_activities_minimal(self, st: SolidarityTech, requests_mock: Mocker) -> None:
        """Verify that :meth:`~parsons.solidarity_tech.SolidarityTech.activities` makes the appropriate calls."""
        endpoint_url = f"{st.api_url}{ENDPOINT}?_limit=20&_since=0"
        _ = requests_mock.get(f"{st.api_url}{ENDPOINT}", json={"data": [{}], "meta": {}})
        _, _ = st.get_activities()

        assert requests_mock.call_count == 1
        assert requests_mock.last_request is not None
        assert requests_mock.last_request.method == "GET"
        assert requests_mock.last_request.url == endpoint_url

    def test_activities_maximal(self, st: SolidarityTech, requests_mock: Mocker) -> None:
        """Verify that :meth:`~parsons.solidarity_tech.SolidarityTech.activities` makes the appropriate calls."""
        endpoint_url = f"{st.api_url}{ENDPOINT}?_limit=30&_cursor=5&_since=1788075104&_include_count=True&user_id=8758764"
        _ = requests_mock.get(f"{st.api_url}{ENDPOINT}", json={"data": [{}], "meta": {}})
        _, _ = st.get_activities(
            limit=30,
            cursor=5,
            since=1788075104,
            include_count=True,
            user_id=8758764,
        )

        assert requests_mock.call_count == 1
        assert requests_mock.last_request is not None
        assert requests_mock.last_request.method == "GET"
        assert requests_mock.last_request.url == endpoint_url
