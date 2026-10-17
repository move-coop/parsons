"""Connector class for interacting with the SolidarityTech Event Attendances endpoint."""

from __future__ import annotations

import logging
from http import HTTPStatus
from typing import TYPE_CHECKING

from parsons import Table
from parsons.solidarity_tech.base import SolidarityTechBase

if TYPE_CHECKING:
    from datetime import datetime

    from parsons.solidarity_tech.datatypes import EventAttendanceData, Metadata
    from parsons.utilities.api_connector import _JsonType


logger = logging.getLogger(__name__)


class SolidarityTechEventAttendances(SolidarityTechBase):
    """Methods for interacting with the SolidarityTech event attendances endpoint."""

    def get_event_attendances(
        self,
        limit: int = 20,
        offset: int = 0,
        since: int | datetime = 0,
        event_id: int | None = None,
        session_id: int | None = None,
    ) -> tuple[Table, Metadata]:
        """
        Retrieve a list of event attendances.

        Args:
            limit:
                Limits the number of items returned.
                Default is 20, maximum is 100.
            offset:
                Number of items to skip before starting to return the results.
            since:
                UTC timestamp in seconds since the Unix epoch to filter calls created after this time.
            event_id:
                Filters attendances by event_id within the accessible scope.
            session_id:
                Filters attendances by session_id (calendar item id) within the accessible scope.

        Raises:
            :class:`STFailedResponseError`: If the operation fails with a known error code.
            :class:`STUnexpectedResponseError`: If the operation fails with an unexpected status code.

        Returns:
            A list of event attendance entries, along with requested metadata.

        Documentation Reference:
            `<https://www.solidarity.tech/reference/get_event-attendances>`__

        """
        params: dict[str, _JsonType] = {}
        _ = event_id is not None and params.update({"event_id": event_id})
        _ = session_id is not None and params.update({"session_id": session_id})

        res = self._get_resources(
            "event_attendances",
            limit=limit,
            offset=offset,
            since=since,
            params=params,
        )

        expected_responses = {HTTPStatus.OK: (True, "event attendances listed")}
        self._handle_status_codes(res=res, codes=expected_responses)

        data: list[EventAttendanceData] = res.json()["data"]
        meta: Metadata = res.json()["meta"]

        return Table(data, name="Solidarity Tech Event Attendances"), meta

    def create_event_attendance(
        self,
        event_id: int,
        event_session_id: int,
        user_id: int,
        *,
        attended: bool,
    ) -> EventAttendanceData:
        """
        Create an event attendance with the specified details.

        Args:
            event_id:
                Identifier for the Mobilize event.
            event_session_id:
                Identifier for the specific event session.
            user_id:
                Identifier for the user attending to the event.
            attended:
                Indicates if the user attended the event.

        Raises:
            :class:`STFailedResponseError`: If the operation fails with a known error code.
            :class:`STUnexpectedResponseError`: If the operation fails with an unexpected status code.

        Returns:
            A single event attendance entry, as it exists after creating.

        Documentation Reference:
            `<https://www.solidarity.tech/reference/post_event-attendances>`__

        """
        payload: dict[str, _JsonType] = {
            "attended": attended,
            "event_id": event_id,
            "event_session_id": event_session_id,
            "user_id": user_id,
        }

        res = self._post_request(
            "event_attendances",
            payload=payload,
            additional_headers={"content-type": "application/json"},
        )

        expected_responses = {
            HTTPStatus.CREATED: (True, "event attendance created"),
            HTTPStatus.NOT_FOUND: (False, "event not found"),
        }
        self._handle_status_codes(res=res, codes=expected_responses)

        data: EventAttendanceData = res.json()["data"]

        return data

    def delete_event_attendance(
        self,
        resource_id: int,
    ) -> bool:
        """
        Delete an event attendance with the specified ID.

        Args:
            resource_id:
                Identifier of the event attendance to delete

        Raises:
            :class:`STFailedResponseError`: If the operation fails with a known error code.
            :class:`STUnexpectedResponseError`: If the operation fails with an unexpected status code.

        Returns:
            Boolean representing success of the operation.
            True if the operation was successful, False otherwise.

        Documentation Reference:
            `<https://www.solidarity.tech/reference/delete_event-attendances-id>`__

        """
        res = self._delete_request(
            "event_attendances",
            resource_id,
        )

        expected_responses = {
            HTTPStatus.OK: (True, "event attendance deleted"),
            HTTPStatus.NOT_FOUND: (False, "event attendance not found"),
        }
        self._handle_status_codes(res=res, codes=expected_responses)

        result = res.json()

        return ("message" in result) and (
            result["message"] == "Event attendance successfully deleted."
        )
