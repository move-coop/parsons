import logging
from datetime import datetime
from typing import Literal

import numpy as np
from requests.exceptions import HTTPError

from parsons.solidarity_tech.exceptions import STUnexpectedResponseCodeError
from parsons.solidarity_tech.solidarity_tech_base import SolidarityTechBase

logger = logging.getLogger(__name__)


class SolidarityTechUserActions(SolidarityTechBase):
    def get_user_actions(
        self,
        user_id: int | None = None,
        page_id: int | None = None,
        group_by: Literal["referred_by_user"] | None = None,
        limit: int = 20,
        offset: int = 0,
        since: int | datetime = 0,
    ) -> str:
        """
        Lists user actions (form submissions).

        .. admonition:: Filtering

            Can be filtered by ``user_id``, ``page_id``, or both.
            To get custom form responses for event RSVPs,
            first get the event's ``event_page_id`` from
            ``GET /events/{id}``, then query this endpoint with that page_id.
            Match to RSVPs by user_id.
            With ``group_by=referred_by_user`` the response becomes a
            eferral leaderboard instead of submission rows.
            There is one row per referrer
            (``{referred_by_user_id, count, user: {id, first_name, last_name}}``),
            ordered by submission count descending, honoring the same filters.

        Args:
            user_id:
                Filter by user ID.
            page_id:
                Filter by page ID
            group_by:
                Set to referred_by_user for a referral leaderboard
                (see the endpoint description).
                Any other value returns 422.
            limit:
                Limits the number of items returned.
                Default is 20, maximum is 100.
            offset:
                Number of items to skip before starting to return the results.
            since:
                UTC timestamp in seconds since the Unix epoch to filter calls created after this time.

        Returns:
            All the user actions.

        Documentation Reference:
            `<https://www.solidarity.tech/reference/get_user-actions>`__

        """
        params = {
            "user_id": user_id,
            "page_id": page_id,
            "group_by": group_by,
        }
        res = self._get_resources(
            "user_actions",
            limit=limit,
            offset=offset,
            since=since,
            params=params,
            additional_headers={"accept": "application/json"},
        )

        if res.status_code not in (200, 422):
            raise STUnexpectedResponseCodeError(res)

        if res.status_code == 422:
            err_msg = "Could not process request. group_by value may be invalid."
            raise HTTPError(err_msg, response=res)

        return res.text

    def create_user_action(
        self,
        page_id: np.int64,
        user_id: np.int64 | None = None,
        created_at: np.int64 | None = None,
        data: dict[str, str | int | bool | dict[str, str]] | None = None,
    ) -> bool:
        """
        Creates a user action for a user.

        .. note::

            This endpoint cannot be used for creating actions
            related to donation pages or scheduled call pages.

        Args:
            page_id:
                Identifier for the Page, required for new user actions.
            user_id:
                Identifier for the User.
            created_at:
                UTC timestamp in seconds since the Unix epoch for the creation time of the user action
            data:
                Action data. See documentation.

        Returns:
            Boolean representing success of the operation.
            True if the operation was successful, False otherwise.

        Raises:
            ValueError: If neither ``user_id``, ``phone_number``, nor ``email`` is provided.
            HTTPError: If the operation fails with a 422 status code.
            STUnexpectedResponseCodeError: If the operation fails with an unexpected status code.

        Documentation Reference:
            `<https://www.solidarity.tech/reference/post_user-actions>`__

        """
        if (
            not page_id
            and isinstance(data, dict)
            and "phone_number" not in data
            and "email" not in data
        ):
            raise ValueError("Either user_id, phone_number, or email must be provided")

        payload = {
            "page_id": page_id,
            "user_id": user_id,
            "created_at": created_at,
            "data": data,
        }
        res = self._post_request(
            "user_actions",
            payload=payload,
            additional_headers={"content-type": "application/json"},
        )

        if res.status_code not in (201, 422):
            raise STUnexpectedResponseCodeError(res)

        if res.status_code == 422:
            raise HTTPError(
                "Request could not be processed, provided data may be invalid", response=res
            )

        return res.status_code == 201
