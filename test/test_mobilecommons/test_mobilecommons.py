import unittest
import os
import requests_mock
from parsons.mobilecommons import MobileCommons
from parsons.etl import Table
from test.utils import assert_matching_tables
# from airtable_responses import insert_response, insert_responses

MOBILECOMMONS_USERNAME = 'MOBILECOMMONS_USERNAME'
MOBILECOMMONS_PASSWORD = 'MOBILECOMMONS_PASSWORD'

class TestMobileCommons(unittest.TestCase):

    @requests_mock.Mocker()
    def setUp(self, m):
        self.base_uri = f'https://secure.mcommons.com/api/'

        self.mc = MobileCommons(username=MOBILECOMMONS_USERNAME, password=MOBILECOMMONS_PASSWORD)

    @requests_mock.Mocker()
    def test_get_records(self, m):

        m.get()