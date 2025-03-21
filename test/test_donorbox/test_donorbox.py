import unittest

import requests_mock

from parsons import Donorbox, Table
from parsons.donorbox.donorbox import URI
from test.test_donorbox import donorbox_test_data
from test.utils import mark_live_test

# NOTE: Donorbox does not provide free sandbox accounts to developers. To enable live tests,
# get a paid account and remove the @skip decorators on the live tests below.


class TestDonorbox(unittest.TestCase):
    def setUp(self):
        self.base_uri = URI
        self.donorbox = Donorbox(email="testemail@examp.org", api_key="faketestapikey")

    @requests_mock.Mocker()
    def test_get_campaigns(self, m):
        m.get(
            self.base_uri + "/campaigns",
            json=donorbox_test_data.get_campaigns_response_json,
        )
        result = self.donorbox.get_campaigns()

        # Assert the method returns expected dict response
        assert result.to_dicts()[0] == donorbox_test_data.get_campaigns_response_json[0]
        columns = [
            "id",
            "name",
            "slug",
            "currency",
            "created_at",
            "updated_at",
            "goal_amt",
            "formatted_goal_amount",
            "total_raised",
            "formatted_total_raised",
            "donations_count",
        ]
        assert len(result.columns) == len(columns)

    @unittest.skip("requires live account setup")
    @mark_live_test
    def test_get_campaigns_live_test(self):
        result = self.donorbox.get_campaigns()
        assert isinstance(result, Table)
        columns = [
            "id",
            "name",
            "slug",
            "currency",
            "created_at",
            "updated_at",
            "goal_amt",
            "formatted_goal_amount",
            "total_raised",
            "formatted_total_raised",
            "donations_count",
        ]
        assert result.columns == columns

    @requests_mock.Mocker()
    def test_get_campaigns_with_id_filter(self, m):
        m.get(
            self.base_uri + "/campaigns",
            json=donorbox_test_data.get_campaigns_filtered_response_json,
        )
        result = self.donorbox.get_campaigns(id=366590)
        assert isinstance(result, Table)
        assert result.num_rows == 1
        assert result.to_dicts()[0]["id"] == 366590
        assert result.to_dicts()[0]["name"] == "Membership Campaign"

    @unittest.skip("requires live account setup")
    @mark_live_test
    def test_get_campaigns_with_id_filter_live_test(self):
        result = self.donorbox.get_campaigns(id=366590)
        assert isinstance(result, Table)
        assert result.num_rows == 1
        assert result.to_dicts()[0]["id"] == 366590
        assert result.to_dicts()[0]["name"] == "Membership Campaign"

    @requests_mock.Mocker()
    def test_get_campaigns_with_name_filter(self, m):
        m.get(
            self.base_uri + "/campaigns",
            json=donorbox_test_data.get_campaigns_filtered_response_json,
        )
        result = self.donorbox.get_campaigns(name="Membership Campaign")
        assert isinstance(result, Table)
        assert result.num_rows == 1
        assert result.to_dicts()[0]["id"] == 366590
        assert result.to_dicts()[0]["name"] == "Membership Campaign"

    @unittest.skip("requires live account setup")
    @mark_live_test
    def test_get_campaigns_with_name_filter_live_test(self):
        result = self.donorbox.get_campaigns(name="Membership Campaign")
        assert isinstance(result, Table)
        assert result.num_rows == 1
        assert result.to_dicts()[0]["id"] == 366590
        assert result.to_dicts()[0]["name"] == "Membership Campaign"

    @requests_mock.Mocker()
    def test_get_campaigns_with_order_filter(self, m):
        m.get(
            self.base_uri + "/campaigns",
            json=donorbox_test_data.get_campaigns_desc_order,
        )
        result = self.donorbox.get_campaigns(order="desc")
        assert result["id"] == [366590, 366172]

        m.get(
            self.base_uri + "/campaigns",
            json=donorbox_test_data.get_campaigns_asc_order,
        )
        result = self.donorbox.get_campaigns(order="asc")
        assert result["id"] == [366172, 366590]

    @unittest.skip("requires live account setup")
    @mark_live_test
    def test_get_campaigns_with_order_filter_live_test(self):
        # check order of the ids without looking at IDs. or maybe look at updated/created date
        result = self.donorbox.get_campaigns()
        assert result["id"] == [366590, 366172]
        result = self.donorbox.get_campaigns(order="desc")
        assert result["id"] == [366590, 366172]
        result = self.donorbox.get_campaigns(order="asc")
        assert result["id"] == [366172, 366590]

    @requests_mock.Mocker()
    def test_get_donations(self, m):
        m.get(
            self.base_uri + "/donations",
            json=donorbox_test_data.get_donations_response_json,
        )
        result = self.donorbox.get_donations()

        # Assert the method returns expected dict response
        assert result.to_dicts()[0] == donorbox_test_data.get_donations_response_json[0]

        columns = [
            "campaign",
            "donor",
            "amount",
            "formatted_amount",
            "converted_amount",
            "formatted_converted_amount",
            "converted_net_amount",
            "formatted_converted_net_amount",
            "recurring",
            "first_recurring_donation",
            "amount_refunded",
            "formatted_amount_refunded",
            "stripe_charge_id",
            "id",
            "status",
            "donation_type",
            "donation_date",
            "anonymous_donation",
            "gift_aid",
            "designation",
            "join_mailing_list",
            "comment",
            "donating_company",
            "currency",
            "converted_currency",
            "utm_campaign",
            "utm_source",
            "utm_medium",
            "utm_term",
            "utm_content",
            "processing_fee",
            "formatted_processing_fee",
            "fee_covered",
            "questions",
            "plan_id",
            "interval",
        ]
        assert len(result.columns) == len(columns)

    @unittest.skip("requires live account setup")
    @mark_live_test
    def test_get_donations_live_test(self):
        result = self.donorbox.get_donations()
        assert isinstance(result, Table)
        columns = [
            "campaign",
            "donor",
            "amount",
            "formatted_amount",
            "converted_amount",
            "formatted_converted_amount",
            "converted_net_amount",
            "formatted_converted_net_amount",
            "recurring",
            "first_recurring_donation",
            "amount_refunded",
            "formatted_amount_refunded",
            "stripe_charge_id",
            "id",
            "status",
            "donation_type",
            "donation_date",
            "anonymous_donation",
            "gift_aid",
            "designation",
            "join_mailing_list",
            "comment",
            "donating_company",
            "currency",
            "converted_currency",
            "utm_campaign",
            "utm_source",
            "utm_medium",
            "utm_term",
            "utm_content",
            "processing_fee",
            "formatted_processing_fee",
            "fee_covered",
            "questions",
            "plan_id",
            "interval",
        ]
        assert result.columns == columns
        assert result.num_rows == 3

    @unittest.skip("requires live account setup")
    @mark_live_test
    def test_get_donations_with_date_from_filter_live_test(self):
        # Correct formats (YYYY-mm-dd YYYY/mm/dd YYYYmmdd dd-mm-YYYY) successfully filter
        result = self.donorbox.get_donations(date_from="2022-10-20")
        assert isinstance(result, Table)
        assert result.num_rows == 1
        assert result[0]["donation_date"] == "2022-10-20T19:33:31.744Z"
        # Try the other three formats quickly
        for date_string in ["2022/10/20", "20221020", "20-10-2022"]:
            assert self.donorbox.get_donations(date_from=date_string).num_rows == 1
        # Incorrect formats raise error
        with self.assertRaises(ValueError):
            result = self.donorbox.get_donations(date_from="10 20 2022")

    @unittest.skip("requires live account setup")
    @mark_live_test
    def test_get_donations_with_date_to_filter_live_test(self):
        # Correct formats (YYYY-mm-dd YYYY/mm/dd YYYYmmdd dd-mm-YYYY) successfully filter
        result = self.donorbox.get_donations(date_to="2022-10-20")
        assert isinstance(result, Table)
        assert result.num_rows == 2
        assert result[0]["donation_date"] == "2022-10-19T18:19:06.044Z"
        # Try the other three formats quickly
        for date_string in ["2022/10/20", "20221020", "20-10-2022"]:
            assert self.donorbox.get_donations(date_to=date_string).num_rows == 2
        # Incorrect formats raise error
        with self.assertRaises(ValueError):
            result = self.donorbox.get_donations(date_to="10 20 2022")

    @requests_mock.Mocker()
    def test_get_donations_with_amount_min_filter(self, m):
        m.get(
            self.base_uri + "/donations",
            json=donorbox_test_data.get_donations_amount_min_3,
        )
        result = self.donorbox.get_donations(amount_min="3")
        assert result.num_rows == 3
        m.get(
            self.base_uri + "/donations",
            json=donorbox_test_data.get_donations_amount_min_4,
        )
        result = self.donorbox.get_donations(amount_min="4")
        assert result.num_rows == 1
        m.get(
            self.base_uri + "/donations",
            json=donorbox_test_data.get_donations_amount_min_5,
        )
        result = self.donorbox.get_donations(amount_min="5")
        assert result.num_rows == 0

    @unittest.skip("requires live account setup")
    @mark_live_test
    def test_get_donations_with_amount_min_filter_live_test(self):
        result = self.donorbox.get_donations(amount_min="3")
        assert result.num_rows == 3
        result = self.donorbox.get_donations(amount_min="4")
        assert result.num_rows == 1
        result = self.donorbox.get_donations(amount_min="5")
        assert result.num_rows == 0

    @requests_mock.Mocker()
    def test_get_donations_with_amount_max_filter(self, m):
        m.get(
            self.base_uri + "/donations",
            json=donorbox_test_data.get_donations_amount_max_3,
        )
        result = self.donorbox.get_donations(amount_max="3")
        assert result.num_rows == 2
        m.get(
            self.base_uri + "/donations",
            json=donorbox_test_data.get_donations_amount_max_4,
        )
        result = self.donorbox.get_donations(amount_max="4")
        assert result.num_rows == 3
        m.get(
            self.base_uri + "/donations",
            json=donorbox_test_data.get_donations_amount_max_2,
        )
        result = self.donorbox.get_donations(amount_max="2")
        assert result.num_rows == 0

    @unittest.skip("requires live account setup")
    @mark_live_test
    def test_get_donations_with_amount_max_filter_live_test(self):
        result = self.donorbox.get_donations(amount_max="3")
        assert result.num_rows == 2
        result = self.donorbox.get_donations(amount_max="4")
        assert result.num_rows == 3
        result = self.donorbox.get_donations(amount_max="2")
        assert result.num_rows == 0

    @requests_mock.Mocker()
    def test_get_donors(self, m):
        m.get(self.base_uri + "/donors", json=donorbox_test_data.get_donors_response_json)
        result = self.donorbox.get_donors()

        # Assert the method returns expected dict response
        assert result.to_dicts()[0] == donorbox_test_data.get_donors_response_json[0]
        columns = [
            "id",
            "created_at",
            "updated_at",
            "first_name",
            "last_name",
            "email",
            "phone",
            "address",
            "city",
            "state",
            "zip_code",
            "country",
            "employer",
            "occupation",
            "comment",
            "donations_count",
            "last_donation_at",
            "total",
        ]
        assert len(result.columns) == len(columns)

    @unittest.skip("requires live account setup")
    @mark_live_test
    def test_get_donors_live_test(self):
        result = self.donorbox.get_donors()
        assert isinstance(result, Table)
        columns = [
            "id",
            "created_at",
            "updated_at",
            "first_name",
            "last_name",
            "email",
            "phone",
            "address",
            "city",
            "state",
            "zip_code",
            "country",
            "employer",
            "occupation",
            "comment",
            "donations_count",
            "last_donation_at",
            "total",
        ]
        assert result.columns == columns
        assert result.num_rows == 2

    @requests_mock.Mocker()
    def test_get_donors_with_name_and_email_filters(self, m):
        m.get(
            self.base_uri + "/donors",
            json=donorbox_test_data.get_donors_response_json_first_name_filter,
        )
        result = self.donorbox.get_donors(first_name="Elizabeth")
        assert result.num_rows == 1
        assert result[0]["last_name"] == "Warren"
        m.get(
            self.base_uri + "/donors",
            json=donorbox_test_data.get_donors_response_json_last_name_filter,
        )
        result = self.donorbox.get_donors(last_name="Warren")
        assert result.num_rows == 1
        assert result[0]["first_name"] == "Elizabeth"
        m.get(
            self.base_uri + "/donors",
            json=donorbox_test_data.get_donors_response_json_donor_name_filter,
        )
        result = self.donorbox.get_donors(donor_name="Paul Wellstone")
        assert result.num_rows == 1
        assert result[0]["email"] == "paulwellstone@senate.gov"
        m.get(
            self.base_uri + "/donors",
            json=donorbox_test_data.get_donors_response_json_email_filter,
        )
        result = self.donorbox.get_donors(email="paulwellstone@senate.gov")
        assert result.num_rows == 1
        assert result[0]["first_name"] == "Paul"

    @requests_mock.Mocker()
    def test_get_plans(self, m):
        m.get(self.base_uri + "/plans", json=donorbox_test_data.get_plans_response_json)
        result = self.donorbox.get_plans()
        assert isinstance(result, Table)
        columns = [
            "id",
            "campaign",
            "donor",
            "type",
            "amount",
            "formatted_amount",
            "payment_method",
            "started_at",
            "last_donation_date",
            "next_donation_date",
            "status",
        ]
        assert result.columns == columns
        assert result.num_rows == 3

    @unittest.skip("requires live account setup")
    @mark_live_test
    def test_get_plans_live_test(self):
        result = self.donorbox.get_plans()
        assert isinstance(result, Table)
        columns = [
            "id",
            "campaign",
            "donor",
            "type",
            "amount",
            "formatted_amount",
            "payment_method",
            "started_at",
            "last_donation_date",
            "next_donation_date",
            "status",
        ]
        assert result.columns == columns
        assert result.num_rows == 3

    @unittest.skip("requires live account setup")
    @mark_live_test
    def test_get_plans_with_date_from_filter_live_test(self):
        # Correct formats (YYYY-mm-dd YYYY/mm/dd YYYYmmdd dd-mm-YYYY) successfully filter
        result = self.donorbox.get_plans(date_from="2022-10-20")
        assert isinstance(result, Table)
        assert result.num_rows == 1
        assert result[0]["started_at"] == "2022-10-20"
        # Try the other three formats quickly
        for date_string in ["2022/10/20", "20221020", "20-10-2022"]:
            assert self.donorbox.get_plans(date_from=date_string).num_rows == 1
        # Incorrect formats raise error
        with self.assertRaises(ValueError):
            result = self.donorbox.get_plans(date_from="10 20 2022")

    @unittest.skip("requires live account setup")
    @mark_live_test
    def test_get_plans_with_date_to_filter_live_test(self):
        # Correct formats (YYYY-mm-dd YYYY/mm/dd YYYYmmdd dd-mm-YYYY) successfully filter
        result = self.donorbox.get_plans(date_to="2022-10-20")
        assert isinstance(result, Table)
        assert result.num_rows == 2
        assert result[0]["started_at"] == "2022-10-19"
        # Try the other three formats quickly
        for date_string in ["2022/10/20", "20221020", "20-10-2022"]:
            assert self.donorbox.get_plans(date_to=date_string).num_rows == 2
        # Incorrect formats raise error
        with self.assertRaises(ValueError):
            result = self.donorbox.get_plans(date_to="10 20 2022")

    def test_date_format_helper(self):
        # valid formats work (should just run without error)
        for good_format in ["2022-10-20", "2022/10/20", "20221020", "20-10-2022"]:
            self.donorbox._date_format_helper(good_format)
        # invalid formats raise errors
        for bad_format in ["10 20 2022", "October 20th, 2022", "22-10-20"]:
            with self.assertRaises(ValueError):
                self.donorbox._date_format_helper(bad_format)
