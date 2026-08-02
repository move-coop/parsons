import logging
from datetime import datetime
from typing import Literal

import numpy as np

from parsons import Table
from parsons.solidarity_tech.solidarity_tech_base import SolidarityTechBase
from parsons.solidarity_tech.solidarity_tech_literals import EventType, ScopeType

logger = logging.getLogger(__name__)


class SolidarityTechEvents(SolidarityTechBase):
    def get_events(
        self,
        limit: int = 20,
        offset: int = 0,
        since: int | datetime = 0,
        scope_id: int | None = None,
        scope_type: ScopeType | None = None,
    ) -> Table:
        """
        Lists events accessible within the given scope.

        Each event in the response includes ``primary_event_id`` and ``is_co_hosted_mirror``.
        For co-hosted events that appear across multiple organizations,
        ``primary_event_id`` always resolves to the original event ID,
        allowing you to identify that two events from different scopes represent the same real world event.
        Each event session also includes ``primary_session_id`` for the same purpose.
        Events with an event page also include ``image_url`` and ``description`` fields, plus ``accessibility_info``; this is
        an optional per-language hash of accessibility details from the event page settings
        (e.g. {"en": "Wheelchair accessible entrance"}), null when not provided.

        Args:
            limit:
                Limits the number of items returned.
                Default is 20, maximum is 100.
            offset:
                Number of items to skip before starting to return the results.
            since:
                UTC timestamp in seconds since the Unix epoch to filter calls created after this time.
            scope_id:
                ID of the scope to filter events by.
            scope_type:
                Type of the scope to filter events by.

        Raises:
            :class:`STFailedResponseError`: If the operation fails with a known error code.
            :class:`STUnexpectedResponseError`: If the operation fails with an unexpected status code.

        Returns:
            All the events.

        Documentation Reference:
            `<https://www.solidarity.tech/reference/get_events>`__

        """
        params = {
            "scope_id": scope_id,
            "scope_type": scope_type,
        }
        res = self._get_resources(
            "events",
            limit=limit,
            offset=offset,
            since=since,
            params=params,
        )

        expected_responses = {200: (True, "events listed")}
        self._handle_status_codes(res=res, codes=expected_responses)

        return Table(res.json())

    def create_event(
        self,
        title: str,
        event_type: EventType | Literal["hybrid"],
        start_time: np.int64,
        end_time: np.int64,
        scope_id: str,
        scope_type: ScopeType,
        location_address: str | None = None,
        virtual_url: str | None = None,
        location_name: str | None = None,
        session_title: str | None = None,
        tags: list[str] | None = None,
        max_capacity: int | None = None,
        latitude: float | None = None,
        longitude: float | None = None,
        skip_duplicate_check: bool = False,
    ) -> bool:
        """
        Create an event with its first event session.

        The event session inherits the title from the event unless ``session_title`` is provided.

        Args:
            title:
                Event title (max 65 characters).
            event_type:
                Type of event.
            start_time:
                Start time as UNIX timestamp.
            end_time:
                End time as UNIX timestamp.
            location_address:
                For virtual: meeting URL.
                For in_person and hybrid: street address for the in-person session.
            virtual_url:
                Meeting URL for the virtual session when event_type is hybrid.
            location_name:
                Display name for location (e.g., "City Hall").
            scope_id:
                ID of the scope (Organization or Chapter).
            scope_type:
                Type of scope.
            session_title:
                Title for the first event session (defaults to event title).
            tags:
                Event tags.
            max_capacity:
                Maximum capacity for the event session (0 = unlimited).
            latitude:
                Latitude for ``in_person`` events (optional, will geocode if not provided).
            longitude:
                Longitude for ``in_person`` events (optional, will geocode if not provided).
            skip_duplicate_check:
                If True, bypasses duplicate event detection. Default is False.

        Raises:
            :class:`STFailedResponseError`: If the operation fails with a known error code.
            :class:`STUnexpectedResponseError`: If the operation fails with an unexpected status code.

        Returns:
            Boolean representing success of the operation.
            True if the operation was successful, False otherwise.

        Documentation Reference:
            `<https://www.solidarity.tech/reference/post_events>`__

        """
        payload = {
            "title": title,
            "event_type": event_type,
            "start_time": start_time,
            "end_time": end_time,
            "location_address": location_address,
            "virtual_url": virtual_url,
            "location_name": location_name,
            "scope_id": scope_id,
            "scope_type": scope_type,
            "session_title": session_title,
            "tags": tags,
            "max_capacity": max_capacity,
            "latitude": latitude,
            "longitude": longitude,
            "skip_duplicate_check": skip_duplicate_check,
        }
        res = self._post_request(
            "events", payload=payload, additional_headers={"content-type": "application/json"}
        )
        expected_responses = {
            201: (True, "event created"),
            404: (False, "scope not found"),
            409: (False, "duplicate event detected"),
            422: (False, "validation error"),
        }
        return self._handle_status_codes(res=res, codes=expected_responses)

    def get_event(
        self,
        id: int,
        include_hosts: bool = False,
    ) -> dict:
        """
        Returns a single event.

        The response includes ``primary_event_id``
        (always resolves to the original event ID, even for co-hosted mirrors) and
        ``is_co_hosted_mirror`` (true if this event is a mirror copy from a co-host relationship).
        Event sessions include ``primary_session_id`` for the same purpose.
        If the event has an event page, the response also includes ``image_url`` (the event page image),
        ``description`` (plain text content from the event page), and ``accessibility_info``
        (an optional per-language hash of accessibility details from the event page settings,
        e.g. {"en": "Wheelchair accessible entrance"}).
        These fields are null when no event page exists or the value is not set.

        Args:
            id:
                ID of the event to retrieve.

        Raises:
            :class:`STFailedResponseError`: If the operation fails with a known error code.
            :class:`STUnexpectedResponseError`: If the operation fails with an unexpected status code.

        Returns:
            A single event.

        Documentation Reference:
            `<https://www.solidarity.tech/reference/get_events-id>`__

        """
        params = {"include_hosts": include_hosts}
        res = self._get_single_resource("event_sessions", id, params=params)

        expected_responses = {
            200: (True, "event found"),
            404: (False, "event not found"),
        }
        self._handle_status_codes(res=res, codes=expected_responses)

        return res.json()
