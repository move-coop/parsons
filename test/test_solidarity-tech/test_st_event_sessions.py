"""Tests for the Event Sessions methods of :class:`~parsons.solidarity_tech.SolidarityTech`."""

from __future__ import annotations

from http import HTTPStatus
from typing import TYPE_CHECKING

import pytest

from parsons import Table
from parsons.solidarity_tech.datatypes import EventType, LocationDataData

if TYPE_CHECKING:
    from collections.abc import Callable

    from requests_mock import Mocker

    from parsons.solidarity_tech import SolidarityTech

ENDPOINT = "event_sessions"


class TestGetEventSessions:
    @pytest.mark.vcr
    def test_get_event_sessions_live(self, st: SolidarityTech) -> None:
        """Verify that :meth:`~parsons.solidarity_tech.SolidarityTech.get_event_sessions` returns both a Table of results and the associated metadata."""
        event_session, event_session_meta = st.get_event_sessions(event_id=30053)

        assert isinstance(event_session, Table)
        assert event_session.name == "Solidarity Tech Event Sessions"
        assert len(event_session) > 0
        assert isinstance(event_session[0], dict)

        assert isinstance(event_session_meta, dict)
        assert event_session_meta["total_count"] > 0
        assert event_session_meta["limit"] == 20
        assert event_session_meta["offset"] == 0

    @pytest.mark.vcr
    def test_get_event_sessions_live_count(self, st: SolidarityTech) -> None:
        """Verify that :meth:`~parsons.solidarity_tech.SolidarityTech.get_event_sessions` returns the count of event sessions when `count` is ``True``."""
        session_count = st.get_event_sessions(count=True)

        assert isinstance(session_count, int)

    def test_get_event_sessions_minimal(self, st: SolidarityTech, requests_mock: Mocker) -> None:
        """Verify that :meth:`~parsons.solidarity_tech.SolidarityTech.get_event_sessions` makes the appropriate calls."""
        endpoint_url = f"{st.api_url}{ENDPOINT}?_limit=20&_offset=0&_since=0&event_id=0"
        _ = requests_mock.get(endpoint_url, json={"data": [{}], "meta": {}})

        _, _ = st.get_event_sessions()

        assert requests_mock.call_count == 1
        assert requests_mock.last_request is not None
        assert requests_mock.last_request.method == "GET"
        assert requests_mock.last_request.url == endpoint_url

    @pytest.mark.parametrize("tags", ["book_club", ["book_club"]], ids=["string", "list"])
    def test_get_event_sessions_maximal(
        self, st: SolidarityTech, requests_mock: Mocker, tags: str | list[str]
    ) -> None:
        """Verify that :meth:`~parsons.solidarity_tech.SolidarityTech.get_event_sessions` makes the appropriate calls."""
        limit = 30
        offset = 5
        since = 1788075104
        event_id = 16284
        upcoming = True
        starts_after = 24792
        starts_before = 20857289
        chapter_id = 208
        event_tags = tags
        include_rsvp_counts = False
        include_confirmed_counts = True
        include_hosts = True
        count = False
        query_formatted_event_tags = (
            event_tags if isinstance(event_tags, str) else ",".join(str(tag) for tag in event_tags)
        )
        endpoint_url = f"{st.api_url}{ENDPOINT}?_limit={limit}&_offset={offset}&_since={since}&event_id={event_id}&upcoming={upcoming}&starts_after={starts_after}&starts_before={starts_before}&chapter_id={chapter_id}&event_tags={query_formatted_event_tags}&include_rsvp_counts={include_rsvp_counts}&include_confirmed_counts={include_confirmed_counts}&include_hosts={include_hosts}"
        _ = requests_mock.get(endpoint_url, json={"data": [{}], "meta": {}})

        _, _ = st.get_event_sessions(
            limit=limit,
            offset=offset,
            since=since,
            event_id=event_id,
            upcoming=upcoming,
            starts_after=starts_after,
            starts_before=starts_before,
            chapter_id=chapter_id,
            event_tags=event_tags,
            include_rsvp_counts=include_rsvp_counts,
            include_confirmed_counts=include_confirmed_counts,
            include_hosts=include_hosts,
            count=count,
        )

        assert requests_mock.call_count == 1
        assert requests_mock.last_request is not None
        assert requests_mock.last_request.method == "GET"
        assert requests_mock.last_request.url == endpoint_url


class TestGetEventSession:
    @pytest.mark.vcr
    def test_get_event_session_live(self, st: SolidarityTech) -> None:
        """Verify that :meth:`~parsons.solidarity_tech.SolidarityTech.get_event_session` returns both a Table of results and the associated metadata."""
        resource_id = 88127
        event_session, event_session_meta = st.get_event_session(resource_id=resource_id)

        assert isinstance(event_session, dict)
        assert event_session["id"] == resource_id

        assert isinstance(event_session_meta, dict)
        assert event_session_meta["total_count"] > 0
        assert event_session_meta["limit"] == 1
        assert event_session_meta["offset"] == 0

    def test_get_event_session(self, st: SolidarityTech, requests_mock: Mocker) -> None:
        """Verify that :meth:`~parsons.solidarity_tech.SolidarityTech.get_event_session` makes the appropriate calls."""
        resource_id = 295857
        endpoint_url = f"{st.api_url}{ENDPOINT}/{resource_id}?include_hosts=False"
        _ = requests_mock.get(endpoint_url, json={"data": {}, "meta": {}})

        _, _ = st.get_event_session(resource_id=resource_id)

        assert requests_mock.call_count == 1
        assert requests_mock.last_request is not None
        assert requests_mock.last_request.method == "GET"
        assert requests_mock.last_request.url == endpoint_url


class TestCreateEventSession:
    @pytest.mark.vcr
    def test_create_event_session_live(
        self, st: SolidarityTech, format_ts: Callable[[int, int], str]
    ) -> None:
        """Verify that :meth:`~parsons.solidarity_tech.SolidarityTech.create_event_session` returns the data for the created event session."""
        event_id = 30053
        start_time = 1791809951
        end_time = 1791817151
        title = "test event"

        event_session = st.create_event_session(
            event_id=event_id, start_time=start_time, end_time=end_time, title=title
        )

        assert isinstance(event_session["id"], int)
        assert event_session["mobilize_event_id"] == event_id
        assert event_session["start_time"] == format_ts(start_time, -7)
        assert event_session["end_time"] == format_ts(end_time, -7)
        assert event_session["title"] == title

    def test_create_event_session_minimal(self, st: SolidarityTech, requests_mock: Mocker) -> None:
        """Verify that :meth:`~parsons.solidarity_tech.SolidarityTech.create_event_session` makes the appropriate calls."""
        event_id = 30053
        start_time = 1791809951
        end_time = 1791817151
        title = "test event"

        endpoint_url = f"{st.api_url}{ENDPOINT}"
        _ = requests_mock.post(endpoint_url, status_code=HTTPStatus.CREATED, json={"data": {}})

        _ = st.create_event_session(
            event_id=event_id, start_time=start_time, end_time=end_time, title=title
        )

        assert requests_mock.call_count == 1
        assert requests_mock.last_request is not None
        assert requests_mock.last_request.method == "POST"
        assert requests_mock.last_request.url == endpoint_url
        assert requests_mock.last_request.json()["event_id"] == event_id
        assert requests_mock.last_request.json()["start_time"] == start_time
        assert requests_mock.last_request.json()["end_time"] == end_time
        assert requests_mock.last_request.json()["title"] == title

    def test_create_event_session_maximal(self, st: SolidarityTech, requests_mock: Mocker) -> None:
        """Verify that :meth:`~parsons.solidarity_tech.SolidarityTech.create_event_session` makes the appropriate calls."""
        event_id = 30053
        start_time = 1791809951
        end_time = 1791817151
        title = "test event"
        event_type = EventType.VIRTUAL
        location_name = "City of Portland"
        location_data: LocationDataData = {
            "address_city": "Portland",
            "full_address": "389 Congress Street, Portland, ME, USA",
            "address_line_1": "389 Congress Street",
            "address_country": "USA",
            "address_postal_code": "04101",
        }
        location_address = location_data["full_address"]
        note = "this event will be great"
        max_capacity = 50
        tags = ["public testimony"]

        endpoint_url = f"{st.api_url}{ENDPOINT}"
        _ = requests_mock.post(endpoint_url, status_code=HTTPStatus.CREATED, json={"data": {}})

        _ = st.create_event_session(
            event_id=event_id,
            start_time=start_time,
            end_time=end_time,
            title=title,
            event_type=event_type,
            location_name=location_name,
            location_data=location_data,
            location_address=location_address,
            note=note,
            max_capacity=max_capacity,
            tags=tags,
        )

        assert requests_mock.call_count == 1
        assert requests_mock.last_request is not None
        assert requests_mock.last_request.method == "POST"
        assert requests_mock.last_request.url == endpoint_url
        assert requests_mock.last_request.json()["event_id"] == event_id
        assert requests_mock.last_request.json()["start_time"] == start_time
        assert requests_mock.last_request.json()["end_time"] == end_time
        assert requests_mock.last_request.json()["title"] == title
        assert requests_mock.last_request.json()["event_type"] == event_type
        assert requests_mock.last_request.json()["location_name"] == location_name
        assert requests_mock.last_request.json()["location_data"] == location_data
        assert requests_mock.last_request.json()["location_address"] == location_address
        assert requests_mock.last_request.json()["note"] == note
        assert requests_mock.last_request.json()["max_capacity"] == max_capacity
        assert requests_mock.last_request.json()["tags"] == tags


class TestUpdateEventSession:
    @pytest.mark.vcr
    def test_update_event_session_live(self, st: SolidarityTech) -> None:
        """Verify that :meth:`~parsons.solidarity_tech.SolidarityTech.update_event_session` returns the data for the updated event session."""
        resource_id = 88127
        note = "updated event note"

        event_session = st.update_event_session(resource_id=resource_id, note=note)

        assert event_session["id"] == resource_id
        assert event_session["note"] == note

    def test_update_event_session(self, st: SolidarityTech, requests_mock: Mocker) -> None:
        """Verify that :meth:`~parsons.solidarity_tech.SolidarityTech.update_event_session` makes the appropriate calls."""
        resource_id = 50417
        endpoint_url = f"{st.api_url}{ENDPOINT}/{resource_id}"
        _ = requests_mock.put(endpoint_url, json={"data": {}})

        _ = st.update_event_session(resource_id=resource_id)

        assert requests_mock.call_count == 1
        assert requests_mock.last_request is not None
        assert requests_mock.last_request.method == "PUT"
        assert requests_mock.last_request.url == endpoint_url


class TestDeleteEventSession:
    @pytest.mark.vcr
    def test_delete_event_session_live(self, st: SolidarityTech) -> None:
        """Verify that :meth:`~parsons.solidarity_tech.SolidarityTech.delete_event_session` returns the data for the updated event session."""
        resource_id = 88127

        event_session = st.delete_event_session(resource_id=resource_id)

        assert event_session

    def test_delete_event_session(self, st: SolidarityTech, requests_mock: Mocker) -> None:
        """Verify that :meth:`~parsons.solidarity_tech.SolidarityTech.delete_event_session` makes the appropriate calls."""
        resource_id = 50417
        endpoint_url = f"{st.api_url}{ENDPOINT}/{resource_id}"
        _ = requests_mock.delete(endpoint_url, json={"data": {}})

        _ = st.delete_event_session(resource_id=resource_id)

        assert requests_mock.call_count == 1
        assert requests_mock.last_request is not None
        assert requests_mock.last_request.method == "DELETE"
        assert requests_mock.last_request.url == endpoint_url


class TestAddEventSessionHost:
    @pytest.mark.vcr
    def test_add_event_host_live(self, st: SolidarityTech) -> None:
        """Verify that :meth:`~parsons.solidarity_tech.SolidarityTech.add_event_host` returns the data for the created event session."""
        resource_id = 88127
        user_id = 1191722

        event_session = st.add_event_host(resource_id=resource_id, user_id=user_id)

        assert event_session["id"] == resource_id
        assert user_id in event_session["host_user_ids"]

    def test_add_event_host_minimal(self, st: SolidarityTech, requests_mock: Mocker) -> None:
        """Verify that :meth:`~parsons.solidarity_tech.SolidarityTech.add_event_host` makes the appropriate calls."""
        resource_id = 30053
        user_id = 29482
        endpoint_url = f"{st.api_url}{ENDPOINT}/{resource_id}/hosts"
        _ = requests_mock.post(endpoint_url, json={"data": {}})

        _ = st.add_event_host(resource_id=resource_id, user_id=user_id)

        assert requests_mock.call_count == 1
        assert requests_mock.last_request is not None
        assert requests_mock.last_request.method == "POST"
        assert requests_mock.last_request.url == endpoint_url
        assert requests_mock.last_request.json()["user_id"] == user_id


class TestRemoveEventSessionHost:
    @pytest.mark.vcr
    def test_remove_event_host_live(self, st: SolidarityTech) -> None:
        """Verify that :meth:`~parsons.solidarity_tech.SolidarityTech.remove_event_host` returns the data for the updated event session."""
        resource_id = 88127
        user_id = 1191722

        event_session = st.remove_event_host(resource_id=resource_id, user_id=user_id)

        assert event_session["id"] == resource_id
        assert user_id not in event_session["host_user_ids"]

    def test_remove_event_host(self, st: SolidarityTech, requests_mock: Mocker) -> None:
        """Verify that :meth:`~parsons.solidarity_tech.SolidarityTech.remove_event_host` makes the appropriate calls."""
        resource_id = 30053
        user_id = 29482
        endpoint_url = f"{st.api_url}{ENDPOINT}/{resource_id}/hosts/{user_id}"
        _ = requests_mock.delete(endpoint_url, json={"data": {}})

        _ = st.remove_event_host(resource_id=resource_id, user_id=user_id)

        assert requests_mock.call_count == 1
        assert requests_mock.last_request is not None
        assert requests_mock.last_request.method == "DELETE"
        assert requests_mock.last_request.url == endpoint_url
