"""Tests for the Event Attendances methods of :class:`~parsons.solidarity_tech.SolidarityTech`."""

from __future__ import annotations

from http import HTTPStatus
from typing import TYPE_CHECKING

import pytest

from parsons import Table

if TYPE_CHECKING:
    from requests_mock import Mocker

    from parsons.solidarity_tech import SolidarityTech

ENDPOINT = "event_attendances"


class TestGetEventAttendances:
    @pytest.mark.vcr
    def test_get_event_attendances_live(self, st: SolidarityTech) -> None:
        """Verify that :meth:`~parsons.solidarity_tech.SolidarityTech.get_event_attendances` returns both a Table of results and the associated metadata."""
        email_senders, email_senders_meta = st.get_event_attendances()

        assert isinstance(email_senders, Table)
        assert email_senders.name == "Solidarity Tech Event Attendances"
        assert len(email_senders) > 0
        assert isinstance(email_senders[0], dict)

        assert isinstance(email_senders_meta, dict)
        assert email_senders_meta["total_count"] > 0
        assert email_senders_meta["limit"] == 20
        assert email_senders_meta["offset"] == 0

    def test_get_event_attendances_minimal(self, st: SolidarityTech, requests_mock: Mocker) -> None:
        """Verify that :meth:`~parsons.solidarity_tech.SolidarityTech.get_event_attendances` makes the appropriate calls."""
        endpoint_url = f"{st.api_url}{ENDPOINT}?_limit=20&_offset=0&_since=0"
        _ = requests_mock.get(endpoint_url, json={"data": [{}], "meta": {}})

        _, _ = st.get_event_attendances()

        assert requests_mock.call_count == 1
        assert requests_mock.last_request is not None
        assert requests_mock.last_request.method == "GET"
        assert requests_mock.last_request.url == endpoint_url

    def test_get_event_attendances_maximal(self, st: SolidarityTech, requests_mock: Mocker) -> None:
        """Verify that :meth:`~parsons.solidarity_tech.SolidarityTech.get_event_attendances` makes the appropriate calls."""
        limit = 30
        offset = 5
        since = 1788075104
        event_id = 16284
        session_id = 41073
        endpoint_url = f"{st.api_url}{ENDPOINT}?_limit={limit}&_offset={offset}&_since={since}&event_id={event_id}&session_id={session_id}"
        _ = requests_mock.get(endpoint_url, json={"data": [{}], "meta": {}})

        _, _ = st.get_event_attendances(
            limit=limit, offset=offset, since=since, event_id=event_id, session_id=session_id
        )

        assert requests_mock.call_count == 1
        assert requests_mock.last_request is not None
        assert requests_mock.last_request.method == "GET"
        assert requests_mock.last_request.url == endpoint_url


class TestCreateEventAttendance:
    @pytest.mark.vcr
    def test_create_event_attendance_live(self, st: SolidarityTech) -> None:
        """Verify that :meth:`~parsons.solidarity_tech.SolidarityTech.create_event_attendance` returns the data for the created event attendance."""
        event_id = 1471
        event_session_id = 1316
        user_id = 1191722
        attended = False
        event_attendance = st.create_event_attendance(
            event_id=event_id, event_session_id=event_session_id, user_id=user_id, attended=attended
        )

        assert isinstance(event_attendance["id"], int)
        assert event_attendance["event_id"] == event_id
        assert event_attendance["event_session_id"] == event_session_id
        assert event_attendance["user_id"] == user_id
        assert event_attendance["attended"] == attended

    def test_create_event_attendance(self, st: SolidarityTech, requests_mock: Mocker) -> None:
        """Verify that :meth:`~parsons.solidarity_tech.SolidarityTech.create_event_attendance` makes the appropriate calls."""
        event_id = 1191722
        event_session_id = 2192958
        user_id = 2952
        attended = True
        endpoint_url = f"{st.api_url}{ENDPOINT}"
        _ = requests_mock.post(endpoint_url, status_code=HTTPStatus.CREATED, json={"data": {}})

        _ = st.create_event_attendance(
            event_id=event_id, event_session_id=event_session_id, user_id=user_id, attended=attended
        )

        assert requests_mock.call_count == 1
        assert requests_mock.last_request is not None
        assert requests_mock.last_request.method == "POST"
        assert requests_mock.last_request.url == endpoint_url
        assert requests_mock.last_request.json()["user_id"] == user_id
        assert requests_mock.last_request.json()["event_session_id"] == event_session_id
        assert requests_mock.last_request.json()["user_id"] == user_id
        assert requests_mock.last_request.json()["attended"] == attended


class TestDeleteEventAttendance:
    @pytest.mark.vcr
    def test_delete_event_attendance_live(self, st: SolidarityTech) -> None:
        """Verify that :meth:`~parsons.solidarity_tech.SolidarityTech.delete_event_attendance` returns the data for the updated event attendance."""
        resource_id = 99573

        event_attendance = st.delete_event_attendance(resource_id=resource_id)

        assert event_attendance

    def test_delete_event_attendance(self, st: SolidarityTech, requests_mock: Mocker) -> None:
        """Verify that :meth:`~parsons.solidarity_tech.SolidarityTech.delete_event_attendance` makes the appropriate calls."""
        resource_id = 50417
        endpoint_url = f"{st.api_url}{ENDPOINT}/{resource_id}"
        _ = requests_mock.delete(endpoint_url, json={"data": {}})

        _ = st.delete_event_attendance(resource_id=resource_id)

        assert requests_mock.call_count == 1
        assert requests_mock.last_request is not None
        assert requests_mock.last_request.method == "DELETE"
        assert requests_mock.last_request.url == endpoint_url
