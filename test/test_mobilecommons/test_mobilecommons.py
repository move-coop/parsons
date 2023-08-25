import unittest
import os
import requests_mock
from parsons.mobilecommons import MobileCommons
from parsons.etl import Table
from test.utils import assert_matching_tables
from mobilecommons_responses import (get_profiles_response, get_broadcasts_response,
                                     post_profile_response)
# from airtable_responses import insert_response, insert_responses

MOBILECOMMONS_USERNAME = 'MOBILECOMMONS_USERNAME'
MOBILECOMMONS_PASSWORD = 'MOBILECOMMONS_PASSWORD'

class TestMobileCommons(unittest.TestCase):

    @requests_mock.Mocker()
    def setUp(self, m):
        self.base_uri = f'https://secure.mcommons.com/api/'

        self.mc = MobileCommons(username=MOBILECOMMONS_USERNAME, password=MOBILECOMMONS_PASSWORD)

    # @requests_mock.Mocker()
    # def test_check_response_status_code(self, m):
    #     m.get(self.base_uri + 'profiles', status_code=400, text='There was a 400 error, oh no!')
    #     error = self.check_response_status_code()
    #     self.assertEqual(error, 'There was a 400 error, oh no!')

    def test_parse_get_response(self, m):
        m.get(self.base_uri + 'profiles', status_code=get_profiles_response.status_code,
              text=get_profiles_response.text)
        parsed_get_response_text = self.mc.parse_get_request()
        self.assertIsInstance(parsed_get_response_text, dict)

    def test_mc_get_request(self, m):
        m.get(self.base_uri + 'profiles', status_code=get_profiles_response.status_code,
              text=get_profiles_response.text)
        parsed_get_response_text = self.mc.mc_get_request()
        self.assertIsInstance(parsed_get_response_text, Table, 'MobileCommons.mc_get_request'
                                                               'does output parsons table')

    @requests_mock.Mocker()
    def test_get_profiles(self, m):
        m.get(self.base_uri + 'profiles', status_code=get_profiles_response.status_code,
              text=get_profiles_response.text)
        profiles = self.mc.get_profiles()
        self.assertIsInstance(profiles, Table, 'MobileCommons.get_profiles method did not '
                                               'return a parsons Table')
        self.assertEqual(profiles[0]['first_name'], 'James',
                         'MobileCommons.get_profiles method not returning a table structured'
                         'as expected')

    @requests_mock.mocker()
    def test_get_broadcasts(self,  m):
        m.get(self.base_uri + 'broadcasts', status_code=get_broadcasts_response.status_code,
              text=get_broadcasts_response.text)
        broadcasts = self.mc.get_broadcasts()
        self.assertIsInstance(broadcasts, Table, 'MobileCommons.get_broadcasts method did not '
                                               'return a parsons Table')
        self.assertEqual(broadcasts[0]['id'], '2549409',
                         'MobileCommons.get_broadcasts method not returning a table structured'
                         'as expected')

    @requests_mock.mocker()
    def test_mc_post_request(self, m):
        m.post(self.base_uri + 'profile_update', text=post_profile_response.text)
        response_dict = self.mc_post_request()
        self.assertIsInstance(response_dict, dict, 'MobileCommons.mc_post_request output '
                                                   'not expected type dictionary')
        self.assertIsEqual(response_dict['profile']['id'], '602169563',
                           'MobileCommons.mc_post_request output value not expected')

    @requests_mock.mocker()
    def test_create_profile(self, m):
        m.post(self.base_uri + 'profile_update', text=post_profile_response.text)
        profile_id = self.create_profile()
        self.assertIsEqual(profile_id, '602169563', 'MobileCommons.create_profile does not return '
                                                    'expected profile_id')
