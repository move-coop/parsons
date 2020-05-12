from parsons.mailchimp.mailchimp import Mailchimp
import unittest
import requests_mock
from test.utils import assert_matching_tables
from test.test_mailchimp import expected_json

API_KEY = 'mykey-us00'

class TestMailchimp(unittest.TestCase):

    def setUp(self):

        self.mc = Mailchimp(API_KEY)

    @requests_mock.Mocker()
    def test_get_campaigns(self, m):

    	# Test that agents are returned correctly.
        m.get(self.mc.uri + 'campaigns', json=expected_json.test_campaigns)
        tbl = self.mc.get_campaigns()

    @requests_mock.Mocker()
    def test_get_lists(self, m):

        # Test that tickets are returned correctly.
        m.get(self.mc.uri + 'lists', json=expected_json.test_ticket)
        tbl = self.mc.get_lists() 

    @requests_mock.Mocker()
    def test_get_members(self, m):

        # Test that tickets are returned correctly.
        m.get(self.mc.uri + 'companies', json=expected_json.test_company)
        tbl = self.mc.get_members() 

    @requests_mock.Mocker()
    def test_get_unsubscribes(self, m):

        # Test that tickets are returned correctly.
        m.get(self.mc.uri + 'contacts', json=expected_json.test_contact)
        tbl = self.mc.get_unsubscribes() 
