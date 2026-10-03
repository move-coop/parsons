"""Connector class for interacting with the SolidarityTech Events endpoint."""

from __future__ import annotations

import logging
from http import HTTPStatus
from typing import TYPE_CHECKING

from parsons import Table
from parsons.solidarity_tech.base import SolidarityTechBase

if TYPE_CHECKING:
    from datetime import datetime

    from parsons.solidarity_tech.datatypes import (
        AutomationStatusData,
        EventData,
        EventType,
        Metadata,
        ScopeType,
    )
    from parsons.utilities.api_connector import _JsonType

logger = logging.getLogger(__name__)


class SolidarityTechEvents(SolidarityTechBase):
    """Methods for interacting with the SolidarityTech events endpoint."""

    def get_events(
        self,
        limit: int = 20,
        offset: int = 0,
        since: int | datetime = 0,
        scope_id: int | None = None,
        scope_type: ScopeType | None = None,
    ) -> tuple[Table, Metadata]:
        """
        Retrieve events accessible within the given scope.

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
            A list of event entries, along with requested metadata.

        Documentation Reference:
            `<https://www.solidarity.tech/reference/get_events>`__

        """
        params: dict[str, _JsonType] = {}
        _ = scope_id is not None and params.update({"scope_id": scope_id})
        _ = scope_type is not None and params.update({"scope_type": scope_type})

        res = self._get_resources(
            "events",
            limit=limit,
            offset=offset,
            since=since,
            params=params,
        )

        expected_responses = {HTTPStatus.OK: (True, "events listed")}
        self._handle_status_codes(res=res, codes=expected_responses)

        data: list[EventData] = res.json()["data"]
        meta: Metadata = res.json()["meta"]

        return Table(data, name="Solidarity Tech Events"), meta

    def create_event(
        self,
        title: str,
        event_type: EventType,
        start_time: int,
        end_time: int,
        scope_id: int,
        scope_type: ScopeType,
        location_address: str | None = None,
        virtual_url: str | None = None,
        location_name: str | None = None,
        session_title: str | None = None,
        tags: list[str] | None = None,
        max_capacity: int | None = None,
        latitude: float | None = None,
        longitude: float | None = None,
        automated_communications: AutomationStatusData | None = None,
        *,
        skip_duplicate_check: bool = False,
        allow_long_title: bool = False,
    ) -> EventData:
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
            allow_long_title:
                If True, raises the session title cap from 65 to 200 characters. Default is False.
            automated_communications:
                On/off switches for the event's automated communications. Omitted settings keep their defaults.

        Raises:
            :class:`STFailedResponseError`: If the operation fails with a known error code.
            :class:`STUnexpectedResponseError`: If the operation fails with an unexpected status code.

        Returns:
            A single event entry, as it exists after creating the event.

        Documentation Reference:
            `<https://www.solidarity.tech/reference/post_events>`__

        """
        payload: dict[str, _JsonType] = {
            "title": title,
            "event_type": event_type,
            "start_time": start_time,
            "end_time": end_time,
            "scope_id": scope_id,
            "scope_type": scope_type,
        }
        _ = location_address is not None and payload.update({"location_address": location_address})
        _ = virtual_url is not None and payload.update({"virtual_url": virtual_url})
        _ = location_name is not None and payload.update({"location_name": location_name})
        _ = session_title is not None and payload.update({"session_title": session_title})
        _ = tags is not None and payload.update({"tags": tags})
        _ = max_capacity is not None and payload.update({"max_capacity": max_capacity})
        _ = latitude is not None and payload.update({"latitude": latitude})
        _ = longitude is not None and payload.update({"longitude": longitude})
        _ = skip_duplicate_check is not None and payload.update(
            {"skip_duplicate_check": skip_duplicate_check}
        )
        _ = allow_long_title is not None and payload.update({"allow_long_title": allow_long_title})
        _ = automated_communications is not None and payload.update(
            {"automated_communications": automated_communications}
        )

        res = self._post_request(
            "events", payload=payload, additional_headers={"content-type": "application/json"}
        )

        expected_responses = {
            HTTPStatus.CREATED: (True, "event created"),
            HTTPStatus.NOT_FOUND: (False, "scope not found"),
            HTTPStatus.CONFLICT: (False, "duplicate event detected"),
            HTTPStatus.UNPROCESSABLE_ENTITY: (False, "validation error"),
        }
        self._handle_status_codes(res=res, codes=expected_responses)

        data: EventData = res.json()["data"]

        return data

    def get_event(
        self,
        resource_id: int,
        *,
        include_hosts: bool = False,
    ) -> tuple[EventData, Metadata]:
        """
        Retrieve a single event.

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
            resource_id:
                ID of the event to retrieve.

        Raises:
            :class:`STFailedResponseError`: If the operation fails with a known error code.
            :class:`STUnexpectedResponseError`: If the operation fails with an unexpected status code.

        Returns:
            A single event entry, along with requested metadata.

        Documentation Reference:
            `<https://www.solidarity.tech/reference/get_events-id>`__

        """
        params: dict[str, _JsonType] = {"include_hosts": include_hosts}

        res = self._get_single_resource("events", resource_id, params=params)

        expected_responses = {
            HTTPStatus.OK: (True, "event found"),
            HTTPStatus.NOT_FOUND: (False, "event not found"),
        }
        self._handle_status_codes(res=res, codes=expected_responses)

        data: EventData = res.json()["data"]
        meta: Metadata = res.json()["meta"]

        return data, meta
