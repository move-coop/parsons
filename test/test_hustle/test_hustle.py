import unittest
import requests_mock
from test.utils import assert_matching_tables
from test.hustle import json_responses
from parsons import Table, Hustle

CLIENT_ID = 'FAKE_ID'
CLIENT_SECRET = 'FAKE_SECRET'


class TestHustle(unittest.TestCase):

    @requests_mock.Mocker()
    def setUp(self, m):

        m.post(self.hustle.uri + 'oauth/token', json=json_responses.auth_token)
        self.hustle = Hustle(CLIENT_ID, CLIENT_SECRET)

    def test_auth_token(self, m):

        self.assertEqual(self.hustle.auth_token, json_responses.auth_token['auth_token'])

    @requests_mock.Mocker()
    def test_create_lead(self, m):

        m.post(self.hustle.uri + 'groups/1/leads', json=expected_posts)
        self.assertEqual(self.hustle.create_lead(), create_lead)
