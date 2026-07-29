import logging
from datetime import datetime
from typing import Literal

import numpy as np

from parsons.solidarity_tech.exceptions import STUnexpectedResponseCodeError
from parsons.solidarity_tech.solidarity_tech_base import SolidarityTechBase

logger = logging.getLogger(__name__)


class SolidarityTechEventRSVPs(SolidarityTechBase):
    def get_event_rsvps(
        self,
        limit: int = 20,
        offset: int = 0,
        since: int | datetime | None = 0,
        event_id: int | None = None,
        session_id: int | None = None,
        user_id: int | None = None,
        full_user_payload: bool = False,
    ) -> str:
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

        Returns:
            All the event rsvps.

        Documentation Reference:
            `<https://www.solidarity.tech/reference/get_event-rsvps>`__

        """
        params = {
            "event_id": event_id,
            "session_id": session_id,
            "user_id": user_id,
            "full_user_payload": full_user_payload,
        }
        res = self._get_resources(
            "event_rsvps",
            limit=limit,
            offset=offset,
            since=since,
            params=params,
        )

        if res.status_code != 200:
            raise STUnexpectedResponseCodeError(res)

        return res.text

    def get_event_rsvp(
        self,
        id: int,
        full_user_payload: bool = False,
    ) -> str:
        """
        Retrieve a single event rsvp.

        Args:
            id:
                ID of the event rsvp to retrieve.
            full_user_payload:
                If True, includes complete user data in the response instead of just basic details.

        Returns:
            A single event rsvp.

        Raises:
            STUnexpectedResponseCodeError: If the operation fails with an unexpected status code.

        Documentation Reference:
            `<https://www.solidarity.tech/reference/get_event-rsvps-id>`__

        """
        params = {"full_user_payload": full_user_payload}
        res = self._get_single_resource("event_rsvps", id, params=params)

        if res.status_code not in (200, 404):
            raise STUnexpectedResponseCodeError(res)

        return res.text

    def create_event_rsvp(
        self,
        event_id: np.int64,
        event_session_id: np.int64,
        is_attending: Literal["yes", "no", "maybe", "waitlisted"],
        agent_user_id: np.int64 | None,
        user_id: np.int64 | None = None,
        is_confirmed: bool | None = None,
        source: str | None = None,
        source_system: str | None = None,
        skip_email_confirmation: bool = False,
    ) -> bool:
        """
        Creates an event rsvp with the specified details.

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
            is_confirmed:
                Indicates if the RSVP is confirmed.
            source:
                Source of the RSVP.
            source_system:
                System from which the RSVP originated.
            skip_email_confirmation:
                If True, skips sending the initial email confirmation to the user.

        Returns:
            Boolean representing success of the operation.
            True if the operation was successful, False otherwise.

        Raises:
            STUnexpectedResponseCodeError: If the operation fails with an unexpected status code.

        Documentation Reference:
            `<https://www.solidarity.tech/reference/post_event-rsvps>`__

        """
        payload = {
            "is_attending": is_attending,
            "agent_user_id": agent_user_id,
            "event_id": event_id,
            "event_session_id": event_session_id,
            "user_id": user_id,
            "is_confirmed": is_confirmed,
            "source": source,
            "source_system": source_system,
            "skip_email_confirmation": skip_email_confirmation,
        }
        res = self._post_request(
            "event_rsvps", payload, additional_headers={"content-type": "application/json"}
        )

        if res.status_code not in (201, 404):
            raise STUnexpectedResponseCodeError(res)

        return res.status_code == 201

    def update_event_rsvp(
        self,
        id: int,
        is_attending: Literal["yes", "no", "maybe", "waitlisted"] | None = None,
        is_confirmed: bool | None = None,
        agent_user_id: np.int64 | None = None,
        source: str | None = None,
        source_system: str | None = None,
    ) -> bool:
        """
        Updates an event rsvp with the specified details.

        Args:
            id:
                Identifier of the event rsvp to update.
            is_attending:
                Indicates if the user is attending the event.
            is_confirmed:
                Indicates if the RSVP is confirmed.
            agent_user_id:
                Identifier for the agent user, if applicable.
            source:
                Source of the RSVP.
            source_system:
                System from which the RSVP originated.


        Returns:
            Boolean representing success of the operation.
            True if the operation was successful, False otherwise.

        Raises:
            STUnexpectedResponseCodeError: If the operation fails with an unexpected status code.

        Documentation Reference:
            `<https://www.solidarity.tech/reference/put_event-rsvps-id>`__

        """
        payload = {
            is_attending: is_attending,
            is_confirmed: is_confirmed,
            agent_user_id: agent_user_id,
            source: source,
            source_system: source_system,
        }
        res = self._put_request(
            "event_rsvps",
            id,
            payload,
            additional_headers={"content-type": "application/json"},
        )

        if res.status_code not in (200, 404):
            raise STUnexpectedResponseCodeError(res)

        return res.status_code == 200

    def delete_event_rsvp(
        self,
        id: str,
    ) -> bool:
        """
        Delete an event rsvp with the specified ID.

        Args:
            id:
                Identifier of the event rsvp to delete

        Returns:
            Boolean representing success of the operation.
            True if the operation was successful, False otherwise.

        Raises:
            STUnexpectedResponseCodeError: If the operation fails with an unexpected status code.

        Documentation Reference:
            `<https://www.solidarity.tech/reference/delete_event-rsvps-id>`__

        """
        res = self._del_request(
            "event_rsvps",
            id,
        )

        if res and res.status_code != 404:
            raise STUnexpectedResponseCodeError(res)

        return not res.status_code
