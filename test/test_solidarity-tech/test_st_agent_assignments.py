"""Test cases for the Agent Assignments methods of the :class:`~parsons.solidarity_tech.SolidarityTech` client."""

from __future__ import annotations

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
    def test_agent_assignments_live(self, st: SolidarityTech) -> None:
        """Verify that :meth:`~parsons.solidarity_tech.SolidarityTech.get_agent_assignments` returns both a Table of results and the associated metadata."""
        agent_assignments, agent_assignments_meta = st.get_agent_assignments()

        assert isinstance(agent_assignments, Table)
        assert len(agent_assignments) > 0
        assert isinstance(agent_assignments[0], dict)

        assert isinstance(agent_assignments_meta, dict)
        assert agent_assignments_meta["total_count"] > 0
        assert agent_assignments_meta["limit"] == 20
        assert agent_assignments_meta["offset"] == 0

    def test_agent_assignments_minimal(self, st: SolidarityTech, requests_mock: Mocker) -> None:
        """Verify that :meth:`~parsons.solidarity_tech.SolidarityTech.agent_assignments` makes the appropriate calls."""
        endpoint_url = f"{st.api_url}{ENDPOINT}"
        _ = requests_mock.get(endpoint_url, json={"data": [{}], "meta": {}})
        _, _ = st.get_agent_assignments()

        assert requests_mock.call_count == 1
        assert requests_mock.last_request is not None
        assert requests_mock.last_request.method == "GET"
        assert requests_mock.last_request.url == f"{endpoint_url}?_limit=20&_offset=0&_since=0"

    def test_agent_assignments_maximal(self, st: SolidarityTech, requests_mock: Mocker) -> None:
        """Verify that :meth:`~parsons.solidarity_tech.SolidarityTech.agent_assignments` makes the appropriate calls."""
        endpoint_url = f"{st.api_url}{ENDPOINT}"
        _ = requests_mock.get(endpoint_url, json={"data": [{}], "meta": {}})
        _, _ = st.get_agent_assignments(
            limit=30,
            offset=5,
            since=1788075104,
            user_id=3295823659,
            agent_user_id=12350912375,
        )

        assert requests_mock.call_count == 1
        assert requests_mock.last_request is not None
        assert requests_mock.last_request.method == "GET"
        assert (
            requests_mock.last_request.url
            == f"{endpoint_url}?_limit=30&_offset=5&_since=1788075104&user_id=3295823659&agent_user_id=12350912375"
        )


class TestGetAgentAssignment:
    @pytest.mark.vcr
    def test_agent_assignment_live(self, st: SolidarityTech) -> None:
        """Verify that :meth:`~parsons.solidarity_tech.SolidarityTech.get_agent_assignments` returns both a Table of results and the associated metadata."""
        agent_assignment, agent_assignment_meta = st.get_agent_assignment(resource_id=478171)

        assert isinstance(agent_assignment, dict)

        assert isinstance(agent_assignment_meta, dict)
        assert agent_assignment_meta["total_count"] == 1
        assert agent_assignment_meta["limit"] == 1
        assert agent_assignment_meta["offset"] == 0

    def test_agent_assignment_minimal(self, st: SolidarityTech, requests_mock: Mocker) -> None:
        """Verify that :meth:`~parsons.solidarity_tech.SolidarityTech.agent_assignments` makes the appropriate calls."""
        endpoint_url = f"{st.api_url}{ENDPOINT}/3598327"
        _ = requests_mock.get(endpoint_url, json={"data": [{}], "meta": {}})
        _, _ = st.get_agent_assignment(resource_id=3598327)

        assert requests_mock.call_count == 1
        assert requests_mock.last_request is not None
        assert requests_mock.last_request.method == "GET"
        assert requests_mock.last_request.url == endpoint_url

    def test_agent_assignment_not_found(self, st: SolidarityTech, requests_mock: Mocker) -> None:
        """Verify that :meth:`~parsons.solidarity_tech.SolidarityTech.agent_assignments` makes the appropriate calls."""
        endpoint_url = f"{st.api_url}{ENDPOINT}/99"
        _ = requests_mock.get(endpoint_url, status_code=404, reason="Agent assignment not found")
        with pytest.raises(STFailedResponseError, match="Agent assignment not found"):
            _, _ = st.get_agent_assignment(resource_id=99)

        assert requests_mock.call_count == 1
        assert requests_mock.last_request is not None
        assert requests_mock.last_request.method == "GET"
        assert requests_mock.last_request.url == endpoint_url
