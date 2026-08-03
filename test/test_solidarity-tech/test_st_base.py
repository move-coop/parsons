import re

import pytest
import requests
from pytest_mock import MockerFixture
from requests_mock import GET, POST, Mocker

from parsons.solidarity_tech import SolidarityTech
from parsons.solidarity_tech.exceptions import STFailedResponseError, STUnexpectedResponseError


@pytest.fixture
def known_status_codes() -> dict[int, tuple[bool, str]]:
    return {
        200: (True, "OK"),
        201: (True, "updated resource"),
        404: (False, "could not find resource"),
        422: (False, "could not process request"),
    }


class Test_Post_Request:
    def test_get_single_resource_makes_request_with_payload(
        self, st: SolidarityTech, requests_mock: Mocker, mocker: MockerFixture
    ) -> None:
        payload = {"user_id": 654123}

        requests_mock.post(st.api_url)
        spy = mocker.spy(st.api, "request")

        st._post_request(st.api_url, payload=payload)
        spy.assert_called_once_with(url=st.api_url, req_type=POST, json=payload)

    def test_get_single_resource_makes_request_with_params(
        self, st: SolidarityTech, requests_mock: Mocker, mocker: MockerFixture
    ) -> None:
        params = {"automation_id": 35876}

        requests_mock.post(st.api_url)
        spy = mocker.spy(st.api, "request")

        st._post_request(st.api_url, params=params)
        spy.assert_called_once_with(url=st.api_url, req_type=POST, json=None, params=params)


class Test_Get_Single_Resource:
    def test_get_single_resource_makes_request_with_id(
        self, st: SolidarityTech, requests_mock: Mocker, mocker: MockerFixture
    ) -> None:
        id = 42
        endpoint = f"{st.api_url}/{id}"

        requests_mock.get(endpoint)
        spy = mocker.spy(st.api, "request")

        st._get_single_resource(st.api_url, id)
        spy.assert_called_once_with(url=endpoint, req_type=GET)


class Test_Get_Resources:
    def test_get_resources_makes_request(
        self, st: SolidarityTech, requests_mock: Mocker, mocker: MockerFixture
    ) -> None:
        requests_mock.get(st.api_url)
        spy = mocker.spy(st.api, "request")
        st._get_resources(st.api_url)
        spy.assert_called_once_with(url=st.api_url, req_type=GET)

    def test_get_resources_remaps_special_query_strings(
        self,
        st: SolidarityTech,
        requests_mock: Mocker,
        mocker: MockerFixture,
    ) -> None:
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
        requests_mock.get(st.api_url)
        with pytest.raises(KeyError, match="Request param '_limit' already exists"):
            st._get_resources(st.api_url, limit=15, params={"_limit": 30})


class Test_Add_If_Field_Not_Empty:
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
        init_dict = {}
        result = st._add_if_field_not_empty(init_dict, key, value)
        assert result == expected

    def test_add_if_field_not_empty_overwrite(self, st: SolidarityTech) -> None:
        init_dict = {"test_key": "original_value"}
        result = st._add_if_field_not_empty(
            init_dict, "test_key", "overwrite_value", overwrite=True
        )
        assert result["test_key"] == "overwrite_value"

    def test_add_if_field_not_empty_no_overwrite_default(self, st: SolidarityTech) -> None:
        init_dict = {"test_key": "original_value"}
        with pytest.raises(KeyError, match="'test_key' already exists"):
            st._add_if_field_not_empty(init_dict, "test_key", "overwrite_value")

    def test_add_if_field_not_empty_no_overwrite(self, st: SolidarityTech) -> None:
        init_dict = {"test_key": "original_value"}
        with pytest.raises(KeyError, match="'test_key' already exists"):
            st._add_if_field_not_empty(init_dict, "test_key", "overwrite_value", overwrite=False)


class Test_Handle_Status_Codes:
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
        status_code = 500

        requests_mock.get("https://api.example.com", status_code=status_code)
        res = requests.get("https://api.example.com")

        with pytest.raises(
            STUnexpectedResponseError,
            match=re.escape(f"Unexpected Response (Status Code {status_code})"),
        ):
            st._handle_status_codes(res, known_status_codes)
