from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import TYPE_CHECKING

import pytest
import requests
from requests_mock import GET, POST, Mocker

from parsons.solidarity_tech.exceptions import STFailedResponseError, STUnexpectedResponseError

if TYPE_CHECKING:
    from pytest_mock import MockerFixture

    from parsons.solidarity_tech import SolidarityTech
    from parsons.utilities.api_connector import _JsonType, _ParamsType


@pytest.fixture
def known_status_codes() -> dict[int, tuple[bool, str]]:
    """Known status codes and their expected outcomes."""
    return {
        200: (True, "OK"),
        201: (True, "updated resource"),
        404: (False, "could not find resource"),
        422: (False, "could not process request"),
    }


class Test_Post_Request:
    """Tests for the _post_request method."""

    @pytest.mark.parametrize(
        "endpoint", ["custom_user_properties", "event_sessions/295876/hosts", "field_survey_urls"]
    )
    def test_get_single_resource_handles_varied_endpoints(
        self, st: SolidarityTech, requests_mock: Mocker, mocker: MockerFixture, endpoint: str
    ) -> None:
        """Make a POST request to varied endpoints."""
        endpoint_url = f"{st.api_url}/{endpoint}"

        requests_mock.post(endpoint_url)
        spy = mocker.spy(st.api, "request")

        st._post_request(endpoint)

        spy.assert_called_once_with(url=endpoint_url, req_type=POST)

    def test_get_single_resource_makes_request_with_payload(
        self, st: SolidarityTech, requests_mock: Mocker, mocker: MockerFixture
    ) -> None:
        """Makes a POST request with payload."""
        payload: _JsonType = {"user_id": 654123}

        requests_mock.post(st.api_url)
        spy = mocker.spy(st.api, "request")

        st._post_request(st.api_url, payload=payload)

        spy.assert_called_once_with(url=st.api_url, req_type=POST, json=payload)

    def test_get_single_resource_makes_request_with_params(
        self, st: SolidarityTech, requests_mock: Mocker, mocker: MockerFixture
    ) -> None:
        """Make a POST request with params."""
        params: _ParamsType = {"automation_id": 35876}

        requests_mock.post(st.api_url)
        spy = mocker.spy(st.api, "request")

        st._post_request(st.api_url, params=params)

        spy.assert_called_once_with(url=st.api_url, req_type=POST, json=None, params=params)


class Test_Get_Single_Resource:
    """Tests for the _get_single_resource method."""

    def test_get_single_resource_makes_request_with_id(
        self, st: SolidarityTech, requests_mock: Mocker, mocker: MockerFixture
    ) -> None:
        """Make a GET request with an ID."""
        id = 42
        endpoint = "users"
        endpoint_url = f"{st.api_url}/{endpoint}/{id}"

        requests_mock.get(endpoint_url)
        spy = mocker.spy(st.api, "request")

        st._get_single_resource(endpoint, id)

        spy.assert_called_once_with(url=endpoint_url, req_type=GET)


class Test_Get_Resources:
    """Tests for the _get_resources method."""

    @pytest.mark.parametrize("endpoint", ["activities", "agent_assignments", "users/124876"])
    def test_get_resources_makes_request(
        self, st: SolidarityTech, requests_mock: Mocker, mocker: MockerFixture, endpoint: str
    ) -> None:
        """Make a GET request to varied endpoints."""
        endpoint_url = f"{st.api_url}/{endpoint}"

        requests_mock.get(endpoint_url)
        spy = mocker.spy(st.api, "request")

        st._get_resources(endpoint)

        spy.assert_called_once_with(url=endpoint_url, req_type=GET)

    def test_get_resources_datetime(
        self,
        st: SolidarityTech,
        requests_mock: Mocker,
        mocker: MockerFixture,
    ) -> None:
        """Convert datetime-typed ``since``."""
        now_datetime = datetime.now(tz=timezone.utc)
        now_timestamp = int(now_datetime.timestamp())

        requests_mock.get(st.api_url)
        spy = mocker.spy(st.api, "request")

        st._get_resources(
            st.api_url,
            since=now_datetime,
        )
        spy.assert_called_once_with(
            url=st.api_url,
            req_type=GET,
            params={"_since": now_timestamp},
        )

    def test_get_resources_remaps_special_query_strings(
        self,
        st: SolidarityTech,
        requests_mock: Mocker,
        mocker: MockerFixture,
    ) -> None:
        """Integrate special query names provided as keyword arguments."""
        requests_mock.get(st.api_url)
        spy = mocker.spy(st.api, "request")

        st._get_resources(
            st.api_url,
            limit=123456,
            cursor=654321,
            offset=321456,
            since=456321,
            include_count=123654,
        )

        spy.assert_called_once_with(
            url=st.api_url,
            req_type=GET,
            params={
                "_limit": 123456,
                "_cursor": 654321,
                "_offset": 321456,
                "_since": 456321,
                "_include_count": 123654,
            },
        )

    def test_get_resources_param_collision_error(
        self,
        st: SolidarityTech,
        requests_mock: Mocker,
    ) -> None:
        """Raise a :class:`KeyError` when a query passed in keyword arguments collides with one passed in params."""
        requests_mock.get(st.api_url)

        with pytest.raises(KeyError, match="Request param '_limit' already exists"):
            st._get_resources(st.api_url, limit=15, params={"_limit": 30})


class Test_Add_If_Field_Not_Empty:
    """Test the ``_add_if_field_not_empty`` method."""

    @pytest.mark.parametrize(
        ("key", "value", "expected"),
        [
            ("test_key1", "test_value", {"test_key1": "test_value"}),
            ("test_key2", 123456, {"test_key2": 123456}),
            ("test_key_none", None, {}),
        ],
    )
    def test_add_if_field_not_empty(
        self,
        st: SolidarityTech,
        key: str,
        value: str | int | None,
        expected: dict[str, str | int],
    ) -> None:
        """Add only items with a value."""
        init_dict = {}
        result = st._add_if_field_not_empty(init_dict, key, value)
        assert result == expected

    def test_add_if_field_not_empty_overwrite(self, st: SolidarityTech) -> None:
        """Overwrite existing keys when ``overwrite`` is ``True``."""
        init_dict = {"test_key": "original_value"}
        result = st._add_if_field_not_empty(
            init_dict, "test_key", "overwrite_value", overwrite=True
        )
        assert result["test_key"] == "overwrite_value"

    def test_add_if_field_not_empty_no_overwrite_default(self, st: SolidarityTech) -> None:
        """Don't overwrite existing keys when ``overwrite`` is not provided."""
        init_dict = {"test_key": "original_value"}
        with pytest.raises(KeyError, match="'test_key' already exists"):
            st._add_if_field_not_empty(init_dict, "test_key", "overwrite_value")

    def test_add_if_field_not_empty_no_overwrite(self, st: SolidarityTech) -> None:
        """Raise a :class`KeyError` when ``overwrite`` is ``False`` and the key already exists."""
        init_dict = {"test_key": "original_value"}
        with pytest.raises(KeyError, match="'test_key' already exists"):
            st._add_if_field_not_empty(init_dict, "test_key", "overwrite_value", overwrite=False)


class Test_Handle_Status_Codes:
    """Test the ``_handle_status_codes`` method."""

    @pytest.mark.parametrize(
        "status_code",
        [200, 201, 404, 422],
    )
    def test_handle_status_codes(
        self,
        st: SolidarityTech,
        requests_mock: Mocker,
        known_status_codes: dict[int, tuple[bool, str]],
        status_code: int,
    ) -> None:
        """
        Handle known status codes.

        Raise a :class:`STFailedResponseError` if parsing a known failure status code,
        return ``True`` if parsing a known success status code.

        """
        requests_mock.get("https://api.example.com", status_code=status_code)
        res = requests.get("https://api.example.com")

        success_expected = known_status_codes[status_code][0]
        if success_expected:
            assert st._handle_status_codes(res, known_status_codes)
        else:
            failure_description = known_status_codes[status_code][1]
            err_msg = re.escape(
                f"Request Failed (Status Code {status_code}) -- {failure_description}"
            )
            with pytest.raises(STFailedResponseError, match=err_msg):
                st._handle_status_codes(res, known_status_codes)

    def test_handle_status_codes_unrecognized(
        self,
        st: SolidarityTech,
        requests_mock: Mocker,
        known_status_codes: dict[int, tuple[bool, str]],
    ) -> None:
        """Raise a :class:`STUnexpectedResponseError` if parsing an unrecognized status code."""
        status_code = 500

        requests_mock.get("https://api.example.com", status_code=status_code)
        res = requests.get("https://api.example.com")

        with pytest.raises(
            STUnexpectedResponseError,
            match=re.escape(f"Unexpected Response (Status Code {status_code})"),
        ):
            st._handle_status_codes(res, known_status_codes)
