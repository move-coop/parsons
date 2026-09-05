import pyrate_limiter
import pytest
import requests
import requests_ratelimiter
from requests.auth import HTTPBasicAuth
from requests.structures import CaseInsensitiveDict
from requests_mock import Mocker

from parsons.utilities.api_connector import APIConnector

EXAMPLE_URL = "https://api.example.com"
EXAMPLE_ENDPOINT = f"{EXAMPLE_URL}/test-endpoint"


@pytest.fixture
def connector() -> APIConnector:
    """Fixture that provides an APIConnector instance with a base URL and headers."""
    return APIConnector(
        uri="https://api.example.com/v1", headers={"content-type": "application/json"}
    )


def test_init_adds_headers(connector: APIConnector, requests_mock: Mocker) -> None:
    """Test that base headers are added to the session during initialization."""
    requests_mock.get(
        "https://api.example.com/v1/data", json={"status": "authorized"}, status_code=200
    )

    connector.request("data", "GET")

    req = requests_mock.last_request
    assert req is not None
    assert req.headers["content-type"] == "application/json"


def test_request_with_additional_headers(connector: APIConnector, requests_mock: Mocker) -> None:
    """Test that additional headers and base headers are included in a request."""
    requests_mock.get(
        "https://api.example.com/v1/data", json={"status": "authorized"}, status_code=200
    )

    connector.request(
        "data",
        "GET",
        additional_headers={"Authorization": "Bearer token123", "X-Custom-Header": "value"},
    )

    req = requests_mock.last_request
    assert req is not None
    assert req.headers["content-type"] == "application/json"
    assert req.headers["Authorization"] == "Bearer token123"
    assert req.headers["X-Custom-Header"] == "value"


def test_init_loads_headers() -> None:
    """Test that providing headers sets the base headers on the session."""
    headers = CaseInsensitiveDict({"authorization": "Bearer cz8on37ogn37vn9wg3n7gy29"})
    conn = APIConnector(uri=EXAMPLE_URL, headers=headers)
    assert conn.session.headers == headers


def test_property_loads_headers() -> None:
    """Test that providing headers via deprecated property sets the base headers on the session."""
    headers = CaseInsensitiveDict({"authorization": "Bearer n8hn9e4hme4h4"})
    conn = APIConnector(uri=EXAMPLE_URL)
    conn.headers = headers
    assert conn.session.headers == headers


def test_init_loads_auth() -> None:
    """Test that providing auth object sets the auth on the session."""
    auth = HTTPBasicAuth("user_name", "user_pass")
    conn = APIConnector(uri=EXAMPLE_URL, auth=auth)
    assert conn.session.auth == auth


def test_property_loads_auth() -> None:
    """Test that providing auth via deprecated property sets the base auth on the session."""
    auth = HTTPBasicAuth("user_name2", "user_pass2")
    conn = APIConnector(uri=EXAMPLE_URL)
    conn.auth = auth
    assert conn.session.auth == auth


def test_init_accepts_ratelimit_as_limiter() -> None:
    """Test that providing a :class:`requests_ratelimiter.Limiter` ratelimit creates a properly-configured :class:`requests_ratelimiter.LimiterSession`."""
    rate = pyrate_limiter.Rate(1, pyrate_limiter.Duration.MINUTE)
    limiter = pyrate_limiter.Limiter(rate)
    conn = APIConnector(uri=EXAMPLE_URL, ratelimit=limiter)
    assert isinstance(conn.session, requests_ratelimiter.LimiterSession)
    assert conn.session.limiter == limiter


def test_init_accepts_ratelimit_as_rate() -> None:
    """Test that providing a :class:`requests_ratelimiter.Rate` ratelimit creates a properly-configured :class:`requests_ratelimiter.LimiterSession`."""
    rate = pyrate_limiter.Rate(1, pyrate_limiter.Duration.MINUTE)
    conn = APIConnector(uri=EXAMPLE_URL, ratelimit=rate)
    assert isinstance(conn.session, requests_ratelimiter.LimiterSession)
    assert conn.session.limiter.buckets()[0]._rates[0] == rate


def test_init_accepts_ratelimit_as_int() -> None:
    """Test that providing an integer ratelimit creates a properly-configured :class:`requests_ratelimiter.LimiterSession`."""
    rate_limit = 60
    conn = APIConnector(uri=EXAMPLE_URL, ratelimit=rate_limit)
    assert isinstance(conn.session, requests_ratelimiter.LimiterSession)
    assert isinstance(conn.session.limiter, pyrate_limiter.Limiter)
    assert str(conn.session.limiter.buckets()[0]._rates[0]) == str(
        pyrate_limiter.Rate(rate_limit, pyrate_limiter.Duration.SECOND)
    )


def test_init_accepts_session() -> None:
    """Test that providing a session overrides the default session."""
    session = requests.Session()
    conn = APIConnector(uri=EXAMPLE_URL, session=session)
    assert isinstance(conn.session, requests.Session)
    assert conn.session == session


def test_init_does_not_accept_ratelimiter_and_session() -> None:
    """Test that providing both a ratelimit and a session raises a ValueError."""
    rate = pyrate_limiter.Rate(1, pyrate_limiter.Duration.MINUTE)
    limiter = pyrate_limiter.Limiter(rate)
    session = requests.Session()
    with pytest.raises(ValueError, match="session and ratelimit cannot both be provided"):
        APIConnector(uri=EXAMPLE_URL, ratelimit=limiter, session=session)


def test_init_creates_regular_session() -> None:
    """Test that the default session is a regular (non-limited) requests session."""
    conn = APIConnector(uri=EXAMPLE_URL)
    assert isinstance(conn.session, requests.Session)
    assert not isinstance(conn.session, requests_ratelimiter.LimiterSession)
