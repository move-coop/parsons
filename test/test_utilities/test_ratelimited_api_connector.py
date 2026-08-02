import pytest
from pyrate_limiter import Duration, Rate
from requests_mock import DELETE, GET, PATCH, POST, PUT, Mocker

from parsons.utilities.ratelimited_api_connector import RateLimitedAPIConnector

EXAMPLE_URL = "https://api.example.com"
EXAMPLE_ENDPOINT = f"{EXAMPLE_URL}/test-endpoint"


@pytest.fixture
def connector() -> RateLimitedAPIConnector:
    rate = Rate(1, Duration.MINUTE)
    return RateLimitedAPIConnector(EXAMPLE_URL, ratelimit=rate)


@pytest.fixture
def limiter_spy(connector: RateLimitedAPIConnector) -> list[tuple[str, bool]]:
    """Spies on connector.limiter.try_acquire and records call results."""
    calls = []
    original_try_acquire = connector.limiter.try_acquire

    def spy_try_acquire(name: str = "pyrate", *, blocking: bool = False):
        is_blocking = not original_try_acquire(name, blocking=blocking)
        calls.append((name, is_blocking))
        return is_blocking

    connector.limiter.try_acquire = spy_try_acquire  # type: ignore
    return calls


@pytest.mark.parametrize(
    ("request_type", "method_name"),
    [
        (GET, "get_request"),
        (POST, "post_request"),
        (PUT, "put_request"),
        (PATCH, "patch_request"),
        (DELETE, "delete_request"),
    ],
)
def test_methods_triggers_limiter(
    connector: RateLimitedAPIConnector,
    requests_mock: Mocker,
    limiter_spy: list[tuple[str, bool]],
    request_type: str,
    method_name: str,
):
    requests_mock.register_uri(
        method=request_type,
        url=EXAMPLE_ENDPOINT,
        json={"status": "ok"},
        status_code=200,
    )

    method = getattr(connector, method_name)
    method(EXAMPLE_ENDPOINT)

    assert limiter_spy == [("api_call", False)]


def test_rate_limiter_blocks_exceeding_calls(
    connector: RateLimitedAPIConnector,
    requests_mock: Mocker,
    limiter_spy: list[tuple[str, bool]],
):
    requests_mock.get(url=EXAMPLE_ENDPOINT, json={"data": "ok"})

    connector.request(EXAMPLE_ENDPOINT, req_type=GET)
    connector.request(EXAMPLE_ENDPOINT, req_type=GET)

    assert limiter_spy == [("api_call", False), ("api_call", True)]
