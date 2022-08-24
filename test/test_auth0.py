from parsons import Auth0, Table
from test.utils import assert_matching_tables
import requests_mock
import unittest

CLIENT_ID = 'abc'
CLIENT_SECRET = 'def'
DOMAIN = 'fakedomain.auth0.com'


class TestAuth0(unittest.TestCase):
    def setUp(self):
        self.auth0 = Auth0(CLIENT_ID, CLIENT_SECRET, DOMAIN)

    @requests_mock.Mocker()
    def test_delete_user(self, m):
        user_id = 1
        m.delete(f'{self.auth0.base_url}/api/v2/users/{user_id}', status_code=204)
        self.assertEqual(self.auth0.delete_user(user_id), 204)

    @requests_mock.Mocker()
    def test_get_users_by_email(self, m):
        email = 'fakeemail@fakedomain.com'
        mock_users = [{'email': 'fake3mail@fakedomain.com', 'id': 2}]
        m.get(f'{self.auth0.base_url}/api/v2/users-by-email?email={email}', json=mock_users)
        assert_matching_tables(self.auth0.get_users_by_email(email), Table(mock_users), True)
