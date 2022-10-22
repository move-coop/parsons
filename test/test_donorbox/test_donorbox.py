import unittest
import requests_mock
from unittest.mock import MagicMock

from parsons import Table, Donorbox
from parsons.donorbox.donorbox import URI
from test.utils import mark_live_test
from test.test_donorbox import donorbox_fake_data


# NOTE: Donorbox does not provide free sandbox accounts to developers, and it may not be worth the monthly 
# fee to enable the live tests. I will keep the live tests commented out for now.

# TODO: 
# - add tests for get_donors
# - add tests for get_plans
# - check the date_from and date_to weirdness again, possibly with curl
# - there's no real way to mock the date_from and date_to formatting stuff, but maybe actually add in a helper
#   that emits a warning when the date_from and date_to are incorrect formats?
# - handle pagination?
# - maybe find a way to quickly test some of the other parameters in the endpoints with lots of options like
#   get_donations?
# docs (plus update the contributor guide)
# comment out the live tests
# submit


class TestDonorbox(unittest.TestCase):

    def setUp(self):
        self.base_uri = URI
        self.email = "shauna.gordon-mckeon@trestle.us"
        self.api_key = "XNUmE2eoTLlHLJSA5WF0hQT92-cbsEU_X-bBdhsqjVLd49qPoPS5pg"
        self.donorbox = Donorbox(self.email, self.api_key)

    @requests_mock.Mocker()
    def test_get_campaigns(self, m):

        m.get(self.base_uri + '/campaigns', json=donorbox_fake_data.get_campaigns_response_json)
        result = self.donorbox.get_campaigns()

        # Assert the method returns expected dict response
        self.assertDictEqual(result.to_dicts()[0], donorbox_fake_data.get_campaigns_response_json[0])
        columns = [
            'id', 'name', 'slug', 'currency', 'created_at', 'updated_at', 
            'goal_amt', 'formatted_goal_amount', 'total_raised', 
            'formatted_total_raised', 'donations_count'
        ]
        self.assertCountEqual(result.columns, columns)

    @mark_live_test
    def test_get_campaigns_live_test(self):
        result = self.donorbox.get_campaigns()
        self.assertIsInstance(result, Table)
        columns = [
            'id', 'name', 'slug', 'currency', 'created_at', 'updated_at', 
            'goal_amt', 'formatted_goal_amount', 'total_raised', 
            'formatted_total_raised', 'donations_count'
        ]
        self.assertEquals(result.columns, columns)

    @requests_mock.Mocker()
    def test_get_campaigns_with_id_filter(self, m):
        m.get(self.base_uri + '/campaigns', json=donorbox_fake_data.get_campaigns_filtered_response_json)
        result = self.donorbox.get_campaigns(id=366590)
        self.assertIsInstance(result, Table)
        self.assertEqual(result.num_rows, 1)
        self.assertEqual(result.to_dicts()[0]["id"], 366590)
        self.assertEqual(result.to_dicts()[0]["name"], "Membership Campaign")

    @mark_live_test
    def test_get_campaigns_with_id_filter_live_test(self):
        result = self.donorbox.get_campaigns(id=366590)
        self.assertIsInstance(result, Table)
        self.assertEqual(result.num_rows, 1)
        self.assertEqual(result.to_dicts()[0]["id"], 366590)
        self.assertEqual(result.to_dicts()[0]["name"], "Membership Campaign")

    @requests_mock.Mocker()
    def test_get_campaigns_with_name_filter(self, m):
        m.get(self.base_uri + '/campaigns', json=donorbox_fake_data.get_campaigns_filtered_response_json)
        result = self.donorbox.get_campaigns(name="Membership Campaign")
        self.assertIsInstance(result, Table)
        self.assertEqual(result.num_rows, 1)
        self.assertEqual(result.to_dicts()[0]["id"], 366590)
        self.assertEqual(result.to_dicts()[0]["name"], "Membership Campaign")

    @mark_live_test
    def test_get_campaigns_with_name_filter_live_test(self):
        result = self.donorbox.get_campaigns(name="Membership Campaign")
        self.assertIsInstance(result, Table)
        self.assertEqual(result.num_rows, 1)
        self.assertEqual(result.to_dicts()[0]["id"], 366590)
        self.assertEqual(result.to_dicts()[0]["name"], "Membership Campaign")

    @requests_mock.Mocker()
    def test_get_campaigns_with_order_filter(self, m):

        m.get(self.base_uri + '/campaigns', json=donorbox_fake_data.get_campaigns_desc_order)
        result = self.donorbox.get_campaigns(order="desc")
        self.assertEqual(result["id"], [366590, 366172])

        m.get(self.base_uri + '/campaigns', json=donorbox_fake_data.get_campaigns_asc_order)
        result = self.donorbox.get_campaigns(order="asc")
        self.assertEqual(result["id"], [366172, 366590])

    @mark_live_test
    def test_get_campaigns_with_order_filter_live_test(self):
        # check order of the ids without looking at IDs. or maybe look at updated/created date
        result = self.donorbox.get_campaigns()
        self.assertEqual(result["id"], [366590, 366172])
        result = self.donorbox.get_campaigns(order="desc")
        self.assertEqual(result["id"], [366590, 366172])
        result = self.donorbox.get_campaigns(order="asc")
        self.assertEqual(result["id"], [366172, 366590])

    @requests_mock.Mocker()
    def test_get_donations(self, m):

        m.get(self.base_uri + '/donations', json=donorbox_fake_data.get_donations_response_json)
        result = self.donorbox.get_donations()

        # Assert the method returns expected dict response
        self.assertDictEqual(result.to_dicts()[0], donorbox_fake_data.get_donations_response_json[0])
        columns = [
            'campaign', 'donor', 'amount', 'formatted_amount', 'converted_amount', 'formatted_converted_amount', 
            'converted_net_amount', 'formatted_converted_net_amount', 'recurring', 'first_recurring_donation', 
            'amount_refunded', 'formatted_amount_refunded', 'stripe_charge_id', 'id', 'status', 'donation_type', 
            'donation_date', 'anonymous_donation', 'gift_aid', 'designation', 'join_mailing_list', 'comment', 
            'donating_company', 'currency', 'converted_currency', 'utm_campaign', 'utm_source', 'utm_medium', 
            'utm_term', 'utm_content', 'processing_fee', 'formatted_processing_fee', 'fee_covered', 'questions', 
            'plan_id', 'interval'
        ]
        self.assertCountEqual(result.columns, columns)

    @mark_live_test
    def test_get_donations_live_test(self):
        result = self.donorbox.get_donations()
        self.assertIsInstance(result, Table)
        columns = [
            'campaign', 'donor', 'amount', 'formatted_amount', 'converted_amount', 'formatted_converted_amount', 
            'converted_net_amount', 'formatted_converted_net_amount', 'recurring', 'first_recurring_donation', 
            'amount_refunded', 'formatted_amount_refunded', 'stripe_charge_id', 'id', 'status', 'donation_type', 
            'donation_date', 'anonymous_donation', 'gift_aid', 'designation', 'join_mailing_list', 'comment', 
            'donating_company', 'currency', 'converted_currency', 'utm_campaign', 'utm_source', 'utm_medium', 
            'utm_term', 'utm_content', 'processing_fee', 'formatted_processing_fee', 'fee_covered', 'questions', 
            'plan_id', 'interval'
        ]
        self.assertEquals(result.columns, columns)
        self.assertEquals(result.num_rows, 3)

    @mark_live_test
    def test_get_donations_with_date_from_filter_live_test(self):
        # Correct formats (YYYY-mm-dd YYYY/mm/dd YYYYmmdd dd-mm-YYYY) successfully filter 
        result = self.donorbox.get_donations(date_from="2022-10-20")
        self.assertIsInstance(result, Table)
        self.assertEquals(result.num_rows, 1)
        self.assertEquals(result[0]["donation_date"], '2022-10-20T19:33:31.744Z')
        # Try the other three formats quickly
        for date_string in ["2022/10/20", "20221020", "20-10-2022"]:
            self.assertEquals(self.donorbox.get_donations(date_from=date_string).num_rows, 1)
        # Incorrect formats do not successfully filter
        result = self.donorbox.get_donations(date_from="10 20 2022")
        self.assertEquals(result.num_rows, 3)  

    @mark_live_test
    def test_get_donations_with_date_to_filter_live_test(self):
        # Correct formats (YYYY-mm-dd YYYY/mm/dd YYYYmmdd dd-mm-YYYY) successfully filter 
        result = self.donorbox.get_donations(date_to="2022-10-20")
        self.assertIsInstance(result, Table)
        self.assertEquals(result.num_rows, 2)
        self.assertEquals(result[0]["donation_date"], '2022-10-19T18:19:06.044Z')
        # Try the other three formats quickly
        for date_string in ["2022/10/20", "20221020", "20-10-2022"]:
            self.assertEquals(self.donorbox.get_donations(date_to=date_string).num_rows, 2)
        # Incorrect formats do not successfully filter
        # NOTE: weirdly, date_from and date_to seem to have different responses to incorrectly formatted dates
        result = self.donorbox.get_donations(date_to="10 20 2022")
        self.assertEquals(result.num_rows, 0)

    @requests_mock.Mocker()
    def test_get_donations_with_amount_min_filter(self, m):
        m.get(self.base_uri + '/donations', json=donorbox_fake_data.get_donations_amount_min_3)
        result = self.donorbox.get_donations(amount_min="3")
        self.assertEquals(result.num_rows, 3)
        m.get(self.base_uri + '/donations', json=donorbox_fake_data.get_donations_amount_min_4)
        result = self.donorbox.get_donations(amount_min="4")
        self.assertEquals(result.num_rows, 1)
        m.get(self.base_uri + '/donations', json=donorbox_fake_data.get_donations_amount_min_5)
        result = self.donorbox.get_donations(amount_min="5")
        self.assertEquals(result.num_rows, 0)

    @mark_live_test
    def test_get_donations_with_amount_min_filter_live_test(self):
        result = self.donorbox.get_donations(amount_min="3")
        self.assertEquals(result.num_rows, 3)
        result = self.donorbox.get_donations(amount_min="4")
        self.assertEquals(result.num_rows, 1)
        result = self.donorbox.get_donations(amount_min="5")
        self.assertEquals(result.num_rows, 0)

    @requests_mock.Mocker()
    def test_get_donations_with_amount_max_filter(self, m):
        m.get(self.base_uri + '/donations', json=donorbox_fake_data.get_donations_amount_max_3)
        result = self.donorbox.get_donations(amount_max="3")
        self.assertEquals(result.num_rows, 2)
        m.get(self.base_uri + '/donations', json=donorbox_fake_data.get_donations_amount_max_4)
        result = self.donorbox.get_donations(amount_max="4")
        self.assertEquals(result.num_rows, 3)
        m.get(self.base_uri + '/donations', json=donorbox_fake_data.get_donations_amount_max_2)
        result = self.donorbox.get_donations(amount_max="2")
        self.assertEquals(result.num_rows, 0)

    @mark_live_test
    def test_get_donations_with_amount_max_filter_live_test(self):
        result = self.donorbox.get_donations(amount_max="3")
        self.assertEquals(result.num_rows, 2)
        result = self.donorbox.get_donations(amount_max="4")
        self.assertEquals(result.num_rows, 3)
        result = self.donorbox.get_donations(amount_max="2")
        self.assertEquals(result.num_rows, 0)
