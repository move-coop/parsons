import pyrate_limiter
import pytest
import requests
import requests_ratelimiter
from requests.auth import HTTPBasicAuth
from requests.structures import CaseInsensitiveDict

from parsons.utilities.api_connector import APIConnector

EXAMPLE_URL = "https://api.example.com"
EXAMPLE_ENDPOINT = f"{EXAMPLE_URL}/test-endpoint"


def test_init_loads_headers() -> None:
    headers = CaseInsensitiveDict({"authorization": "Bearer cz8on37ogn37vn9wg3n7gy29"})
    conn = APIConnector(uri=EXAMPLE_URL, headers=headers)
    assert conn.session.headers == headers

    headers = CaseInsensitiveDict({"authorization": "Bearer n8hn9e4hme4h4"})
    conn.headers = headers
    assert conn.session.headers == headers


def test_init_loads_auth() -> None:
    auth = HTTPBasicAuth("user_name", "user_pass")
    conn = APIConnector(uri=EXAMPLE_URL, auth=auth)
    assert conn.session.auth == auth

    auth = HTTPBasicAuth("user_name2", "user_pass2")
    conn.auth = auth
    assert conn.session.auth == auth


def test_init_accepts_ratelimiter() -> None:
    rate = pyrate_limiter.Rate(1, pyrate_limiter.Duration.MINUTE)
    limiter = pyrate_limiter.Limiter(rate)
    conn = APIConnector(uri=EXAMPLE_URL, ratelimiter=limiter)
    assert isinstance(conn.session, requests_ratelimiter.LimiterSession)
    assert conn.session.limiter == limiter


def test_init_accepts_session() -> None:
    session = requests.Session()
    conn = APIConnector(uri=EXAMPLE_URL, session=session)
    assert isinstance(conn.session, requests.Session)
    assert conn.session == session


def test_init_does_not_accept_ratelimiter_and_session() -> None:
    rate = pyrate_limiter.Rate(1, pyrate_limiter.Duration.MINUTE)
    limiter = pyrate_limiter.Limiter(rate)
    session = requests.Session()
    with pytest.raises(ValueError, match="session and ratelimiter cannot both be provided"):
        APIConnector(uri=EXAMPLE_URL, ratelimiter=limiter, session=session)


def test_init_creates_regular_session() -> None:
    conn = APIConnector(uri=EXAMPLE_URL)
    assert isinstance(conn.session, requests.Session)
    assert not isinstance(conn.session, requests_ratelimiter.LimiterSession)
