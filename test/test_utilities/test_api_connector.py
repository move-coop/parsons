import pyrate_limiter
import requests
import requests_ratelimiter
from requests.structures import CaseInsensitiveDict

from parsons.utilities.api_connector import APIConnector

EXAMPLE_URL = "https://api.example.com"
EXAMPLE_ENDPOINT = f"{EXAMPLE_URL}/test-endpoint"


def test_init_accepts_ratelimiter() -> None:
    rate = pyrate_limiter.Rate(1, pyrate_limiter.Duration.MINUTE)
    limiter = pyrate_limiter.Limiter(rate)
    conn = APIConnector(uri=EXAMPLE_URL, ratelimiter=limiter)
    assert isinstance(conn.session, requests_ratelimiter.LimiterSession)
    assert conn.session.limiter == limiter


def test_init_accepts_session() -> None:
    session = requests.Session()
    session.headers = CaseInsensitiveDict({"testing_header": "parsonstestheadervalue"})
    conn = APIConnector(uri=EXAMPLE_URL, session=session)
    assert isinstance(conn.session, requests.Session)
    assert conn.session == session
    assert conn.session.headers == session.headers


def test_init_creates_regular_session() -> None:
    conn = APIConnector(uri=EXAMPLE_URL)
    assert isinstance(conn.session, requests.Session)
    assert not isinstance(conn.session, requests_ratelimiter.LimiterSession)
