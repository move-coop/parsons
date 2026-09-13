"""Tests for the Events methods of :class:`~parsons.solidarity_tech.SolidarityTech`."""

from __future__ import annotations

from http import HTTPStatus
from typing import TYPE_CHECKING

import pytest

from parsons import Table
from parsons.solidarity_tech.datatypes import (
    AutomationStatusData,
    EventType,
    ScopeType,
)

if TYPE_CHECKING:
    from collections.abc import Callable

    from requests_mock import Mocker

    from parsons.solidarity_tech import SolidarityTech

ENDPOINT = "events"


class TestGetEvents:
    @pytest.mark.vcr
    def test_get_events_live(self, st: SolidarityTech) -> None:
        """Verify that :meth:`~parsons.solidarity_tech.SolidarityTech.get_events` returns both a Table of results and the associated metadata."""
        events = st.get_events()

        assert isinstance(events, Table)
        assert events.name == "Solidarity Tech Events"
        assert len(events) > 0
        assert isinstance(events[0], dict)

    def test_get_events_minimal(self, st: SolidarityTech, requests_mock: Mocker) -> None:
        """Verify that :meth:`~parsons.solidarity_tech.SolidarityTech.get_events` makes the appropriate calls."""
        endpoint_url = f"{st.api_url}{ENDPOINT}?_limit=20&_offset=0&_since=0"
        _ = requests_mock.get(endpoint_url, json={"data": [{}]})

        _ = st.get_events()

        assert requests_mock.call_count == 1
        assert requests_mock.last_request is not None
        assert requests_mock.last_request.method == "GET"
        assert requests_mock.last_request.url == endpoint_url

    def test_get_events_maximal(self, st: SolidarityTech, requests_mock: Mocker) -> None:
        """Verify that :meth:`~parsons.solidarity_tech.SolidarityTech.get_events` makes the appropriate calls."""
        limit = 30
        offset = 5
        since = 1788075104
        scope_id = 294762
        scope_type = ScopeType.CHAPTER
        endpoint_url = f"{st.api_url}{ENDPOINT}?_limit={limit}&_offset={offset}&_since={since}&scope_id={scope_id}&scope_type={scope_type.value}"
        _ = requests_mock.get(endpoint_url, json={"data": [{}]})

        _ = st.get_events(
            limit=limit,
            offset=offset,
            since=since,
            scope_id=scope_id,
            scope_type=scope_type,
        )

        assert requests_mock.call_count == 1
        assert requests_mock.last_request is not None
        assert requests_mock.last_request.method == "GET"
        assert requests_mock.last_request.url == endpoint_url


class TestGetEvent:
    @pytest.mark.vcr
    def test_get_event_live(self, st: SolidarityTech) -> None:
        """Verify that :meth:`~parsons.solidarity_tech.SolidarityTech.get_event` returns both a Table of results and the associated metadata."""
        resource_id = 25835
        event, event_meta = st.get_event(resource_id=resource_id)

        assert isinstance(event, dict)
        assert event["id"] == resource_id

        assert isinstance(event_meta, dict)
        assert event_meta["total_count"] > 0
        assert event_meta["limit"] == 1
        assert event_meta["offset"] == 0

    def test_get_event_minimal(self, st: SolidarityTech, requests_mock: Mocker) -> None:
        """Verify that :meth:`~parsons.solidarity_tech.SolidarityTech.get_event` makes the appropriate calls."""
        resource_id = 295857
        endpoint_url = f"{st.api_url}{ENDPOINT}/{resource_id}?include_hosts=False"
        _ = requests_mock.get(endpoint_url, json={"data": {}, "meta": {}})

        _, _ = st.get_event(resource_id=resource_id)

        assert requests_mock.call_count == 1
        assert requests_mock.last_request is not None
        assert requests_mock.last_request.method == "GET"
        assert requests_mock.last_request.url == endpoint_url

    def test_get_event_maximal(self, st: SolidarityTech, requests_mock: Mocker) -> None:
        """Verify that :meth:`~parsons.solidarity_tech.SolidarityTech.get_event` makes the appropriate calls."""
        resource_id = 295857
        include_hosts = True
        endpoint_url = f"{st.api_url}{ENDPOINT}/{resource_id}?include_hosts={include_hosts}"
        _ = requests_mock.get(endpoint_url, json={"data": {}, "meta": {}})

        _, _ = st.get_event(resource_id=resource_id, include_hosts=include_hosts)

        assert requests_mock.call_count == 1
        assert requests_mock.last_request is not None
        assert requests_mock.last_request.method == "GET"
        assert requests_mock.last_request.url == endpoint_url


class TestCreateEvent:
    @pytest.mark.vcr
    def test_create_event_live(
        self, st: SolidarityTech, format_ts: Callable[[int, int], str]
    ) -> None:
        """Verify that :meth:`~parsons.solidarity_tech.SolidarityTech.create_event` returns the data for the created event."""
        title = "newer test event"
        event_type = EventType.IN_PERSON
        start_time = 1791809955
        end_time = 1791817165
        scope_id = 960
        scope_type = ScopeType.CHAPTER

        event = st.create_event(
            title=title,
            event_type=event_type,
            start_time=start_time,
            end_time=end_time,
            scope_id=scope_id,
            scope_type=scope_type,
        )

        assert isinstance(event["id"], int)
        assert event["title"] == title
        assert event["event_type"] == event_type
        assert event["scope_id"] == scope_id
        assert event["scope_type"] == scope_type

        event_session = event["event_sessions"][0]
        assert event_session["start_time"] == format_ts(start_time, -4)
        assert event_session["end_time"] == format_ts(end_time, -4)

    def test_create_event_minimal(self, st: SolidarityTech, requests_mock: Mocker) -> None:
        """Verify that :meth:`~parsons.solidarity_tech.SolidarityTech.create_event` makes the appropriate calls."""
        title = "new test event"
        event_type = EventType.IN_PERSON
        start_time = 1791809951
        end_time = 1791817151
        scope_id = 960
        scope_type = ScopeType.CHAPTER

        endpoint_url = f"{st.api_url}{ENDPOINT}"
        _ = requests_mock.post(endpoint_url, status_code=HTTPStatus.CREATED, json={"data": {}})

        _ = st.create_event(
            title=title,
            event_type=event_type,
            start_time=start_time,
            end_time=end_time,
            scope_id=scope_id,
            scope_type=scope_type,
        )

        assert requests_mock.call_count == 1
        assert requests_mock.last_request is not None
        assert requests_mock.last_request.method == "POST"
        assert requests_mock.last_request.url == endpoint_url
        assert requests_mock.last_request.json()["title"] == title
        assert requests_mock.last_request.json()["event_type"] == event_type
        assert requests_mock.last_request.json()["start_time"] == start_time
        assert requests_mock.last_request.json()["end_time"] == end_time
        assert requests_mock.last_request.json()["scope_id"] == scope_id
        assert requests_mock.last_request.json()["scope_type"] == scope_type

    def test_create_event_maximal(self, st: SolidarityTech, requests_mock: Mocker) -> None:
        """Verify that :meth:`~parsons.solidarity_tech.SolidarityTech.create_event` makes the appropriate calls."""
        title = "new test event"
        event_type = EventType.HYBRID
        start_time = 1791809960
        end_time = 1791817188
        location_address = ""
        virtual_url = ""
        location_name = ""
        scope_id = 960
        scope_type = ScopeType.CHAPTER
        session_title = ""
        allow_long_title = True
        tags = ["tag1", "tag2"]
        max_capacity = 18
        latitude = 43.6596536
        longitude = -70.562347
        skip_duplicate_check = True
        automated_communications: AutomationStatusData = {
            "rsvp_confirmation_email": False,
            "rsvp_confirmation_text": False,
            "day_before_email_reminder": True,
            "day_before_text_reminder": False,
            "day_of_email_reminder": True,
            "day_of_text_reminder": False,
            "ten_min_before_text_reminder": True,
            "post_event_survey_email": True,
            "post_event_survey_text": True,
        }

        endpoint_url = f"{st.api_url}{ENDPOINT}"
        _ = requests_mock.post(endpoint_url, status_code=HTTPStatus.CREATED, json={"data": {}})

        _ = st.create_event(
            title=title,
            event_type=event_type,
            start_time=start_time,
            end_time=end_time,
            location_address=location_address,
            virtual_url=virtual_url,
            location_name=location_name,
            scope_id=scope_id,
            scope_type=scope_type,
            session_title=session_title,
            allow_long_title=allow_long_title,
            tags=tags,
            max_capacity=max_capacity,
            latitude=latitude,
            longitude=longitude,
            skip_duplicate_check=skip_duplicate_check,
            automated_communications=automated_communications,
        )

        assert requests_mock.call_count == 1
        assert requests_mock.last_request is not None
        assert requests_mock.last_request.method == "POST"
        assert requests_mock.last_request.url == endpoint_url
        assert requests_mock.last_request.json()["title"] == title
        assert requests_mock.last_request.json()["event_type"] == event_type
        assert requests_mock.last_request.json()["start_time"] == start_time
        assert requests_mock.last_request.json()["end_time"] == end_time
        assert requests_mock.last_request.json()["location_address"] == location_address
        assert requests_mock.last_request.json()["virtual_url"] == virtual_url
        assert requests_mock.last_request.json()["location_name"] == location_name
        assert requests_mock.last_request.json()["scope_id"] == scope_id
        assert requests_mock.last_request.json()["scope_type"] == scope_type
        assert requests_mock.last_request.json()["allow_long_title"] == allow_long_title
        assert requests_mock.last_request.json()["tags"] == tags
        assert requests_mock.last_request.json()["max_capacity"] == max_capacity
        assert requests_mock.last_request.json()["latitude"] == latitude
        assert requests_mock.last_request.json()["longitude"] == longitude
        assert requests_mock.last_request.json()["skip_duplicate_check"] == skip_duplicate_check
        assert (
            requests_mock.last_request.json()["automated_communications"]
            == automated_communications
        )
