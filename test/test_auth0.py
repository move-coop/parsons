import gzip
import json
import unittest
import unittest.mock
from test.utils import assert_matching_tables

import requests_mock
from parsons import Auth0, Table

CLIENT_ID = "abc"
CLIENT_SECRET = "def"
DOMAIN = "fakedomain.auth0.com"


class TestAuth0(unittest.TestCase):
    def setUp(self):
        self.auth0 = Auth0(CLIENT_ID, CLIENT_SECRET, DOMAIN)
        self.fake_upsert_person = {
            "email": "fakeemail@fakedomain.com",
            "given_name": "Fakey",
            "family_name": "McFakerson",
            "username": "fakeusername",
            "user_id": 3,
        }

    @requests_mock.Mocker()
    def test_delete_user(self, m):
        user_id = 1
        m.delete(f"{self.auth0.base_url}/api/v2/users/{user_id}", status_code=204)
        self.assertEqual(self.auth0.delete_user(user_id), 204)

    @requests_mock.Mocker()
    def test_get_users_by_email(self, m):
        email = "fakeemail@fakedomain.com"
        mock_users = [{"email": "fake3mail@fakedomain.com", "id": 2}]
        m.get(
            f"{self.auth0.base_url}/api/v2/users-by-email?email={email}",
            json=mock_users,
        )
        assert_matching_tables(self.auth0.get_users_by_email(email), Table(mock_users), True)

    @requests_mock.Mocker()
    def test_retrieve_all_users(self, m):
        mock_users = [{"email": "fake3mail@fakedomain.com", "id": 2}]

        fake_job_id = 1234567
        m.post(
            f"{self.auth0.base_url}/api/v2/jobs/users-exports",
            json={"id": fake_job_id},
        )
        test_url = f"{self.auth0.base_url}/test.json.gz"
        m.get(
            f"{self.auth0.base_url}/api/v2/jobs/{fake_job_id}",
            json={
                "status": "completed",
                "location": test_url,
            },
        )
        m.get(
            test_url,
            content=gzip.compress(bytes(json.dumps(mock_users), encoding="utf-8")),
        )

        connections = [{"id": 1234, "name": "Username-Password-Authentication"}]
        m.get(f"{self.auth0.base_url}/api/v2/connections", json=connections)
        data = self.auth0.retrieve_all_users()
        print(data)

        assert_matching_tables(self.auth0.retrieve_all_users(), Table(mock_users), True)

    @requests_mock.Mocker()
    def test_upsert_user(self, m):
        user = self.fake_upsert_person
        email = user["email"]
        m.get(
            f"{self.auth0.base_url}/api/v2/users-by-email?email={email}",
            json=[user],
        )
        mock_resp = unittest.mock.MagicMock()
        mock_resp.status_code = 200
        m.patch(f"{self.auth0.base_url}/api/v2/users/{user['user_id']}", [mock_resp])
        m.post(f"{self.auth0.base_url}/api/v2/users", mock_resp)
        ret = self.auth0.upsert_user(
            email,
            user["username"],
            user["given_name"],
            user["family_name"],
            {},
            {},
        )
        self.assertEqual(ret.status_code, 200)

    @requests_mock.Mocker()
    def test_block_user(self, m):
        user = self.fake_upsert_person
        user["blocked"] = True
        mock_resp = unittest.mock.MagicMock()
        mock_resp.status_code = 200
        m.patch(f"{self.auth0.base_url}/api/v2/users/{user['user_id']}", [mock_resp])
        ret = self.auth0.block_user(user["user_id"])
        self.assertEqual(ret.status_code, 200)
