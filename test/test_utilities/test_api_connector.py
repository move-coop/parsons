import pytest
from requests_mock import Mocker

from parsons.utilities.api_connector import APIConnector


@pytest.fixture
def connector() -> APIConnector:
    return APIConnector(
        uri="https://api.example.com/v1", headers={"content-type": "application/json"}
    )


def test_init_adds_headers(connector: APIConnector, requests_mock: Mocker) -> None:
    requests_mock.get(
        "https://api.example.com/v1/data", json={"status": "authorized"}, status_code=200
    )

    connector.request("data", "GET")

    req = requests_mock.last_request
    assert req.headers["content-type"] == "application/json"


def test_request_with_additional_headers(connector: APIConnector, requests_mock) -> None:
    requests_mock.get(
        "https://api.example.com/v1/data", json={"status": "authorized"}, status_code=200
    )

    connector.request(
        "data",
        "GET",
        additional_headers={"Authorization": "Bearer token123", "X-Custom-Header": "value"},
    )

    req = requests_mock.last_request
    assert req.headers["Authorization"] == "Bearer token123"
    assert req.headers["X-Custom-Header"] == "value"


def test_request_merges_base_and_additional_headers(
    connector: APIConnector, requests_mock: Mocker
) -> None:
    requests_mock.get("https://api.example.com/v1/data", json={}, status_code=200)

    connector.request(
        "data",
        "GET",
        additional_headers={"Authorization": "Bearer token123", "X-Custom-Header": "value"},
    )

    req = requests_mock.last_request
    assert req.headers["content-type"] == "application/json"
    assert req.headers["Authorization"] == "Bearer token123"
    assert req.headers["X-Custom-Header"] == "value"
