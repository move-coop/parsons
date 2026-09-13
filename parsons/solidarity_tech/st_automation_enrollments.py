"""Connector class for interacting with the SolidarityTech Automation Enrollments endpoint."""

from __future__ import annotations

import logging
from http import HTTPStatus

from parsons.solidarity_tech.base import SolidarityTechBase, _JsonType

logger = logging.getLogger(__name__)


class SolidarityTechAutomationEnrollments(SolidarityTechBase):
    """Methods for interacting with the SolidarityTech automation enrollments endpoint."""

    def enroll_user_in_automation(
        self,
        automation_id: int,
        user_id: int,
    ) -> dict[str, _JsonType]:
        """
        Retrieve a list of agent assignments.

        Args:
            automation_id:
                The ID of the automation to enroll the user in.
            user_id:
                The ID of the user to enroll.

        Raises:
            :class:`STFailedResponseError`: If the operation fails with a known error code.
            :class:`STUnexpectedResponseError`: If the operation fails with an unexpected status code.

        Returns:
            Boolean representing success of the operation.
            True if the operation was successful, False otherwise.

        Documentation Reference:
            `<https://www.solidarity.tech/reference/post_automation-enrollments>`__

        """
        payload: dict[str, _JsonType] = {"automation_id": automation_id, "user_id": user_id}

        res = self._post_request(
            "automation_enrollments",
            payload=payload,
            additional_headers={"content-type": "application/json"},
        )

        expected_responses = {
            HTTPStatus.CREATED: (True, "enrollment created"),
            HTTPStatus.FORBIDDEN: (False, "automation not accessible"),
            HTTPStatus.UNPROCESSABLE_ENTITY: (False, "inactive automation"),
        }
        self._handle_status_codes(res=res, codes=expected_responses)

        return res.json()["data"]
