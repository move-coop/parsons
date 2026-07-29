import logging

from requests.exceptions import HTTPError

from parsons.solidarity_tech.exceptions import STUnexpectedResponseCodeError
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

        Returns:
            Boolean representing success of the operation.
            True if the operation was successful, False otherwise.

        Raises:
            HTTPError: If user, agent, or page are not found.
            HTTPError: If required parameters are missing.
            STUnexpectedResponseCodeError: If the operation fails with an unexpected status code.

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
            payload,
            additional_headers={"accept": "application/json", "content-type": "application/json"},
        )

        if res.status_code not in (200, 404, 409, 422):
            raise STUnexpectedResponseCodeError(res)

        if res.status_code == 404:
            raise HTTPError("User, agent, or page not found", response=res)

        if res.status_code == 422:
            raise HTTPError("Required parameters are missing", response=res)

        return res.status_code == 200
