"""Tests for the Scheduled Calls methods of :class:`~parsons.solidarity_tech.SolidarityTech`."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from requests_mock import Mocker

    from parsons.solidarity_tech import SolidarityTech

ENDPOINT = "scheduled_calls"


class TestGetScheduledCalls:
    # TODO(bmos): Implement once there is data
    #    @pytest.mark.vcr
    #    def test_get_scheduled_calls_live(self, st: SolidarityTech) -> None:
    #        """Verify that :meth:`~parsons.solidarity_tech.SolidarityTech.get_scheduled_calls` returns both a Table of results and the associated metadata."""
    #        scheduled_calls, scheduled_calls_meta = st.get_scheduled_calls()
    #
    #        assert isinstance(scheduled_calls, Table)
    #        assert scheduled_calls.name == "Solidarity Tech Scheduled Calls"
    #        assert len(scheduled_calls) > 0
    #        assert isinstance(scheduled_calls[0], dict)
    #
    #        assert isinstance(scheduled_calls_meta, dict)
    #        assert scheduled_calls_meta["total_count"] > 0
    #        assert scheduled_calls_meta["limit"] == 20
    #        assert scheduled_calls_meta["offset"] == 0

    def test_get_scheduled_calls_minimal(self, st: SolidarityTech, requests_mock: Mocker) -> None:
        """Verify that :meth:`~parsons.solidarity_tech.SolidarityTech.get_scheduled_calls` makes the appropriate calls."""
        endpoint_url = f"{st.api_url}{ENDPOINT}?_limit=20&_offset=0&_since=0"
        _ = requests_mock.get(endpoint_url, json={"data": [{}], "meta": {}})

        _ = st.get_scheduled_calls()

        assert requests_mock.call_count == 1
        assert requests_mock.last_request is not None
        assert requests_mock.last_request.method == "GET"
        assert requests_mock.last_request.url == endpoint_url

    def test_get_scheduled_calls_maximal(self, st: SolidarityTech, requests_mock: Mocker) -> None:
        """Verify that :meth:`~parsons.solidarity_tech.SolidarityTech.get_scheduled_calls` makes the appropriate calls."""
        limit = 30
        offset = 5
        since = 1788075104
        user_id = 2796
        agent_user_id = 908
        endpoint_url = f"{st.api_url}{ENDPOINT}?_limit={limit}&_offset={offset}&_since={since}&user_id={user_id}&agent_user_id={agent_user_id}"
        _ = requests_mock.get(endpoint_url, json={"data": [{}], "meta": {}})

        _ = st.get_scheduled_calls(
            limit=limit,
            offset=offset,
            since=since,
            user_id=user_id,
            agent_user_id=agent_user_id,
        )

        assert requests_mock.call_count == 1
        assert requests_mock.last_request is not None
        assert requests_mock.last_request.method == "GET"
        assert requests_mock.last_request.url == endpoint_url


class TestGetScheduledCall:
    # TODO(bmos): Implement once there is data
    #    @pytest.mark.vcr
    #    def test_get_scheduled_call_live(self, st: SolidarityTech) -> None:
    #        """Verify that :meth:`~parsons.solidarity_tech.SolidarityTech.get_scheduled_call` returns the expected data."""
    #        resource_id = 774
    #        scheduled_call, scheduled_call_meta = st.get_scheduled_call(resource_id=resource_id)
    #
    #        assert isinstance(scheduled_call, dict)
    #        assert scheduled_call["id"] == resource_id
    #
    #        assert isinstance(scheduled_call_meta, dict)
    #        assert scheduled_call_meta["total_count"] > 0
    #        assert scheduled_call_meta["limit"] == 1
    #        assert scheduled_call_meta["offset"] == 0

    def test_get_scheduled_call(self, st: SolidarityTech, requests_mock: Mocker) -> None:
        """Verify that :meth:`~parsons.solidarity_tech.SolidarityTech.get_scheduled_call` makes the appropriate calls."""
        resource_id = 960
        endpoint_url = f"{st.api_url}{ENDPOINT}/{resource_id}"
        _ = requests_mock.get(endpoint_url, json={"data": {}, "meta": {}})

        _, _ = st.get_scheduled_call(resource_id=resource_id)

        assert requests_mock.call_count == 1
        assert requests_mock.last_request is not None
        assert requests_mock.last_request.method == "GET"
        assert requests_mock.last_request.url == endpoint_url
