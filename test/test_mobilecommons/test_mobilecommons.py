import unittest
import os
import requests_mock
from parsons.mobilecommons import MobileCommons
from parsons.etl import Table
from test.utils import assert_matching_tables
from mobilecommons_responses import get_profiles_response, get_broadcasts_response, \
    post_profiles_response
# from airtable_responses import insert_response, insert_responses

MOBILECOMMONS_USERNAME = 'MOBILECOMMONS_USERNAME'
MOBILECOMMONS_PASSWORD = 'MOBILECOMMONS_PASSWORD'

class TestMobileCommons(unittest.TestCase):

    @requests_mock.Mocker()
    def setUp(self, m):
        self.base_uri = f'https://secure.mcommons.com/api/'

        self.mc = MobileCommons(username=MOBILECOMMONS_USERNAME, password=MOBILECOMMONS_PASSWORD)

    @requests_mock.Mocker()
    def test_get_profiles(self, m):

        m.get(self.base_uri + 'profiles', status_code=get_profiles_response.status_code,
              text=get_profiles_response.text)
        profiles = self.mc.get_profiles()
        '''Two main things to check for - type and content of response content'''
        self.assertEqual(profiles, )