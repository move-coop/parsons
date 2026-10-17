"""Connector class for interacting with the SolidarityTech Event RSVPs endpoint."""

from __future__ import annotations

import logging
from http import HTTPStatus
from typing import TYPE_CHECKING

from parsons import Table
from parsons.solidarity_tech.base import SolidarityTechBase

if TYPE_CHECKING:
    from datetime import datetime

    from parsons.solidarity_tech.datatypes import AttendanceStatus, EventRSVPData, Metadata
    from parsons.utilities.api_connector import _JsonType

logger = logging.getLogger(__name__)


class SolidarityTechEventRSVPs(SolidarityTechBase):
    """Methods for interacting with the SolidarityTech event rsvps endpoint."""

    def get_event_rsvps(
        self,
        limit: int = 20,
        offset: int = 0,
        since: int | datetime = 0,
        event_id: int | None = None,
        session_id: int | None = None,
        user_id: int | None = None,
        *,
        full_user_payload: bool = False,
    ) -> tuple[Table, Metadata]:
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
                Filters rsvps by event_id within the accessible scope.
            session_id:
                Filters rsvps by session_id (calendar item id) within the accessible scope.
            user_id:
                Filters rsvps by user_id within the accessible scope.
            full_user_payload:
                If True, includes complete user data in the response instead of just basic details.

        Raises:
            :class:`STFailedResponseError`: If the operation fails with a known error code.
            :class:`STUnexpectedResponseError`: If the operation fails with an unexpected status code.

        Returns:
            A list of event rsvp entries, along with requested metadata.

        Documentation Reference:
            `<https://www.solidarity.tech/reference/get_event-rsvps>`__

        """
        params: dict[str, _JsonType] = {"full_user_payload": full_user_payload}
        _ = event_id is not None and params.update({"event_id": event_id})
        _ = session_id is not None and params.update({"session_id": session_id})
        _ = user_id is not None and params.update({"user_id": user_id})

        res = self._get_resources(
            "event_rsvps",
            limit=limit,
            offset=offset,
            since=since,
            params=params,
        )

        expected_responses = {HTTPStatus.OK: (True, "event rsvps listed")}
        self._handle_status_codes(res=res, codes=expected_responses)

        data: list[EventRSVPData] = res.json()["data"]
        meta: Metadata = res.json()["meta"]

        return Table(data, name="Solidarity Tech Event RSVPs"), meta

    def get_event_rsvp(
        self,
        resource_id: int,
        *,
        full_user_payload: bool = False,
    ) -> tuple[EventRSVPData, Metadata]:
        """
        Retrieve a single event rsvp.

        Args:
            resource_id:
                ID of the event rsvp to retrieve.
            full_user_payload:
                If True, includes complete user data in the response instead of just basic details.

        Raises:
            :class:`STFailedResponseError`: If the operation fails with a known error code.
            :class:`STUnexpectedResponseError`: If the operation fails with an unexpected status code.

        Returns:
            A single event rsvp entry, along with requested metadata.

        Documentation Reference:
            `<https://www.solidarity.tech/reference/get_event-rsvps-id>`__

        """
        params: dict[str, _JsonType] = {"full_user_payload": full_user_payload}

        res = self._get_single_resource("event_rsvps", resource_id, params=params)

        expected_responses = {
            HTTPStatus.OK: (True, "event rsvp found"),
            HTTPStatus.NOT_FOUND: (False, "event rsvp not found"),
        }
        self._handle_status_codes(res=res, codes=expected_responses)

        data: EventRSVPData = res.json()["data"]
        meta: Metadata = res.json()["meta"]

        return data, meta

    def create_event_rsvp(
        self,
        event_id: int,
        event_session_id: int,
        is_attending: AttendanceStatus,
        agent_user_id: int | None,
        user_id: int | None = None,
        source: str | None = None,
        source_system: str | None = None,
        *,
        is_confirmed: bool | None = None,
        skip_email_confirmation: bool = False,
    ) -> EventRSVPData:
        """
        Create an event rsvp with the specified details.

        Args:
            event_id:
                Identifier for the Mobilize event.
            event_session_id:
                Identifier for the specific event session.
            is_attending:
                Indicates if the user is attending the event.
            agent_user_id:
                Identifier for the agent user, if applicable.
            user_id:
                Identifier for the user RSVPing to the event.
            source:
                Source of the RSVP.
            source_system:
                System from which the RSVP originated.
            is_confirmed:
                Indicates if the RSVP is confirmed.
            skip_email_confirmation:
                If True, skips sending the initial email confirmation to the user.

        Raises:
            :class:`STFailedResponseError`: If the operation fails with a known error code.
            :class:`STUnexpectedResponseError`: If the operation fails with an unexpected status code.

        Returns:
            A single event rsvp entry, as it exists after creating.

        Documentation Reference:
            `<https://www.solidarity.tech/reference/post_event-rsvps>`__

        """
        payload: dict[str, _JsonType] = {
            "is_attending": is_attending,
            "agent_user_id": agent_user_id,
            "event_id": event_id,
            "event_session_id": event_session_id,
            "skip_email_confirmation": skip_email_confirmation,
        }
        _ = user_id is not None and payload.update({"user_id": user_id})
        _ = is_confirmed is not None and payload.update({"is_confirmed": is_confirmed})
        _ = source is not None and payload.update({"source": source})
        _ = source_system is not None and payload.update({"source_system": source_system})

        res = self._post_request(
            "event_rsvps", payload=payload, additional_headers={"content-type": "application/json"}
        )

        expected_responses = {
            HTTPStatus.CREATED: (True, "event rsvp created"),
            HTTPStatus.NOT_FOUND: (False, "event not found"),
        }
        self._handle_status_codes(res=res, codes=expected_responses)

        data: EventRSVPData = res.json()["data"]

        return data

    def update_event_rsvp(
        self,
        resource_id: int,
        is_attending: AttendanceStatus | None = None,
        agent_user_id: int | None = None,
        source: str | None = None,
        source_system: str | None = None,
        *,
        is_confirmed: bool | None = None,
    ) -> EventRSVPData:
        """
        Update an event rsvp with the specified details.

        Args:
            resource_id:
                Identifier of the event rsvp to update.
            is_attending:
                Indicates if the user is attending the event.
            agent_user_id:
                Identifier for the agent user, if applicable.
            source:
                Source of the RSVP.
            source_system:
                System from which the RSVP originated.
            is_confirmed:
                Indicates if the RSVP is confirmed.

        Raises:
            :class:`STFailedResponseError`: If the operation fails with a known error code.
            :class:`STUnexpectedResponseError`: If the operation fails with an unexpected status code.

        Returns:
            A single event rsvp entry, as it exists after updating.

        Documentation Reference:
            `<https://www.solidarity.tech/reference/put_event-rsvps-id>`__

        """
        payload: dict[str, _JsonType] = {}
        _ = is_attending is not None and payload.update({"is_attending": is_attending})
        _ = is_confirmed is not None and payload.update({"is_confirmed": is_confirmed})
        _ = agent_user_id is not None and payload.update({"agent_user_id": agent_user_id})
        _ = source is not None and payload.update({"source": source})
        _ = source_system is not None and payload.update({"source_system": source_system})

        res = self._put_request(
            "event_rsvps",
            resource_id,
            payload=payload,
            additional_headers={"content-type": "application/json"},
        )

        expected_responses = {
            HTTPStatus.OK: (True, "event rsvp updated"),
            HTTPStatus.NOT_FOUND: (False, "event rsvp not found"),
        }
        self._handle_status_codes(res=res, codes=expected_responses)

        data: EventRSVPData = res.json()["data"]

        return data

    def delete_event_rsvp(
        self,
        resource_id: int,
    ) -> bool:
        """
        Delete an event rsvp with the specified ID.

        Args:
            resource_id:
                Identifier of the event rsvp to delete

        Raises:
            :class:`STFailedResponseError`: If the operation fails with a known error code.
            :class:`STUnexpectedResponseError`: If the operation fails with an unexpected status code.

        Returns:
            Boolean representing success of the operation.
            True if the operation was successful, False otherwise.

        Documentation Reference:
            `<https://www.solidarity.tech/reference/delete_event-rsvps-id>`__

        """
        res = self._delete_request(
            "event_rsvps",
            resource_id,
        )

        expected_responses = {
            HTTPStatus.OK: (True, "event rsvp successfully deleted"),
            HTTPStatus.NOT_FOUND: (False, "event rsvp not found"),
        }
        return self._handle_status_codes(res=res, codes=expected_responses)
