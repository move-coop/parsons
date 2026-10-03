"""Tests for :class:`~parsons.utilities.bearer_auth.BearerAuth`."""

from __future__ import annotations

import secrets
import warnings
from datetime import datetime, timedelta, timezone
from typing import TYPE_CHECKING

import pytest
import requests

from parsons.utilities.bearer_auth import BearerAuth, TokenTimeoutWarning

if TYPE_CHECKING:
    from collections.abc import Callable


TEST_REFRESH_DATETIME = datetime(year=2026, month=5, day=1, hour=18, minute=54, tzinfo=timezone.utc)


@pytest.fixture
def prepared_req() -> requests.PreparedRequest:
    """Fixture for creating a generic prepared request with url and header."""
    req = requests.Request(url="https://example.com", headers={"X-Test": "test"})
    return req.prepare()


@pytest.fixture
def bearer_auth() -> BearerAuth:
    """Fixture for creating a simple BearerAuth object."""
    api_token = secrets.token_hex(64)
    return BearerAuth(api_token)


@pytest.fixture
def bearer_auth_header_name() -> BearerAuth:
    """Fixture for creating a BearerAuth object with a custom header name."""
    api_token = secrets.token_hex(64)
    header_name = "Auth"
    return BearerAuth(api_token, header_name=header_name)


@pytest.fixture
def bearer_auth_token_divider() -> BearerAuth:
    """Fixture for creating a BearerAuth object with a custom token divider."""
    api_token = secrets.token_hex(64)
    token_divider = ":"
    return BearerAuth(api_token, token_divider=token_divider)


@pytest.fixture
def bearer_auth_token_name() -> BearerAuth:
    """Fixture for creating a BearerAuth object with a custom token name."""
    api_token = secrets.token_hex(64)
    token_name = "Login"
    return BearerAuth(api_token, token_name=token_name)


@pytest.fixture
def bearer_auth_expires() -> BearerAuth:
    """Fixture for creating a BearerAuth object with a non-expired token."""
    api_token = secrets.token_hex(64)
    now = datetime.now(tz=timezone.utc)
    later = now + timedelta(seconds=600)
    return BearerAuth(api_token, expires=later)


@pytest.fixture
def bearer_auth_expired() -> BearerAuth:
    """Fixture for creating a BearerAuth object with an expired token."""
    api_token = secrets.token_hex(64)
    now = datetime.now(tz=timezone.utc)
    before = now - timedelta(seconds=600)
    return BearerAuth(api_token, expires=before)


@pytest.fixture
def bearer_auth_refresh_callback() -> BearerAuth:
    """Fixture for creating a BearerAuth object with a refresh callback and an expired token."""
    api_token = secrets.token_hex(64)
    now = datetime.now(tz=timezone.utc)
    now_plus = now - timedelta(seconds=600)

    def refresh_callback() -> tuple[str, datetime]:
        return api_token, TEST_REFRESH_DATETIME

    return BearerAuth(api_token, expires=now_plus, refresh_callback=refresh_callback)


@pytest.mark.parametrize(
    ("auth_kwargs", "expected_attr", "expected_value_key"),
    [
        ({}, "api_key", "api_token"),
        ({"expires": datetime.now(tz=timezone.utc)}, "expires", "expires"),
        ({"token_name": "LoginToken"}, "token_name", "token_name"),
        ({"token_divider": ":"}, "token_divider", "token_divider"),
        ({"header_name": "AuthHeader"}, "header_name", "header_name"),
    ],
    ids=[
        "api_key only",
        "api_key with expires",
        "api_key with token_divider",
        "api_key with token_name",
        "api_key with header_name",
    ],
)
def test_auth_init_variants(auth_kwargs: dict, expected_attr: str, expected_value_key: str) -> None:
    """Test that the auth object is initialized correctly with various supplied attributes."""
    api_token = secrets.token_hex(64)

    if expected_value_key == "api_token":
        expected_value = api_token
    else:
        expected_value = auth_kwargs[expected_value_key]

    auth = BearerAuth(api_token, **auth_kwargs)

    assert getattr(auth, expected_attr) == expected_value


def test_auth_strips() -> None:
    """Test that the auth object is initialized with the supplied API key, with leading and trailing whitespace removed."""
    api_token = secrets.token_hex(64)
    auth = BearerAuth(f" {api_token} ")

    assert auth.api_key == api_token


@pytest.mark.parametrize(
    ("auth1_kwargs", "auth2_kwargs", "should_be_equal"),
    [
        ({}, {}, True),
        ({"header_name": "Auth1"}, {"header_name": "Auth1"}, True),
        ({"header_name": "Auth1"}, {"header_name": "Auth2"}, False),
        ({"token_name": "Login1"}, {"token_name": "Login1"}, True),
        ({"token_name": "Login1"}, {"token_name": "Login2"}, False),
        ({"token_divider": ":"}, {"token_divider": ":"}, True),
        ({"token_divider": ":"}, {"token_divider": " "}, False),
        (
            {"expires": (now := datetime.now(tz=timezone.utc))},
            {"expires": now},
            True,
        ),
        (
            {"expires": datetime.now(tz=timezone.utc)},
            {"expires": datetime.now(tz=timezone.utc) + timedelta(seconds=600)},
            False,
        ),
    ],
    ids=[
        "matching api_key",
        "matching header_name",
        "different header_name",
        "matching token_name",
        "different token_name",
        "matching token_divider",
        "different token_divider",
        "matching expires",
        "different expires",
    ],
)
def test_auth_eq(auth1_kwargs: dict, auth2_kwargs: dict, should_be_equal: bool) -> None:
    """Test that instances of auth objects can be compared for equality under various configurations."""
    api_token = secrets.token_hex(64)

    auth1 = BearerAuth(api_token, **auth1_kwargs)
    auth2 = BearerAuth(api_token, **auth2_kwargs)

    if should_be_equal:
        assert auth1 == auth2
    else:
        assert auth1 != auth2


def test_auth_eq_different_keys() -> None:
    """Test that auth objects with different API keys are not equal."""
    api_token1 = secrets.token_hex(64)
    api_token2 = secrets.token_hex(64)

    auth1 = BearerAuth(api_token1)
    auth2 = BearerAuth(api_token2)

    assert auth1 != auth2


@pytest.mark.parametrize(
    "fixture_name",
    [
        "bearer_auth",
        "bearer_auth_header_name",
        "bearer_auth_token_name",
        "bearer_auth_token_divider",
        "bearer_auth_expires",
        "bearer_auth_refresh_callback",
    ],
)
def test_auth_hash(fixture_name: str, request: pytest.FixtureRequest) -> None:
    """Test that auth objects are hashable based on their attributes."""
    auth_obj = request.getfixturevalue(fixture_name)
    assert hash(auth_obj) == hash(
        auth_obj.api_key
        + auth_obj.header_name
        + str(auth_obj.token_name)
        + str(auth_obj.token_divider)
        + str(auth_obj.expires)
        + str(auth_obj.refresh_callback)
    )


@pytest.mark.parametrize(
    ("fixture_name", "attribute_getter"),
    [
        ("bearer_auth", lambda a: a.api_key),
        ("bearer_auth_header_name", lambda a: str(a.header_name)),
        ("bearer_auth_token_name", lambda a: str(a.token_name)),
        ("bearer_auth_token_divider", lambda a: str(a.token_divider)),
        ("bearer_auth_expires", lambda a: str(a.expires)),
        ("bearer_auth_refresh_callback", lambda a: str(a.refresh_callback)),
    ],
    ids=[
        "api_key only",
        "api_key with header_name",
        "api_key with token_name",
        "api_key with token_divider",
        "api_key with expires",
        "api_key with refresh_callback",
    ],
)
def test_auth_repr(
    fixture_name: str,
    attribute_getter: Callable[[BearerAuth], str],
    request: pytest.FixtureRequest,
) -> None:
    """Test that auth objects include key attributes in their repr."""
    auth_obj = request.getfixturevalue(fixture_name)
    assert attribute_getter(auth_obj) in repr(auth_obj)


@pytest.mark.parametrize(
    ("fixture_name", "expected_warning", "expected_expires"),
    [
        ("bearer_auth", None, None),
        ("bearer_auth_header_name", None, None),
        ("bearer_auth_token_name", None, None),
        ("bearer_auth_token_divider", None, None),
        ("bearer_auth_expired", TokenTimeoutWarning, None),
        ("bearer_auth_expires", None, None),
        ("bearer_auth_refresh_callback", None, TEST_REFRESH_DATETIME),
    ],
)
def test_auth_call(
    fixture_name: str,
    expected_warning: type[Warning] | None,
    expected_expires: datetime | None,
    request: pytest.FixtureRequest,
    prepared_req: requests.PreparedRequest,
) -> None:
    """Test various behaviors of BearerAuth object execution."""
    bearer_auth = request.getfixturevalue(fixture_name)

    with warnings.catch_warnings(record=True) as record:
        warnings.simplefilter("always")
        bearer_auth(prepared_req)

    if expected_warning:
        matching_warnings = [w for w in record if issubclass(w.category, expected_warning)]
        assert len(matching_warnings) == 1
        expected_msg = f"API token expired at {bearer_auth.expires}. Please re-authenticate."
        assert expected_msg in str(matching_warnings[0].message)
    else:
        timeout_warnings = [w for w in record if issubclass(w.category, TokenTimeoutWarning)]
        assert len(timeout_warnings) == 0

    if expected_expires is not None:
        assert bearer_auth.expires == expected_expires

    token_value = (
        f"{bearer_auth.token_name}{bearer_auth.token_divider!s}{bearer_auth.api_key}"
        if bearer_auth.token_name
        else bearer_auth.api_key
    )
    assert prepared_req.headers[bearer_auth.header_name] == token_value
    assert prepared_req.headers["X-Test"] == "test"
