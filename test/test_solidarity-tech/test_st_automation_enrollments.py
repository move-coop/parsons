"""Tests for the Automation Enrollments methods of :class:`~parsons.solidarity_tech.SolidarityTech`."""

from __future__ import annotations

from http import HTTPStatus
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from requests_mock import Mocker

    from parsons.solidarity_tech import SolidarityTech

ENDPOINT = "automation_enrollments"


class TestEnrollUserInAutomation:
    # TODO(bmos): Implement this. Currently no example of what expected output will be.
    # @pytest.mark.vcr
    # def test_enroll_user_in_automation_live(self, st: SolidarityTech) -> None:
    #     """Verify that :meth:`~parsons.solidarity_tech.SolidarityTech.enroll_user_in_automation` returns the result."""
    #     automation_id = 2598823
    #     user_id = 1191722
    #
    #     result = st.enroll_user_in_automation(automation_id=automation_id, user_id=user_id)
    #
    #     assert isinstance(result, dict)

    def test_enroll_user_in_automation(self, st: SolidarityTech, requests_mock: Mocker) -> None:
        """Verify that :meth:`~parsons.solidarity_tech.SolidarityTech.enroll_user_in_automation` makes the appropriate calls."""
        automation_id = 2598823
        user_id = 1191722
        endpoint_url = f"{st.api_url}{ENDPOINT}"
        _ = requests_mock.post(endpoint_url, status_code=HTTPStatus.CREATED, json={"data": {}})

        _ = st.enroll_user_in_automation(automation_id=automation_id, user_id=user_id)

        assert requests_mock.call_count == 1
        assert requests_mock.last_request is not None
        assert requests_mock.last_request.method == "POST"
        assert requests_mock.last_request.url == endpoint_url
        assert requests_mock.last_request.json()["automation_id"] == automation_id
        assert requests_mock.last_request.json()["user_id"] == user_id
