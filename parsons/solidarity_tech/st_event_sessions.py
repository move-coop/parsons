from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, Literal

from parsons import Table
from parsons.solidarity_tech.base import SolidarityTechBase

if TYPE_CHECKING:
    from datetime import datetime

    import numpy as np

    from parsons.solidarity_tech.base import ParamsType
    from parsons.solidarity_tech.enums import EventType

logger = logging.getLogger(__name__)


class SolidarityTechEventSessions(SolidarityTechBase):
    """Methods for interacting with the SolidarityTech event sessions endpoint."""

    def get_event_sessions(
        self,
        limit: int = 20,
        offset: int = 0,
        since: int | datetime = 0,
        event_id: int = 0,
        starts_after: int | datetime | None = None,
        starts_before: int | datetime | None = None,
        chapter_id: int | None = None,
        event_tags: list[str] | str | None = None,
        *,
        upcoming: bool | None = None,
        include_rsvp_counts: bool | None = None,
        include_confirmed_counts: bool | None = None,
        include_hosts: bool | None = None,
        count: bool | None = None,
    ) -> Table:
        """
        Retrieve a list of event rsvps.

        Args:
            limit:
                Limits the number of items returned.
                Default is 20, maximum is 100.
            offset:
                Number of items to skip before starting to return the results.
            since:
                UTC timestamp in seconds since the Unix epoch to filter calls created after this time.
            event_id:
                Filters sessions by event_id within the accessible scope.
            starts_after:
                UTC timestamp in seconds since the Unix epoch;
                only sessions with start_time at or after this moment.
            starts_before:
                UTC timestamp in seconds since the Unix epoch;
                only sessions with start_time at or before this moment.
            chapter_id:
                Only sessions of events scoped to this chapter.
                Chapters outside your accessible scope simply match nothing.
            event_tags:
                Comma-separated list of tags.
                Matches sessions whose own tags OR whose parent event tags overlap with the list.
            upcoming:
                If True, returns only sessions that have not ended yet,
                sorted by start_time ascending (soonest first).
            include_rsvp_counts:
                If True, each session in the response includes an rsvp_counts object keyed by RSVP status.
                (e.g. {"yes": 12, "no": 3})
            include_confirmed_counts:
                If True, each session includes a confirmed_counts object
                (the same per-status breakdown as rsvp_counts, restricted to RSVPs an organizer confirmed).
            include_hosts:
                If True, each session includes a hosts array of
                {id, first_name, last_name} objects resolved from host_user_ids, in host order.
            count:
                If True, returns {"count": n} of matching sessions instead of the rows.
                Combines with all other filters.

        Raises:
            :class:`STFailedResponseError`: If the operation fails with a known error code.
            :class:`STUnexpectedResponseError`: If the operation fails with an unexpected status code.

        Returns:
            All the event sessions.

        Documentation Reference:
            `<https://www.solidarity.tech/reference/get_event-sessions>`__

        """
        if isinstance(event_tags, list):
            event_tags = ",".join(str(tag) for tag in event_tags)

        params: ParamsType = {
            "event_id": event_id,
        }
        self._add_if_field_not_empty(params, "upcoming", upcoming)
        self._add_if_field_not_empty(params, "starts_after", starts_after)
        self._add_if_field_not_empty(params, "starts_before", starts_before)
        self._add_if_field_not_empty(params, "chapter_id", chapter_id)
        self._add_if_field_not_empty(params, "event_tags", event_tags)
        self._add_if_field_not_empty(params, "include_rsvp_counts", include_rsvp_counts)
        self._add_if_field_not_empty(params, "include_confirmed_counts", include_confirmed_counts)
        self._add_if_field_not_empty(params, "include_hosts", include_hosts)
        self._add_if_field_not_empty(params, "count", count)

        res = self._get_resources(
            "event_sessions",
            limit=limit,
            offset=offset,
            since=since,
            params=params,
        )

        expected_responses = {200: (True, "filtered event sessions listed")}
        self._handle_status_codes(res=res, codes=expected_responses)

        return Table(res.json())

    def create_event_sessions(
        self,
        event_id: np.int64,
        start_time: np.int64,
        end_time: np.int64,
        title: str,
        event_type: Literal[EventType.VIRTUAL, EventType.IN_PERSON] | None = None,
        location_name: str | None = None,
        location_data: dict[str, str] | None = None,
        location_address: str | None = None,
        note: str | None = None,
        max_capacity: int | None = None,
        tags: list[str] | None = None,
        *,
        show_rsvp_bar: bool | None = None,
        show_title_in_form: bool | None = None,
    ) -> bool:
        """
        Create an event rsvp with the specified details.

        Args:
            event_id:
                Identifier for the Mobilize event.
            start_time:
                UTC timestamp in seconds since the Unix epoch.
            end_time:
                UTC timestamp in seconds since the Unix epoch.
            title:
                Title of the event session.
            event_type:
                Type of session.
            location_name:
                Name of the location.
            location_data:
                Structured location details.
                Components and coordinates may be sent either as native JSON (array/object)
                or as JSON-encoded strings; both are stored and returned as JSON strings.
                Neighborhood is the components entry whose types include "neighborhood";
                NYC borough is the entry whose types include "sublocality_level_1".
            location_address:
                Physical address of the event location.
            note:
                Additional notes for the event session.
            max_capacity:
                Maximum capacity for the event session.
            tags:
                Array of tags for the event session.
            show_rsvp_bar:
                Flag to show RSVP buttons bar.
            show_title_in_form:
                Flag to show title in the form.

        Raises:
            :class:`STFailedResponseError`: If the operation fails with a known error code.
            :class:`STUnexpectedResponseError`: If the operation fails with an unexpected status code.

        Returns:
            Boolean representing success of the operation.
            True if the operation was successful, False otherwise.

        Documentation Reference:
            `<https://www.solidarity.tech/reference/post_event-sessions>`__

        """
        payload: dict[str, Any] = {
            "event_id": event_id,
            "start_time": start_time,
            "end_time": end_time,
            "title": title,
        }
        self._add_if_field_not_empty(payload, "event_type", event_type)
        self._add_if_field_not_empty(payload, "location_name", location_name)
        self._add_if_field_not_empty(payload, "location_data", location_data)
        self._add_if_field_not_empty(payload, "location_address", location_address)
        self._add_if_field_not_empty(payload, "show_rsvp_bar", show_rsvp_bar)
        self._add_if_field_not_empty(payload, "show_title_in_form", show_title_in_form)
        self._add_if_field_not_empty(payload, "note", note)
        self._add_if_field_not_empty(payload, "max_capacity", max_capacity)
        self._add_if_field_not_empty(payload, "tags", tags)

        res = self._post_request(
            "event_rsvps", payload=payload, additional_headers={"content-type": "application/json"}
        )

        expected_responses = {
            201: (True, "event session created"),
            422: (False, "unprocessable entity"),
        }
        return self._handle_status_codes(res=res, codes=expected_responses)

    def get_event_session(
        self,
        resource_id: int,
        *,
        include_hosts: bool = False,
    ) -> dict:
        """
        Retrieve a single event session.

        Args:
            resource_id:
                ID of the event session to retrieve.
            include_hosts:
                If True, the session includes a hosts array of
                {id, first_name, last_name} objects resolved from host_user_ids,
                in host order.

        Raises:
            :class:`STFailedResponseError`: If the operation fails with a known error code.
            :class:`STUnexpectedResponseError`: If the operation fails with an unexpected status code.

        Returns:
            A single event session.

        Documentation Reference:
            `<https://www.solidarity.tech/reference/get_event-sessions-id>`__

        """
        params: ParamsType = {"include_hosts": include_hosts}
        res = self._get_single_resource("event_sessions", resource_id, params=params)

        expected_responses = {
            200: (True, "event session found"),
            404: (False, "event session not found"),
        }
        self._handle_status_codes(res=res, codes=expected_responses)

        return res.json()

    def update_event_session(
        self,
        resource_id: int,
        start_time: np.int64 | None = None,
        end_time: np.int64 | None = None,
        title: str | None = None,
        location_name: str | None = None,
        location_address: str | None = None,
        location_data: dict[str, str] | None = None,
        note: str | None = None,
        max_capacity: int | None = None,
        tags: list[str] | None = None,
        *,
        show_rsvp_bar: bool | None = None,
        show_title_in_form: bool | None = None,
    ) -> bool:
        """
        Update an event session with the specified details.

        Args:
            resource_id:
                Identifier of the event session to update.
            start_time:
                UTC timestamp in seconds since the Unix epoch.
            end_time:
                UTC timestamp in seconds since the Unix epoch.
            title:
                Title of the event session.
            location_name:
                Name of the location.
            location_address:
                Physical address of the event location.
            location_data:
                See :meth:`create_event_session`.
                ``components``/``coordinates`` accept native JSON or JSON strings
                and are stored/returned as JSON strings.
                Omit to leave the existing location_data unchanged.
            note:
                Additional notes for the event session.
            max_capacity:
                Maximum capacity of the event session.
            tags:
                List of tags for the event session.
            show_rsvp_bar:
                Flag to show RSVP buttons bar.
            show_title_in_form:
                Flag to show title in the form.

        Raises:
            :class:`STFailedResponseError`: If the operation fails with a known error code.
            :class:`STUnexpectedResponseError`: If the operation fails with an unexpected status code.

        Returns:
            Boolean representing success of the operation.
            True if the operation was successful, False otherwise.

        Documentation Reference:
            `<https://www.solidarity.tech/reference/put_event-sessions-id>`__

        """
        payload: dict[str, Any] = {}
        self._add_if_field_not_empty(payload, "start_time", start_time)
        self._add_if_field_not_empty(payload, "end_time", end_time)
        self._add_if_field_not_empty(payload, "title", title)
        self._add_if_field_not_empty(payload, "location_name", location_name)
        self._add_if_field_not_empty(payload, "location_address", location_address)
        self._add_if_field_not_empty(payload, "location_data", location_data)
        self._add_if_field_not_empty(payload, "show_rsvp_bar", show_rsvp_bar)
        self._add_if_field_not_empty(payload, "show_title_in_form", show_title_in_form)
        self._add_if_field_not_empty(payload, "note", note)
        self._add_if_field_not_empty(payload, "max_capacity", max_capacity)
        self._add_if_field_not_empty(payload, "tags", tags)

        res = self._put_request(
            "event_sessions",
            resource_id,
            payload=payload,
            additional_headers={"content-type": "application/json"},
        )

        expected_responses = {
            200: (True, "event session updated"),
            404: (False, "event session not found"),
            422: (False, "unprocessable entity"),
        }
        return self._handle_status_codes(res=res, codes=expected_responses)

    def delete_event_session(
        self,
        resource_id: str,
    ) -> bool:
        """
        Delete an event session with the specified ID.

        Args:
            resource_id:
                Identifier of the event session to delete

        Raises:
            :class:`STFailedResponseError`: If the operation fails with a known error code.
            :class:`STUnexpectedResponseError`: If the operation fails with an unexpected status code.

        Returns:
            Boolean representing success of the operation.
            True if the operation was successful, False otherwise.

        Documentation Reference:
            `<https://www.solidarity.tech/reference/delete_event-sessions-id>`__

        """
        res = self._del_request(
            "event_sessions",
            resource_id,
        )

        expected_responses = {
            404: (False, "event session not found"),
        }
        return self._handle_status_codes(res=res, codes=expected_responses)

    def add_event_host(
        self,
        resource_id: int,
        user_id: np.int64,
    ) -> bool:
        """
        Add a user as a host of the event session.

        .. admonition:: Atomic and Idempotent

            Adding a user who is already a host returns 200 without duplicating.
            The user must belong to your organization.
            Hosts are readable on the session as host_user_ids and usable in
            message templates via the {{ event-session.hosts }},
            {{ event-session.host }}, and {{ event-session.host-names }} merge tags.

        Args:
            resource_id:
                Identifier of the event session.
            user_id:
                ID of the user to add as a host.

        Raises:
            :class:`STFailedResponseError`: If the operation fails with a known error code.
            :class:`STUnexpectedResponseError`: If the operation fails with an unexpected status code.

        Returns:
            Boolean representing success of the operation.
            True if the operation was successful, False otherwise.

        Documentation Reference:
            `<https://www.solidarity.tech/reference/post_event-sessions-id-hosts>`__

        """
        payload: dict[str, Any] = {"user_id": user_id}

        res = self._post_request(
            f"event_sessions/{resource_id}/hosts",
            payload=payload,
            additional_headers={"content-type": "application/json"},
        )

        expected_responses = {
            200: (True, "host added"),
            404: (False, "user or event session not found"),
        }
        return self._handle_status_codes(res=res, codes=expected_responses)

    def remove_event_host(
        self,
        resource_id: str,
        user_id: int,
    ) -> bool:
        """
        Remove a user from the event session hosts.

        .. admonition:: Atomic and Idempotent

            Removing a user who is not a host returns 200.


        Args:
            resource_id:
                Identifier of the event session.
            user_id:
                ID of the user to remove from hosts.

        Raises:
            :class:`STFailedResponseError`: If the operation fails with a known error code.
            :class:`STUnexpectedResponseError`: If the operation fails with an unexpected status code.

        Returns:
            Boolean representing success of the operation.
            True if the operation was successful, False otherwise.

        Documentation Reference:
            `<https://www.solidarity.tech/reference/delete_event-sessions-id-hosts-user-id>`__

        """
        res = self._del_request(
            "event_sessions",
            f"{resource_id}/hosts/{user_id}",
        )

        expected_responses = {
            200: (True, "host removed"),
        }
        return self._handle_status_codes(res=res, codes=expected_responses)
