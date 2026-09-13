"""Connector class for interacting with the SolidarityTech Field Survey URLs endpoint."""

from __future__ import annotations

import logging
from http import HTTPStatus
from typing import TYPE_CHECKING

from parsons.solidarity_tech.base import SolidarityTechBase, _JsonType

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from parsons.solidarity_tech.datatypes import FieldSurveyURL


class SolidarityTechFieldSurveyURLs(SolidarityTechBase):
    """Methods for interacting with the SolidarityTech Field Survey URLs endpoint."""

    def generate_field_survey_url(
        self,
        user_id: int,
        agent_user_id: int,
        page_id: int,
    ) -> FieldSurveyURL:
        """
        Generate a field survey URL for the given user, agent, and page.

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
            URL and expiration timestamp.

        Documentation Reference:
            `<https://www.solidarity.tech/reference/post_field-survey-urls>`__

        """
        payload: dict[str, _JsonType] = {
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
            HTTPStatus.OK: (True, "field survey URL generated"),
            HTTPStatus.NOT_FOUND: (False, "user, agent, or page not found"),
            HTTPStatus.UNPROCESSABLE_ENTITY: (False, "missing required parameters"),
        }
        self._handle_status_codes(res=res, codes=expected_responses)

        return res.json()
