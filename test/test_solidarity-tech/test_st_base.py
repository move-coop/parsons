import re

import pytest
import requests
from requests_mock import Mocker

from parsons import SolidarityTech
from parsons.solidarity_tech.exceptions import STFailedResponseError, STUnexpectedResponseError


@pytest.fixture
def known_status_codes() -> dict[int, tuple[bool, str]]:
    return {
        200: (True, "OK"),
        201: (True, "updated resource"),
        404: (False, "could not find resource"),
        422: (False, "could not process request"),
    }


@pytest.mark.parametrize(
    ("key", "value", "expected"),
    [
        ("test_key1", "test_value", {"test_key1": "test_value"}),
        ("test_key2", 123456, {"test_key2": 123456}),
        ("test_key_none", None, {}),
    ],
)
def test_get_resources(
    st: SolidarityTech,
    key: str,
    value: str | int | None,
    expected: dict[str, str | int],
) -> None:
    init_dict = {}
    result = st._add_if_field_not_empty(init_dict, key, value)
    assert result == expected


def test_get_resources_overwrite(st: SolidarityTech) -> None:
    init_dict = {"test_key": "original_value"}
    result = st._add_if_field_not_empty(init_dict, "test_key", "overwrite_value", overwrite=True)
    assert result["test_key"] == "overwrite_value"


def test_get_resources_no_overwrite_default(st: SolidarityTech) -> None:
    init_dict = {"test_key": "original_value"}
    with pytest.raises(KeyError, match="'test_key' already exists"):
        st._add_if_field_not_empty(init_dict, "test_key", "overwrite_value")


def test_get_resources_no_overwrite(st: SolidarityTech) -> None:
    init_dict = {"test_key": "original_value"}
    with pytest.raises(KeyError, match="'test_key' already exists"):
        st._add_if_field_not_empty(init_dict, "test_key", "overwrite_value", overwrite=False)


@pytest.mark.parametrize(
    "status_code",
    [200, 201, 404, 422],
)
def test_handle_status_codes(
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
        err_msg = re.escape(f"Request Failed (Status Code {status_code}) -- {failure_description}")
        with pytest.raises(STFailedResponseError, match=err_msg):
            st._handle_status_codes(res, known_status_codes)


def test_handle_status_codes_unrecognized(
    st: SolidarityTech, requests_mock: Mocker, known_status_codes: dict[int, tuple[bool, str]]
) -> None:
    status_code = 500

    requests_mock.get("https://api.example.com", status_code=status_code)
    res = requests.get("https://api.example.com")

    with pytest.raises(
        STUnexpectedResponseError,
        match=re.escape(f"Unexpected Response (Status Code {status_code})"),
    ):
        st._handle_status_codes(res, known_status_codes)
