"""Tests for the Event RSVPs methods of :class:`~parsons.solidarity_tech.SolidarityTech`."""

from __future__ import annotations

from http import HTTPStatus
from typing import TYPE_CHECKING

import pytest

from parsons import Table
from parsons.solidarity_tech.datatypes import AttendanceStatus

if TYPE_CHECKING:
    from requests_mock import Mocker

    from parsons.solidarity_tech import SolidarityTech

ENDPOINT = "event_rsvps"


class TestGetEventRSVPs:
    @pytest.mark.vcr
    def test_get_event_rsvps_live(self, st: SolidarityTech) -> None:
        """Verify that :meth:`~parsons.solidarity_tech.SolidarityTech.get_event_rsvps` returns both a Table of results and the associated metadata."""
        email_senders, email_senders_meta = st.get_event_rsvps()

        assert isinstance(email_senders, Table)
        assert email_senders.name == "Solidarity Tech Event RSVPs"
        assert len(email_senders) > 0
        assert isinstance(email_senders[0], dict)

        assert isinstance(email_senders_meta, dict)
        assert email_senders_meta["total_count"] > 0
        assert email_senders_meta["limit"] == 20
        assert email_senders_meta["offset"] == 0

    def test_get_event_rsvps_minimal(self, st: SolidarityTech, requests_mock: Mocker) -> None:
        """Verify that :meth:`~parsons.solidarity_tech.SolidarityTech.get_event_rsvps` makes the appropriate calls."""
        endpoint_url = (
            f"{st.api_url}{ENDPOINT}?_limit=20&_offset=0&_since=0&full_user_payload=False"
        )
        _ = requests_mock.get(endpoint_url, json={"data": [{}], "meta": {}})

        _, _ = st.get_event_rsvps()

        assert requests_mock.call_count == 1
        assert requests_mock.last_request is not None
        assert requests_mock.last_request.method == "GET"
        assert requests_mock.last_request.url == endpoint_url

    def test_get_event_rsvps_maximal(self, st: SolidarityTech, requests_mock: Mocker) -> None:
        """Verify that :meth:`~parsons.solidarity_tech.SolidarityTech.get_event_rsvps` makes the appropriate calls."""
        limit = 30
        offset = 5
        since = 1788075104
        event_id = 16284
        session_id = 41073
        full_user_payload = True
        endpoint_url = f"{st.api_url}{ENDPOINT}?_limit={limit}&_offset={offset}&_since={since}&full_user_payload={full_user_payload}&event_id={event_id}&session_id={session_id}"
        _ = requests_mock.get(endpoint_url, json={"data": [{}], "meta": {}})

        _, _ = st.get_event_rsvps(
            limit=limit,
            offset=offset,
            since=since,
            event_id=event_id,
            session_id=session_id,
            full_user_payload=full_user_payload,
        )

        assert requests_mock.call_count == 1
        assert requests_mock.last_request is not None
        assert requests_mock.last_request.method == "GET"
        assert requests_mock.last_request.url == endpoint_url


class TestGetEventRSVP:
    @pytest.mark.vcr
    def test_get_event_rsvp_live(self, st: SolidarityTech) -> None:
        """Verify that :meth:`~parsons.solidarity_tech.SolidarityTech.get_event_rsvp` returns both a Table of results and the associated metadata."""
        resource_id = 378949
        event_rsvp, event_rsvp_meta = st.get_event_rsvp(resource_id=resource_id)

        assert isinstance(event_rsvp, dict)
        assert event_rsvp["id"] == resource_id

        assert isinstance(event_rsvp_meta, dict)
        assert event_rsvp_meta["total_count"] > 0
        assert event_rsvp_meta["limit"] == 1
        assert event_rsvp_meta["offset"] == 0

    def test_get_event_rsvp(self, st: SolidarityTech, requests_mock: Mocker) -> None:
        """Verify that :meth:`~parsons.solidarity_tech.SolidarityTech.get_event_rsvp` makes the appropriate calls."""
        resource_id = 295857
        endpoint_url = f"{st.api_url}{ENDPOINT}/{resource_id}?full_user_payload=False"
        _ = requests_mock.get(endpoint_url, json={"data": [{}], "meta": {}})

        _, _ = st.get_event_rsvp(resource_id=resource_id)

        assert requests_mock.call_count == 1
        assert requests_mock.last_request is not None
        assert requests_mock.last_request.method == "GET"
        assert requests_mock.last_request.url == endpoint_url


class TestCreateEventAttendance:
    @pytest.mark.vcr
    def test_create_event_rsvp_live(self, st: SolidarityTech) -> None:
        """Verify that :meth:`~parsons.solidarity_tech.SolidarityTech.create_event_rsvp` returns the data for the created event rsvp."""
        event_id = 1471
        event_session_id = 1316
        user_id = 1928273
        is_attending = AttendanceStatus.YES
        agent_user_id = 1191722
        event_rsvp = st.create_event_rsvp(
            event_id=event_id,
            event_session_id=event_session_id,
            user_id=user_id,
            is_attending=is_attending,
            agent_user_id=agent_user_id,
        )

        assert isinstance(event_rsvp["id"], int)
        assert event_rsvp["event_id"] == event_id
        assert event_rsvp["event_session_id"] == event_session_id
        assert event_rsvp["user_id"] == user_id
        assert event_rsvp["is_attending"] == is_attending
        assert event_rsvp["agent_user_id"] == agent_user_id

    def test_create_event_rsvp_minimal(self, st: SolidarityTech, requests_mock: Mocker) -> None:
        """Verify that :meth:`~parsons.solidarity_tech.SolidarityTech.create_event_rsvp` makes the appropriate calls."""
        event_id = 1191722
        event_session_id = 2192958
        is_attending = AttendanceStatus.MAYBE
        agent_user_id = 8352
        endpoint_url = f"{st.api_url}{ENDPOINT}"
        _ = requests_mock.post(endpoint_url, status_code=HTTPStatus.CREATED, json={"data": {}})

        _ = st.create_event_rsvp(
            event_id=event_id,
            event_session_id=event_session_id,
            is_attending=is_attending,
            agent_user_id=agent_user_id,
        )

        assert requests_mock.call_count == 1
        assert requests_mock.last_request is not None
        assert requests_mock.last_request.method == "POST"
        assert requests_mock.last_request.url == endpoint_url
        assert requests_mock.last_request.json()["event_id"] == event_id
        assert requests_mock.last_request.json()["event_session_id"] == event_session_id
        assert requests_mock.last_request.json()["is_attending"] == is_attending
        assert requests_mock.last_request.json()["agent_user_id"] == agent_user_id

    def test_create_event_rsvp_maximal(self, st: SolidarityTech, requests_mock: Mocker) -> None:
        """Verify that :meth:`~parsons.solidarity_tech.SolidarityTech.create_event_rsvp` makes the appropriate calls."""
        event_id = 1191722
        event_session_id = 2192958
        user_id = 2952
        is_attending = AttendanceStatus.MAYBE
        is_confirmed = True
        agent_user_id = 8352
        source = "chat"
        source_system = "web"
        skip_email_confirmation = True
        endpoint_url = f"{st.api_url}{ENDPOINT}"
        _ = requests_mock.post(endpoint_url, status_code=HTTPStatus.CREATED, json={"data": {}})

        _ = st.create_event_rsvp(
            event_id=event_id,
            event_session_id=event_session_id,
            user_id=user_id,
            is_attending=is_attending,
            agent_user_id=agent_user_id,
            source=source,
            source_system=source_system,
            is_confirmed=is_confirmed,
            skip_email_confirmation=skip_email_confirmation,
        )

        assert requests_mock.call_count == 1
        assert requests_mock.last_request is not None
        assert requests_mock.last_request.method == "POST"
        assert requests_mock.last_request.url == endpoint_url
        assert requests_mock.last_request.json()["event_id"] == event_id
        assert requests_mock.last_request.json()["event_session_id"] == event_session_id
        assert requests_mock.last_request.json()["user_id"] == user_id
        assert requests_mock.last_request.json()["is_attending"] == is_attending
        assert requests_mock.last_request.json()["agent_user_id"] == agent_user_id
        assert requests_mock.last_request.json()["source"] == source
        assert requests_mock.last_request.json()["source_system"] == source_system
        assert requests_mock.last_request.json()["is_confirmed"] == is_confirmed
        assert (
            requests_mock.last_request.json()["skip_email_confirmation"] == skip_email_confirmation
        )


class TestUpdateEventAttendance:
    @pytest.mark.vcr
    def test_update_event_rsvp_live(self, st: SolidarityTech) -> None:
        """Verify that :meth:`~parsons.solidarity_tech.SolidarityTech.update_event_rsvp` returns the data for the updated event rsvp."""
        resource_id = 74398
        is_attending = AttendanceStatus.NO

        event_rsvp = st.update_event_rsvp(resource_id=resource_id, is_attending=is_attending)

        assert event_rsvp["id"] == resource_id
        assert event_rsvp["is_attending"] == is_attending

    def test_update_event_rsvp(self, st: SolidarityTech, requests_mock: Mocker) -> None:
        """Verify that :meth:`~parsons.solidarity_tech.SolidarityTech.update_event_rsvp` makes the appropriate calls."""
        resource_id = 50417
        endpoint_url = f"{st.api_url}{ENDPOINT}/{resource_id}"
        _ = requests_mock.put(endpoint_url, json={"data": {}})

        _ = st.update_event_rsvp(resource_id=resource_id)

        assert requests_mock.call_count == 1
        assert requests_mock.last_request is not None
        assert requests_mock.last_request.method == "PUT"
        assert requests_mock.last_request.url == endpoint_url


class TestDeleteEventAttendance:
    @pytest.mark.vcr
    def test_delete_event_rsvp_live(self, st: SolidarityTech) -> None:
        """Verify that :meth:`~parsons.solidarity_tech.SolidarityTech.delete_event_rsvp` returns the data for the updated event rsvp."""
        resource_id = 72101

        event_rsvp = st.delete_event_rsvp(resource_id=resource_id)

        assert event_rsvp

    def test_delete_event_rsvp(self, st: SolidarityTech, requests_mock: Mocker) -> None:
        """Verify that :meth:`~parsons.solidarity_tech.SolidarityTech.delete_event_rsvp` makes the appropriate calls."""
        resource_id = 50417
        endpoint_url = f"{st.api_url}{ENDPOINT}/{resource_id}"
        _ = requests_mock.delete(endpoint_url, json={"data": {}})

        _ = st.delete_event_rsvp(resource_id=resource_id)

        assert requests_mock.call_count == 1
        assert requests_mock.last_request is not None
        assert requests_mock.last_request.method == "DELETE"
        assert requests_mock.last_request.url == endpoint_url
