"""Tests for the Field Survey URLs methods of :class:`~parsons.solidarity_tech.SolidarityTech`."""

from __future__ import annotations

from http import HTTPStatus
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from requests_mock import Mocker

    from parsons.solidarity_tech import SolidarityTech

ENDPOINT = "field_survey_urls"


class TestGenerateFieldSurveyURL:
    #    @pytest.mark.vcr
    #    def test_generate_field_survey_url_live(self, st: SolidarityTech) -> None:
    #        """Verify that :meth:`~parsons.solidarity_tech.SolidarityTech.generate_field_survey_url` returns the data for the generated URL."""
    #        user_id = 1191722
    #        agent_user_id = 1191722
    #        page_id = 5315
    #
    #        field_survey_url = st.generate_field_survey_url(
    #            user_id=user_id,
    #            agent_user_id=agent_user_id,
    #            page_id=page_id,
    #        )
    #
    #        assert isinstance(field_survey_url["url"], str)
    #        assert isinstance(field_survey_url["expires_at"], str)

    def test_generate_field_survey_url(self, st: SolidarityTech, requests_mock: Mocker) -> None:
        """Verify that :meth:`~parsons.solidarity_tech.SolidarityTech.generate_field_survey_url` makes the appropriate calls."""
        user_id = 1191722
        agent_user_id = 1191722
        page_id = 5315
        endpoint_url = f"{st.api_url}{ENDPOINT}"

        _ = requests_mock.post(
            endpoint_url,
            status_code=HTTPStatus.OK,
            json={
                "url": "https://example.com/field-survey/volunteer-survey?access_token=abc123&user_id=456",
                "expires_at": "2025-11-14T10:30:00Z",
            },
        )

        _ = st.generate_field_survey_url(
            user_id=user_id,
            agent_user_id=agent_user_id,
            page_id=page_id,
        )

        assert requests_mock.call_count == 1
        assert requests_mock.last_request is not None
        assert requests_mock.last_request.method == "POST"
        assert requests_mock.last_request.url == endpoint_url
        assert requests_mock.last_request.json()["user_id"] == user_id
        assert requests_mock.last_request.json()["agent_user_id"] == agent_user_id
        assert requests_mock.last_request.json()["page_id"] == page_id
