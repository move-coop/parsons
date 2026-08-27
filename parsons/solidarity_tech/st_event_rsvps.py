from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from parsons import Table
from parsons.solidarity_tech.base import SolidarityTechBase

if TYPE_CHECKING:
    from datetime import datetime

    import numpy as np

    from parsons.solidarity_tech.base import ParamsType
    from parsons.solidarity_tech.enums import AttendanceStatus

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
            All the event rsvps.

        Documentation Reference:
            `<https://www.solidarity.tech/reference/get_event-rsvps>`__

        """
        params: ParamsType = {"full_user_payload": full_user_payload}
        self._add_if_field_not_empty(params, "event_id", event_id)
        self._add_if_field_not_empty(params, "session_id", session_id)
        self._add_if_field_not_empty(params, "user_id", user_id)

        res = self._get_resources(
            "event_rsvps",
            limit=limit,
            offset=offset,
            since=since,
            params=params,
        )

        expected_responses = {200: (True, "event rsvps listed")}
        self._handle_status_codes(res=res, codes=expected_responses)

        return Table(res.json())

    def get_event_rsvp(
        self,
        resource_id: int,
        *,
        full_user_payload: bool = False,
    ) -> dict:
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
            A single event rsvp.

        Documentation Reference:
            `<https://www.solidarity.tech/reference/get_event-rsvps-id>`__

        """
        params: ParamsType = {"full_user_payload": full_user_payload}

        res = self._get_single_resource("event_rsvps", resource_id, params=params)

        expected_responses = {
            200: (True, "event rsvp found"),
            404: (False, "event rsvp not found"),
        }
        self._handle_status_codes(res=res, codes=expected_responses)

        return res.json()

    def create_event_rsvp(
        self,
        event_id: np.int64,
        event_session_id: np.int64,
        is_attending: AttendanceStatus,
        agent_user_id: np.int64 | None,
        user_id: np.int64 | None = None,
        source: str | None = None,
        source_system: str | None = None,
        *,
        is_confirmed: bool | None = None,
        skip_email_confirmation: bool = False,
    ) -> bool:
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
            Boolean representing success of the operation.
            True if the operation was successful, False otherwise.

        Documentation Reference:
            `<https://www.solidarity.tech/reference/post_event-rsvps>`__

        """
        payload: dict[str, Any] = {
            "is_attending": is_attending.value,
            "agent_user_id": agent_user_id,
            "event_id": event_id,
            "event_session_id": event_session_id,
            "skip_email_confirmation": skip_email_confirmation,
        }
        self._add_if_field_not_empty(payload, "user_id", user_id)
        self._add_if_field_not_empty(payload, "is_confirmed", is_confirmed)
        self._add_if_field_not_empty(payload, "source", source)
        self._add_if_field_not_empty(payload, "source_system", source_system)

        res = self._post_request(
            "event_rsvps", payload=payload, additional_headers={"content-type": "application/json"}
        )

        expected_responses = {
            201: (True, "event rsvp created"),
            404: (False, "event not found"),
        }
        return self._handle_status_codes(res=res, codes=expected_responses)

    def update_event_rsvp(
        self,
        resource_id: int,
        is_attending: AttendanceStatus | None = None,
        agent_user_id: np.int64 | None = None,
        source: str | None = None,
        source_system: str | None = None,
        *,
        is_confirmed: bool | None = None,
    ) -> bool:
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
            Boolean representing success of the operation.
            True if the operation was successful, False otherwise.

        Documentation Reference:
            `<https://www.solidarity.tech/reference/put_event-rsvps-id>`__

        """
        payload: dict[str, Any] = {}
        self._add_if_field_not_empty(payload, "is_attending", is_attending)
        self._add_if_field_not_empty(payload, "is_confirmed", is_confirmed)
        self._add_if_field_not_empty(payload, "agent_user_id", agent_user_id)
        self._add_if_field_not_empty(payload, "source", source)
        self._add_if_field_not_empty(payload, "source_system", source_system)

        res = self._put_request(
            "event_rsvps",
            resource_id,
            payload=payload,
            additional_headers={"content-type": "application/json"},
        )

        expected_responses = {
            200: (True, "event rsvp updated"),
            404: (False, "event rsvp not found"),
        }
        return self._handle_status_codes(res=res, codes=expected_responses)

    def delete_event_rsvp(
        self,
        resource_id: str,
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
        res = self._del_request(
            "event_rsvps",
            resource_id,
        )

        expected_responses = {404: (False, "event rsvp not found")}
        return self._handle_status_codes(res=res, codes=expected_responses)
