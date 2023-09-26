from parsons import Mailchimp
import unittest
import requests_mock
from test.test_mailchimp import expected_json

API_KEY = "mykey-us00"


class TestMailchimp(unittest.TestCase):
    def setUp(self):

        self.mc = Mailchimp(API_KEY)

    @requests_mock.Mocker()
    def test_get_campaigns(self, m):

        # Test that campaigns are returned correctly.
        m.get(self.mc.uri + "campaigns", json=expected_json.test_campaigns)
        tbl = self.mc.get_campaigns()

        self.assertEqual(tbl.num_rows, 2)

    @requests_mock.Mocker()
    def test_get_lists(self, m):

        # Test that lists are returned correctly.
        m.get(self.mc.uri + "lists", json=expected_json.test_lists)
        tbl = self.mc.get_lists()

        self.assertEqual(tbl.num_rows, 2)

    @requests_mock.Mocker()
    def test_get_members(self, m):

        # Test that list members are returned correctly.
        m.get(self.mc.uri + "lists/zyx/members", json=expected_json.test_members)
        tbl = self.mc.get_members(list_id="zyx")

        self.assertEqual(tbl.num_rows, 2)

    @requests_mock.Mocker()
    def test_get_unsubscribes(self, m):

        # Test that campaign unsubscribes are returned correctly.
        m.get(
            self.mc.uri + "reports/abc/unsubscribed",
            json=expected_json.test_unsubscribes,
        )
        tbl = self.mc.get_unsubscribes(campaign_id="abc")

        self.assertEqual(tbl.num_rows, 1)
