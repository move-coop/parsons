import logging

from parsons.solidarity_tech.solidarity_tech_base import SolidarityTechBase

logger = logging.getLogger(__name__)


class SolidarityTechFieldSurveyURLs(SolidarityTechBase):
    def generate_field_survey_url(
        self,
        user_id: int,
        agent_user_id: int,
        page_id: int,
    ) -> bool:
        """
        Generates a field survey URL for the given user, agent, and page.

        Response contains complete URL with access token (expires in 24 hours),
        and an ISO 8601 timestamp of when the access token expires.

        Args:
            user_id:
                The ID of the user to generate URL for.
            agent_user_id:
                The ID of the agent user.
            page_id:
                The ID of the action page (field survey).

        Raises:
            :class:`STFailedResponseError`: If the operation fails with a known error code.
            :class:`STUnexpectedResponseError`: If the operation fails with an unexpected status code.

        Returns:
            Boolean representing success of the operation.
            True if the operation was successful, False otherwise.

        Documentation Reference:
            `<https://www.solidarity.tech/reference/post_field-survey-urls>`__

        """
        payload = {
            "user_id": user_id,
            "agent_user_id": agent_user_id,
            "page_id": page_id,
        }
        res = self._post_request(
            "field_survey_urls",
            payload=payload,
            additional_headers={"accept": "application/json", "content-type": "application/json"},
        )

        expected_responses = {
            200: (True, "field survey URL generated"),
            404: (False, "user, agent, or page not found"),
            422: (False, "missing required parameters"),
        }
        return self._handle_status_codes(res=res, codes=expected_responses)
