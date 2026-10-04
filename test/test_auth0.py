import gzip
import json
from http import HTTPStatus

import pytest
from pytest_mock import MockerFixture
from requests_mock import Mocker

from parsons import Auth0, Table
from test.conftest import assert_matching_tables

CLIENT_ID = "abc"
CLIENT_SECRET = "def"
DOMAIN = "fakedomain.auth0.com"
ACCESS_TOKEN = "fake_token"


@pytest.fixture
def auth0_client(requests_mock: Mocker) -> Auth0:
    requests_mock.post(f"https://{DOMAIN}/oauth/token", json={"access_token": ACCESS_TOKEN})
    auth0 = Auth0(CLIENT_ID, CLIENT_SECRET, DOMAIN)
    requests_mock.reset_mock()
    return auth0


@pytest.fixture
def fake_upsert_person() -> dict[str, str | int]:
    return {
        "email": "fakeemail@fakedomain.com",
        "given_name": "Fakey",
        "family_name": "McFakerson",
        "username": "fakeusername",
        "user_id": 3,
    }


def test_delete_user(auth0_client: Auth0, requests_mock: Mocker) -> None:
    user_id = 1
    status_code = HTTPStatus.NO_CONTENT
    requests_mock.delete(f"{auth0_client.base_url}/api/v2/users/{user_id}", status_code=status_code)

    # Validate status code is returned
    assert auth0_client.delete_user(user_id) == status_code

    assert requests_mock.last_request is not None
    assert "Authorization" in requests_mock.last_request.headers
    assert requests_mock.last_request.headers["Authorization"] == f"Bearer {ACCESS_TOKEN}"


def test_get_users_by_email(auth0_client: Auth0, requests_mock: Mocker) -> None:
    email = "fakeemail@fakedomain.com"
    mock_users = [{"email": "fake3mail@fakedomain.com", "id": 2}]
    request_url = f"{auth0_client.base_url}/api/v2/users-by-email?email={email}"
    requests_mock.get(request_url, json=mock_users)

    assert_matching_tables(
        auth0_client.get_users_by_email(email), Table(mock_users), ignore_headers=True
    )

    assert requests_mock.last_request is not None
    assert "Authorization" in requests_mock.last_request.headers
    assert requests_mock.last_request.headers["Authorization"] == f"Bearer {ACCESS_TOKEN}"


def test_retrieve_all_users(auth0_client: Auth0, requests_mock: Mocker) -> None:
    connections_json = [{"id": 1234, "name": "Username-Password-Authentication"}]
    requests_mock.get(f"{auth0_client.base_url}/api/v2/connections", json=connections_json)

    start_json = {"id": 1234567}
    requests_mock.post(f"{auth0_client.base_url}/api/v2/jobs/users-exports", json=start_json)

    test_url = f"{auth0_client.base_url}/test.json.gz"
    jobs_json = {"status": "completed", "location": test_url}
    # Queue status check twice
    requests_mock.get(f"{auth0_client.base_url}/api/v2/jobs/{start_json['id']}", json=jobs_json)

    mock_users = [{"email": "fake3mail@fakedomain.com", "id": 2}]
    compressed_users = gzip.compress(bytes(json.dumps(mock_users), encoding="utf-8"))
    requests_mock.get(test_url, content=compressed_users)

    assert_matching_tables(
        auth0_client.retrieve_all_users(), Table(mock_users), ignore_headers=True
    )

    history = requests_mock.request_history
    assert [(req.method, req.url) for req in history] == [
        ("GET", f"{auth0_client.base_url}/api/v2/connections"),  # Retrieve auth0 connection id
        ("POST", f"{auth0_client.base_url}/api/v2/jobs/users-exports"),  # Start user export
        ("GET", f"{auth0_client.base_url}/api/v2/jobs/{start_json['id']}"),  # Check export status
        ("GET", test_url),  # Download user export
    ]

    # Validate authentication header on internal API requests (all except final export download)
    for request in history[:-1]:
        assert request.headers.get("Authorization") == f"Bearer {ACCESS_TOKEN}"


def test_upsert_user(
    auth0_client: Auth0,
    fake_upsert_person: dict[str, str | int],
    requests_mock: Mocker,
    mocker: MockerFixture,
) -> None:
    user = fake_upsert_person
    email = user["email"]
    requests_mock.get(f"{auth0_client.base_url}/api/v2/users-by-email?email={email}", json=[user])
    mock_resp = mocker.MagicMock()
    mock_resp.status_code = HTTPStatus.OK
    requests_mock.patch(f"{auth0_client.base_url}/api/v2/users/{user['user_id']}", [mock_resp])
    requests_mock.post(f"{auth0_client.base_url}/api/v2/users", mock_resp)

    ret = auth0_client.upsert_user(
        email,
        user["username"],
        user["given_name"],
        user["family_name"],
        {},
        {},
    )
    assert ret.status_code == HTTPStatus.OK

    assert requests_mock.last_request is not None
    assert "Authorization" in requests_mock.last_request.headers
    assert requests_mock.last_request.headers["Authorization"] == f"Bearer {ACCESS_TOKEN}"


def test_block_user(
    auth0_client: Auth0,
    fake_upsert_person: dict[str, str | int],
    requests_mock: Mocker,
    mocker: MockerFixture,
) -> None:
    user = fake_upsert_person
    user["blocked"] = True
    mock_resp = mocker.MagicMock()
    mock_resp.status_code = HTTPStatus.OK
    requests_mock.patch(f"{auth0_client.base_url}/api/v2/users/{user['user_id']}", [mock_resp])

    ret = auth0_client.block_user(user["user_id"])
    assert ret.status_code == HTTPStatus.OK

    assert requests_mock.last_request is not None
    assert "Authorization" in requests_mock.last_request.headers
    assert requests_mock.last_request.headers["Authorization"] == f"Bearer {ACCESS_TOKEN}"
