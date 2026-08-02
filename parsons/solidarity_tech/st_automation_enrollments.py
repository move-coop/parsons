import logging

from parsons.solidarity_tech.solidarity_tech_base import SolidarityTechBase

logger = logging.getLogger(__name__)


class SolidarityTechAutomationEnrollments(SolidarityTechBase):
    def enroll_user_in_automation(
        self,
        automation_id: int,
        user_id: int,
    ) -> bool:
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
        payload = {"automation_id": automation_id, "user_id": user_id}
        res = self._post_request(
            "automation_enrollments",
            payload=payload,
            additional_headers={"content-type": "application/json"},
        )

        expected_responses = {
            201: (True, "enrollment created"),
            403: (False, "automation not accessible"),
            422: (False, "inactive automation"),
        }
        return self._handle_status_codes(res=res, codes=expected_responses)
