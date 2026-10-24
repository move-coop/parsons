from http import HTTPStatus

import pytest
import requests
from requests.auth import HTTPBasicAuth
from requests.structures import CaseInsensitiveDict
from requests_mock import Mocker

from parsons.utilities.api_connector import APIConnector

EXAMPLE_URL = "https://api.example.com"


@pytest.fixture
def connector() -> APIConnector:
    """Fixture that provides an APIConnector instance with a base URL and headers."""
    return APIConnector(uri=f"{EXAMPLE_URL}/v1", headers={"content-type": "application/json"})


def test_init_adds_headers(connector: APIConnector, requests_mock: Mocker) -> None:
    """Test that base headers are added to the session during initialization."""
    requests_mock.get(
        f"{EXAMPLE_URL}/v1/data", json={"status": "authorized"}, status_code=HTTPStatus.OK
    )

    connector.request("data", "GET")

    req = requests_mock.last_request
    assert req is not None
    assert req.headers["content-type"] == "application/json"


def test_request_with_additional_headers(connector: APIConnector, requests_mock: Mocker) -> None:
    """Test that additional headers and base headers are included in a request."""
    json_data = {"status": "authorized"}
    requests_mock.get(f"{EXAMPLE_URL}/v1/data", json=json_data, status_code=HTTPStatus.OK)

    additional_headers = {"Authorization": "Bearer token123", "X-Custom-Header": "value"}
    connector.request("data", "GET", additional_headers=additional_headers)

    req = requests_mock.last_request
    assert req is not None
    assert req.headers["content-type"] == "application/json"
    assert req.headers["Authorization"] == "Bearer token123"
    assert req.headers["X-Custom-Header"] == "value"


def test_get_request_with_invalid_return_format(
    connector: APIConnector, requests_mock: Mocker
) -> None:
    """Test that get_request method raises RuntimeError if `return_format` is invalid."""
    requests_mock.get(f"{EXAMPLE_URL}/v1/data")

    with pytest.raises(RuntimeError, match="not a valid format, change to json or content"):
        connector.get_request("data", return_format="invalid")  # type: ignore[ty:no-matching-overload]


@pytest.mark.parametrize("method", ["get", "post", "put", "patch", "delete"])
def test_request_raise_on_error_false(
    connector: APIConnector, requests_mock: Mocker, method: str
) -> None:
    """Test that request methods do not raise an error if request fails and `raise_on_error` is False."""
    requests_mock.request(
        method.upper(), f"{EXAMPLE_URL}/v1/data", status_code=HTTPStatus.INTERNAL_SERVER_ERROR
    )

    resp = getattr(connector, f"{method}_request")("data", raise_on_error=False)

    assert resp is None


def test_init_loads_headers() -> None:
    """Test that providing headers sets the base headers on the session."""
    headers = CaseInsensitiveDict({"authorization": "Bearer cz8on37ogn37vn9wg3n7gy29"})
    conn = APIConnector(uri=EXAMPLE_URL, headers=headers)
    assert conn.session.headers == headers


def test_init_loads_auth() -> None:
    """Test that providing auth object sets the auth on the session."""
    auth = HTTPBasicAuth("user_name", "user_pass")
    conn = APIConnector(uri=EXAMPLE_URL, auth=auth)
    assert conn.session.auth == auth


def test_init_creates_regular_session() -> None:
    """Test that the default session is a regular (non-limited) requests session."""
    conn = APIConnector(uri=EXAMPLE_URL)
    assert isinstance(conn.session, requests.Session)


def test_init_accepts_session() -> None:
    """Test that providing a session overrides the default session."""
    session = requests.Session()
    conn = APIConnector(uri=EXAMPLE_URL, session=session)
    assert isinstance(conn.session, requests.Session)
    assert conn.session == session
