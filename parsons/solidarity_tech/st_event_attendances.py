import logging
from datetime import datetime

import numpy as np

from parsons import Table
from parsons.solidarity_tech.solidarity_tech_base import SolidarityTechBase

logger = logging.getLogger(__name__)


class SolidarityTechEventAttendances(SolidarityTechBase):
    def get_event_attendances(
        self,
        limit: int = 20,
        offset: int = 0,
        since: int | datetime = 0,
        event_id: int | None = None,
        session_id: int | None = None,
    ) -> Table:
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
            All the event attendance entries.

        Documentation Reference:
            `<https://www.solidarity.tech/reference/get_event-attendances>`__

        """
        params = {"event_id": event_id, "session_id": session_id}
        res = self._get_resources(
            "event_attendances",
            limit=limit,
            offset=offset,
            since=since,
            params=params,
        )

        expected_responses = {200: (True, "event attendances listed")}
        self._handle_status_codes(res=res, codes=expected_responses)

        return Table(res.json())

    def create_event_attendance(
        self,
        event_id: np.int64,
        event_session_id: np.int64,
        user_id: np.int64,
        attended: bool,
    ) -> bool:
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
            Boolean representing success of the operation.
            True if the operation was successful, False otherwise.

        Documentation Reference:
            `<https://www.solidarity.tech/reference/post_event-attendances>`__

        """
        payload = {
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
            201: (True, "event attendance created"),
            404: (False, "event not found"),
        }
        return self._handle_status_codes(res=res, codes=expected_responses)

    def delete_event_attendance(
        self,
        id: str,
    ) -> bool:
        """
        Delete an event attendance with the specified ID.

        Args:
            id:
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
        res = self._del_request(
            "event_attendances",
            id,
        )

        expected_responses = {
            200: (True, "event attendance deleted"),
            404: (False, "event attendance not found"),
        }
        return self._handle_status_codes(res=res, codes=expected_responses)
