"""Tests for the Auth0 connector.

Auth0 calls ``requests`` directly, so tests mock the HTTP boundary with the
``requests_mock`` fixture (see docs/write_tests.rst).
"""

import gzip
import json

from parsons import Table
from test.conftest import assert_matching_tables
from test.test_auth0.conftest import BASE_URL

FAKE_USER = {
    "email": "fakeemail@fakedomain.com",
    "given_name": "Fakey",
    "family_name": "McFakerson",
    "username": "fakeusername",
    "user_id": 3,
}


def test_delete_user(auth0, requests_mock):
    requests_mock.delete(f"{BASE_URL}/api/v2/users/1", status_code=204)

    assert auth0.delete_user(1) == 204


def test_get_users_by_email(auth0, requests_mock):
    mock_users = [{"email": "fake3mail@fakedomain.com", "id": 2}]
    requests_mock.get(f"{BASE_URL}/api/v2/users-by-email", json=mock_users)

    assert_matching_tables(
        auth0.get_users_by_email("fakeemail@fakedomain.com"), Table(mock_users), ignore_headers=True
    )


def test_retrieve_all_users(auth0, requests_mock):
    mock_users = [{"email": "fake3mail@fakedomain.com", "id": 2}]
    fake_job_id = 1234567
    download_url = f"{BASE_URL}/test.json.gz"

    requests_mock.get(
        f"{BASE_URL}/api/v2/connections",
        json=[{"id": 1234, "name": "Username-Password-Authentication"}],
    )
    requests_mock.post(f"{BASE_URL}/api/v2/jobs/users-exports", json={"id": fake_job_id})
    requests_mock.get(
        f"{BASE_URL}/api/v2/jobs/{fake_job_id}",
        json={"status": "completed", "location": download_url},
    )
    requests_mock.get(download_url, content=gzip.compress(json.dumps(mock_users).encode("utf-8")))

    assert_matching_tables(auth0.retrieve_all_users(), Table(mock_users), ignore_headers=True)


def test_upsert_user(auth0, requests_mock):
    requests_mock.get(f"{BASE_URL}/api/v2/users-by-email", json=[FAKE_USER])
    requests_mock.patch(f"{BASE_URL}/api/v2/users/{FAKE_USER['user_id']}", status_code=200, json={})

    ret = auth0.upsert_user(
        FAKE_USER["email"],
        FAKE_USER["username"],
        FAKE_USER["given_name"],
        FAKE_USER["family_name"],
        {},
        {},
    )

    assert ret.status_code == 200


def test_block_user(auth0, requests_mock):
    requests_mock.patch(f"{BASE_URL}/api/v2/users/{FAKE_USER['user_id']}", status_code=200, json={})

    ret = auth0.block_user(FAKE_USER["user_id"])

    assert ret.status_code == 200
