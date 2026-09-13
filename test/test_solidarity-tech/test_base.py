"""Tests for :class:`~parsons.solidarity_tech.base.SolidarityTechBase`."""

from __future__ import annotations

import re
from datetime import datetime, timezone
from http import HTTPStatus
from typing import TYPE_CHECKING
from urllib.parse import urlencode, urlsplit

import pytest
import requests

from parsons.solidarity_tech.exceptions import (
    STFailedAuthenticationError,
    STFailedResponseError,
    STUnexpectedResponseError,
)

if TYPE_CHECKING:
    from requests_mock import Mocker

    from parsons.solidarity_tech import SolidarityTech
    from parsons.utilities.api_connector import _JsonType, _ParamsType


@pytest.fixture
def known_status_codes() -> dict[int, tuple[bool, str]]:
    """Known status codes and their expected outcomes."""
    return {
        HTTPStatus.OK: (True, "OK"),
        HTTPStatus.CREATED: (True, "updated resource"),
        HTTPStatus.NOT_FOUND: (False, "could not find resource"),
        HTTPStatus.UNPROCESSABLE_ENTITY: (False, "could not process request"),
    }


class TestDeleteRequest:
    """Tests for :meth:`parsons.solidarity_tech.SolidarityTech._delete_request`."""

    def test_delete_request(self, st: SolidarityTech, requests_mock: Mocker) -> None:
        """Make a DELETE request with an ID."""
        resource_id = 42
        endpoint = "users"
        endpoint_url = f"{st.api_url}{endpoint}/{resource_id}"
        _ = requests_mock.delete(endpoint_url, json={"id": resource_id})

        _ = st._delete_request(endpoint, resource_id)

        assert requests_mock.call_count == 1
        assert requests_mock.last_request is not None
        assert requests_mock.last_request.method == "DELETE"
        assert requests_mock.last_request.url == endpoint_url


class TestPutRequest:
    """Tests for :meth:`parsons.solidarity_tech.SolidarityTech._put_request`."""

    def test_put_request(self, st: SolidarityTech, requests_mock: Mocker) -> None:
        """Make a GET request with an ID."""
        resource_id = 42
        endpoint = "users"
        endpoint_url = f"{st.api_url}{endpoint}/{resource_id}"
        _ = requests_mock.put(endpoint_url, json={"id": resource_id})

        _ = st._put_request(endpoint, resource_id)

        assert requests_mock.call_count == 1
        assert requests_mock.last_request is not None
        assert requests_mock.last_request.method == "PUT"
        assert requests_mock.last_request.url == endpoint_url


class TestPostRequest:
    """Tests for :meth:`parsons.solidarity_tech.SolidarityTech._post_request`."""

    @pytest.mark.parametrize(
        "endpoint", ["custom_user_properties", "event_sessions/295876/hosts", "field_survey_urls"]
    )
    def test_post_request_handles_varied_endpoints(
        self, st: SolidarityTech, requests_mock: Mocker, endpoint: str
    ) -> None:
        """Make a POST request to varied endpoints."""
        endpoint_url = f"{st.api_url}{endpoint}"
        _ = requests_mock.post(endpoint_url)

        _ = st._post_request(endpoint)

        assert requests_mock.call_count == 1
        assert requests_mock.last_request is not None
        assert requests_mock.last_request.method == "POST"
        assert requests_mock.last_request.url == endpoint_url

    def test_post_request_makes_request_with_payload(
        self, st: SolidarityTech, requests_mock: Mocker
    ) -> None:
        """Makes a POST request with payload."""
        payload: _JsonType = {"user_id": 654123}
        _ = requests_mock.post(st.api_url)

        _ = st._post_request(st.api_url, payload=payload)

        assert requests_mock.call_count == 1
        assert requests_mock.last_request is not None
        assert requests_mock.last_request.method == "POST"
        assert requests_mock.last_request.url == st.api_url
        assert requests_mock.last_request.json() == payload

    def test_post_request_makes_request_with_params(
        self, st: SolidarityTech, requests_mock: Mocker
    ) -> None:
        """Make a POST request with params."""
        params: _ParamsType = {"automation_id": 35876}
        _ = requests_mock.post(st.api_url)

        _ = st._post_request(st.api_url, params=params)

        assert requests_mock.call_count == 1
        assert requests_mock.last_request is not None
        assert requests_mock.last_request.method == "POST"

        last_url = urlsplit(requests_mock.last_request.url)
        assert f"{last_url.scheme}://{last_url.netloc}{last_url.path}" == st.api_url
        assert last_url.query == urlencode(params)


class TestGetSingleResource:
    """Tests for :meth:`parsons.solidarity_tech.SolidarityTech._get_single_resource`."""

    def test_get_single_resource_makes_request_with_id(
        self, st: SolidarityTech, requests_mock: Mocker
    ) -> None:
        """Make a GET request with an ID."""
        resource_id = 42
        endpoint = "users"
        endpoint_url = f"{st.api_url}{endpoint}/{resource_id}"
        _ = requests_mock.get(endpoint_url, json={"id": resource_id})

        _ = st._get_single_resource(endpoint, resource_id)

        assert requests_mock.call_count == 1
        assert requests_mock.last_request is not None
        assert requests_mock.last_request.method == "GET"
        assert requests_mock.last_request.url == endpoint_url


class TestGetResources:
    """Tests for :meth:`parsons.solidarity_tech.SolidarityTech._get_resources`."""

    @pytest.mark.parametrize("endpoint", ["activities", "agent_assignments", "users/124876"])
    def test_get_resources_makes_request(
        self, st: SolidarityTech, requests_mock: Mocker, endpoint: str
    ) -> None:
        """Make a GET request to varied endpoints."""
        endpoint_url = f"{st.api_url}{endpoint}"
        _ = requests_mock.get(endpoint_url)

        _ = st._get_resources(endpoint)

        assert requests_mock.call_count == 1
        assert requests_mock.last_request is not None
        assert requests_mock.last_request.method == "GET"
        assert requests_mock.last_request.url == endpoint_url

    def test_get_resources_datetime(
        self,
        st: SolidarityTech,
        requests_mock: Mocker,
    ) -> None:
        """Convert datetime-typed ``since``."""
        now_datetime = datetime.now(tz=timezone.utc)
        now_timestamp = int(now_datetime.timestamp())
        _ = requests_mock.get(st.api_url)

        _ = st._get_resources(
            st.api_url,
            since=now_datetime,
        )

        assert requests_mock.call_count == 1
        assert requests_mock.last_request is not None
        assert requests_mock.last_request.method == "GET"

        last_url = urlsplit(requests_mock.last_request.url)
        assert f"{last_url.scheme}://{last_url.netloc}{last_url.path}" == st.api_url
        assert last_url.query == urlencode({"_since": now_timestamp})

    def test_get_resources_remaps_special_query_strings(
        self,
        st: SolidarityTech,
        requests_mock: Mocker,
    ) -> None:
        """Integrate special query names provided as keyword arguments."""
        _ = requests_mock.get(st.api_url)

        _ = st._get_resources(
            st.api_url,
            limit=123456,
            cursor=654321,
            offset=321456,
            since=456321,
            include_count=123654,
        )

        assert requests_mock.call_count == 1
        assert requests_mock.last_request is not None
        assert requests_mock.last_request.method == "GET"

        last_url = urlsplit(requests_mock.last_request.url)
        assert f"{last_url.scheme}://{last_url.netloc}{last_url.path}" == st.api_url
        assert last_url.query == urlencode(
            {
                "_limit": 123456,
                "_cursor": 654321,
                "_offset": 321456,
                "_since": 456321,
                "_include_count": 123654,
            }
        )

    def test_get_resources_param_collision_error(
        self,
        st: SolidarityTech,
        requests_mock: Mocker,
    ) -> None:
        """Raise a :class:`KeyError` when a query passed in keyword arguments collides with one passed in params."""
        _ = requests_mock.get(st.api_url)

        with pytest.raises(KeyError, match="Request param '_limit' already exists"):
            _ = st._get_resources(st.api_url, limit=15, params={"_limit": 30})

    def test_get_resources_does_not_include_params_with_none_value(
        self,
        st: SolidarityTech,
        requests_mock: Mocker,
    ) -> None:
        """Skip queries passed in params that have the value of None."""
        _ = requests_mock.get(st.api_url)

        _ = st._get_resources(st.api_url, params={"_limit": None})

        assert requests_mock.call_count == 1
        assert requests_mock.last_request is not None
        assert requests_mock.last_request.method == "GET"
        assert requests_mock.last_request.url == st.api_url


class TestHandleStatusCodes:
    """Test :meth:`parsons.solidarity_tech.SolidarityTech._handle_status_codes`."""

    @pytest.mark.parametrize(
        "status_code",
        [HTTPStatus.OK, HTTPStatus.CREATED, HTTPStatus.NOT_FOUND, HTTPStatus.UNPROCESSABLE_ENTITY],
    )
    def test_handle_status_codes(
        self,
        st: SolidarityTech,
        requests_mock: Mocker,
        known_status_codes: dict[HTTPStatus, tuple[bool, str]],
        status_code: HTTPStatus,
    ) -> None:
        """
        Handle known status codes.

        Raise a :class:`STFailedResponseError` if parsing a known failure status code,
        return ``True`` if parsing a known success status code.

        """
        _ = requests_mock.get("https://api.example.com", status_code=status_code)
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
                _ = st._handle_status_codes(res, known_status_codes)

    def test_handle_status_codes_unauthorized(
        self,
        st: SolidarityTech,
        requests_mock: Mocker,
        known_status_codes: dict[HTTPStatus, tuple[bool, str]],
    ) -> None:
        """Raise a :class:`STUnexpectedResponseError` if parsing an unrecognized status code."""
        status_code = HTTPStatus.UNAUTHORIZED

        _ = requests_mock.get("https://api.example.com", status_code=status_code)
        res = requests.get("https://api.example.com")

        with pytest.raises(
            STFailedAuthenticationError,
            match=re.escape(f"Authentication failed or not provided (Status Code {status_code})"),
        ):
            _ = st._handle_status_codes(res, known_status_codes)

    def test_handle_status_codes_unrecognized(
        self,
        st: SolidarityTech,
        requests_mock: Mocker,
        known_status_codes: dict[HTTPStatus, tuple[bool, str]],
    ) -> None:
        """Raise a :class:`STUnexpectedResponseError` if parsing an unrecognized status code."""
        status_code = HTTPStatus.INTERNAL_SERVER_ERROR

        _ = requests_mock.get("https://api.example.com", status_code=status_code)
        res = requests.get("https://api.example.com")

        with pytest.raises(
            STUnexpectedResponseError,
            match=re.escape(f"Unexpected Response (Status Code {status_code})"),
        ):
            _ = st._handle_status_codes(res, known_status_codes)
