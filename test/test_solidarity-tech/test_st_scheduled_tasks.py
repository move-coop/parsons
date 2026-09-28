"""Tests for the Scheduled Tasks methods of :class:`~parsons.solidarity_tech.SolidarityTech`."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from requests_mock import Mocker

    from parsons.solidarity_tech import SolidarityTech

ENDPOINT = "scheduled_tasks"


class TestGetScheduledTasks:
    # TODO(bmos): Implement once there is data
    #    @pytest.mark.vcr
    #    def test_get_scheduled_tasks_live(self, st: SolidarityTech) -> None:
    #        """Verify that :meth:`~parsons.solidarity_tech.SolidarityTech.get_scheduled_tasks` returns both a Table of results and the associated metadata."""
    #        scheduled_tasks, scheduled_tasks_meta = st.get_scheduled_tasks()
    #
    #        assert isinstance(scheduled_tasks, Table)
    #        assert scheduled_tasks.name == "Solidarity Tech Scheduled Tasks"
    #        assert len(scheduled_tasks) > 0
    #        assert isinstance(scheduled_tasks[0], dict)
    #
    #        assert isinstance(scheduled_tasks_meta, dict)
    #        assert scheduled_tasks_meta["total_count"] > 0
    #        assert scheduled_tasks_meta["limit"] == 20
    #        assert scheduled_tasks_meta["offset"] == 0

    def test_get_scheduled_tasks_minimal(self, st: SolidarityTech, requests_mock: Mocker) -> None:
        """Verify that :meth:`~parsons.solidarity_tech.SolidarityTech.get_scheduled_tasks` makes the appropriate calls."""
        endpoint_url = f"{st.api_url}{ENDPOINT}?_limit=20&_offset=0&_since=0"
        _ = requests_mock.get(endpoint_url, json={"data": [{}], "meta": {}})

        _ = st.get_scheduled_tasks()

        assert requests_mock.call_count == 1
        assert requests_mock.last_request is not None
        assert requests_mock.last_request.method == "GET"
        assert requests_mock.last_request.url == endpoint_url

    def test_get_scheduled_tasks_maximal(self, st: SolidarityTech, requests_mock: Mocker) -> None:
        """Verify that :meth:`~parsons.solidarity_tech.SolidarityTech.get_scheduled_tasks` makes the appropriate calls."""
        limit = 30
        offset = 5
        since = 1788075104
        user_id = 2796
        agent_user_id = 908
        endpoint_url = f"{st.api_url}{ENDPOINT}?_limit={limit}&_offset={offset}&_since={since}&user_id={user_id}&agent_user_id={agent_user_id}"
        _ = requests_mock.get(endpoint_url, json={"data": [{}], "meta": {}})

        _ = st.get_scheduled_tasks(
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


class TestGetScheduledTask:
    # TODO(bmos): Implement once there is data
    #    @pytest.mark.vcr
    #    def test_get_scheduled_task_live(self, st: SolidarityTech) -> None:
    #        """Verify that :meth:`~parsons.solidarity_tech.SolidarityTech.get_scheduled_task` returns the expected data."""
    #        resource_id = 774
    #        scheduled_task, scheduled_task_meta = st.get_scheduled_task(resource_id=resource_id)
    #
    #        assert isinstance(scheduled_task, dict)
    #        assert scheduled_task["id"] == resource_id
    #
    #        assert isinstance(scheduled_task_meta, dict)
    #        assert scheduled_task_meta["total_count"] > 0
    #        assert scheduled_task_meta["limit"] == 1
    #        assert scheduled_task_meta["offset"] == 0

    def test_get_scheduled_task(self, st: SolidarityTech, requests_mock: Mocker) -> None:
        """Verify that :meth:`~parsons.solidarity_tech.SolidarityTech.get_scheduled_task` makes the appropriate calls."""
        resource_id = 960
        endpoint_url = f"{st.api_url}{ENDPOINT}/{resource_id}"
        _ = requests_mock.get(endpoint_url, json={"data": {}, "meta": {}})

        _, _ = st.get_scheduled_task(resource_id=resource_id)

        assert requests_mock.call_count == 1
        assert requests_mock.last_request is not None
        assert requests_mock.last_request.method == "GET"
        assert requests_mock.last_request.url == endpoint_url
