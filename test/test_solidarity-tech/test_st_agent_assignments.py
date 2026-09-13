"""Tests for the Agent Assignments methods of :class:`~parsons.solidarity_tech.SolidarityTech`."""

from __future__ import annotations

from http import HTTPStatus
from typing import TYPE_CHECKING

import pytest

from parsons import Table
from parsons.solidarity_tech.exceptions import STFailedResponseError

if TYPE_CHECKING:
    from requests_mock import Mocker

    from parsons.solidarity_tech import SolidarityTech

ENDPOINT = "agent_assignments"


class TestGetAgentAssignments:
    @pytest.mark.vcr
    def test_get_agent_assignments_live(self, st: SolidarityTech) -> None:
        """Verify that :meth:`~parsons.solidarity_tech.SolidarityTech.get_agent_assignments` returns both a Table of results and the associated metadata."""
        agent_assignments, agent_assignments_meta = st.get_agent_assignments()

        assert isinstance(agent_assignments, Table)
        assert agent_assignments.name == "Solidarity Tech Agent Assignments"
        assert len(agent_assignments) > 0
        assert isinstance(agent_assignments[0], dict)

        assert isinstance(agent_assignments_meta, dict)
        assert agent_assignments_meta["total_count"] > 0
        assert agent_assignments_meta["limit"] == 20
        assert agent_assignments_meta["offset"] == 0

    def test_get_agent_assignments_minimal(self, st: SolidarityTech, requests_mock: Mocker) -> None:
        """Verify that :meth:`~parsons.solidarity_tech.SolidarityTech.get_agent_assignments` makes the appropriate calls."""
        endpoint_url = f"{st.api_url}{ENDPOINT}"
        _ = requests_mock.get(endpoint_url, json={"data": [{}], "meta": {}})

        _, _ = st.get_agent_assignments()

        assert requests_mock.call_count == 1
        assert requests_mock.last_request is not None
        assert requests_mock.last_request.method == "GET"
        assert requests_mock.last_request.url == f"{endpoint_url}?_limit=20&_offset=0&_since=0"

    def test_get_agent_assignments_maximal(self, st: SolidarityTech, requests_mock: Mocker) -> None:
        """Verify that :meth:`~parsons.solidarity_tech.SolidarityTech.get_agent_assignments` makes the appropriate calls."""
        limit = 30
        offset = 5
        since = 1788075104
        user_id = 3295823659
        agent_user_id = 12350912375
        endpoint_url = f"{st.api_url}{ENDPOINT}"
        _ = requests_mock.get(endpoint_url, json={"data": [{}], "meta": {}})

        _, _ = st.get_agent_assignments(
            limit=limit,
            offset=offset,
            since=since,
            user_id=user_id,
            agent_user_id=agent_user_id,
        )

        assert requests_mock.call_count == 1
        assert requests_mock.last_request is not None
        assert requests_mock.last_request.method == "GET"
        assert (
            requests_mock.last_request.url
            == f"{endpoint_url}?_limit={limit}&_offset={offset}&_since={since}&user_id={user_id}&agent_user_id={agent_user_id}"
        )


class TestGetAgentAssignment:
    @pytest.mark.vcr
    def test_get_agent_assignment_live(self, st: SolidarityTech) -> None:
        """Verify that :meth:`~parsons.solidarity_tech.SolidarityTech.get_agent_assignment` returns both a Table of results and the associated metadata."""
        resource_id = 478171
        agent_assignment, agent_assignment_meta = st.get_agent_assignment(resource_id=resource_id)

        assert isinstance(agent_assignment, dict)
        assert agent_assignment["id"] == resource_id

        assert isinstance(agent_assignment_meta, dict)
        assert agent_assignment_meta["total_count"] == 1
        assert agent_assignment_meta["limit"] == 1
        assert agent_assignment_meta["offset"] == 0

    def test_get_agent_assignment(self, st: SolidarityTech, requests_mock: Mocker) -> None:
        """Verify that :meth:`~parsons.solidarity_tech.SolidarityTech.get_agent_assignment` makes the appropriate calls."""
        resource_id = 3598327
        endpoint_url = f"{st.api_url}{ENDPOINT}/{resource_id}"
        _ = requests_mock.get(endpoint_url, json={"data": [{}], "meta": {}})

        _, _ = st.get_agent_assignment(resource_id=resource_id)

        assert requests_mock.call_count == 1
        assert requests_mock.last_request is not None
        assert requests_mock.last_request.method == "GET"
        assert requests_mock.last_request.url == endpoint_url

    def test_get_agent_assignment_not_found(
        self, st: SolidarityTech, requests_mock: Mocker
    ) -> None:
        """Verify that :meth:`~parsons.solidarity_tech.SolidarityTech.get_agent_assignment` makes the appropriate calls."""
        endpoint_url = f"{st.api_url}{ENDPOINT}/99"
        _ = requests_mock.get(
            endpoint_url,
            status_code=HTTPStatus.NOT_FOUND,
            reason="Agent assignment not found",
        )

        with pytest.raises(STFailedResponseError, match="Agent assignment not found"):
            _, _ = st.get_agent_assignment(resource_id=99)

        assert requests_mock.call_count == 1
        assert requests_mock.last_request is not None
        assert requests_mock.last_request.method == "GET"
        assert requests_mock.last_request.url == endpoint_url


class TestCreateAgentAssignment:
    @pytest.mark.vcr
    def test_create_agent_assignment_live_success(self, st: SolidarityTech) -> None:
        """Verify that :meth:`~parsons.solidarity_tech.SolidarityTech.create_agent_assignment` returns the data for the created agent assignment."""
        user_id = 1191722
        agent_user_id = 2192958
        agent_assignment = st.create_agent_assignment(user_id=user_id, agent_user_id=agent_user_id)

        assert isinstance(agent_assignment["id"], int)
        assert agent_assignment["user_id"] == user_id
        assert agent_assignment["agent_user_id"] == agent_user_id

    @pytest.mark.vcr
    def test_create_agent_assignment_live_failure(self, st: SolidarityTech) -> None:
        """Verify that :meth:`~parsons.solidarity_tech.SolidarityTech.create_agent_assignment` fails if either user_id or agent_user_id is invalid."""
        with pytest.raises(STFailedResponseError, match="Not Found"):
            _ = st.create_agent_assignment(user_id=1191722, agent_user_id=99)

    def test_create_agent_assignment(self, st: SolidarityTech, requests_mock: Mocker) -> None:
        """Verify that :meth:`~parsons.solidarity_tech.SolidarityTech.create_agent_assignment` makes the appropriate calls."""
        user_id = 1191722
        agent_user_id = 2192958
        is_active = False
        endpoint_url = f"{st.api_url}{ENDPOINT}"
        _ = requests_mock.post(endpoint_url, status_code=HTTPStatus.CREATED, json={"data": {}})

        _ = st.create_agent_assignment(
            user_id=user_id, agent_user_id=agent_user_id, is_active=is_active
        )

        assert requests_mock.call_count == 1
        assert requests_mock.last_request is not None
        assert requests_mock.last_request.method == "POST"
        assert requests_mock.last_request.url == endpoint_url
        assert requests_mock.last_request.json()["user_id"] == user_id
        assert requests_mock.last_request.json()["agent_user_id"] == agent_user_id
        assert requests_mock.last_request.json()["is_active"] == is_active


class TestUpdateAgentAssignment:
    @pytest.mark.vcr
    def test_update_agent_assignment_live_success(self, st: SolidarityTech) -> None:
        """Verify that :meth:`~parsons.solidarity_tech.SolidarityTech.update_agent_assignment` returns the data for the updated agent assignment."""
        resource_id = 610872
        user_id = 1191722
        agent_user_id = 2192968

        agent_assignment = st.update_agent_assignment(
            resource_id=resource_id,
            user_id=user_id,
            agent_user_id=agent_user_id,
        )

        assert agent_assignment["id"] == resource_id
        assert agent_assignment["user_id"] == user_id
        assert agent_assignment["agent_user_id"] == agent_user_id

    @pytest.mark.vcr
    def test_update_agent_assignment_live_failure(self, st: SolidarityTech) -> None:
        """Verify that :meth:`~parsons.solidarity_tech.SolidarityTech.update_agent_assignment` fails if either user_id or agent_user_id is invalid."""
        with pytest.raises(STFailedResponseError, match="Not Found"):
            _ = st.update_agent_assignment(resource_id=295862, user_id=928642, agent_user_id=99)

    def test_update_agent_assignment(self, st: SolidarityTech, requests_mock: Mocker) -> None:
        """Verify that :meth:`~parsons.solidarity_tech.SolidarityTech.update_agent_assignment` makes the appropriate calls."""
        resource_id = 295862
        user_id = 1191722
        agent_user_id = 2192958
        is_active = False
        endpoint_url = f"{st.api_url}{ENDPOINT}/{resource_id}"
        _ = requests_mock.put(endpoint_url, json={"data": {}})

        _ = st.update_agent_assignment(
            resource_id=resource_id,
            user_id=user_id,
            agent_user_id=agent_user_id,
            is_active=is_active,
        )

        assert requests_mock.call_count == 1
        assert requests_mock.last_request is not None
        assert requests_mock.last_request.method == "PUT"
        assert requests_mock.last_request.url == endpoint_url
        assert requests_mock.last_request.json()["user_id"] == user_id
        assert requests_mock.last_request.json()["agent_user_id"] == agent_user_id
        assert requests_mock.last_request.json()["is_active"] == is_active


class TestDeleteAgentAssignment:
    pass
    #    @pytest.mark.vcr
    #    def test_delete_agent_assignment_live(self, st: SolidarityTech) -> None:
    #        """Verify that :meth:`~parsons.solidarity_tech.SolidarityTech.delete_agent_assignment` returns the data for the deleted agent assignment."""
    #        resource_id = 610872
    #        user_id = 1191722
    #        agent_user_id = 2192968
    #
    #        agent_assignment = st.delete_agent_assignment(
    #            resource_id=resource_id,
    #            user_id=user_id,
    #            agent_user_id=agent_user_id,
    #        )
    #
    #        assert agent_assignment["id"] == resource_id
    #        assert agent_assignment["user_id"] == user_id
    #        assert agent_assignment["agent_user_id"] == agent_user_id

    #    def test_delete_agent_assignment(self, st: SolidarityTech, requests_mock: Mocker) -> None:
    #        """Verify that :meth:`~parsons.solidarity_tech.SolidarityTech.delete_agent_assignment` makes the appropriate calls."""
    #        resource_id = 736213
    #        endpoint_url = f"{st.api_url}{ENDPOINT}/{resource_id}"
    #        _ = requests_mock.delete(endpoint_url, json={"data": {}})
    #
    #        _ = st.delete_agent_assignment(resource_id=resource_id)
    #
    #        assert requests_mock.call_count == 1
    #        assert requests_mock.last_request is not None
    #        assert requests_mock.last_request.method == "PUT"
    #        assert requests_mock.last_request.url == endpoint_url
