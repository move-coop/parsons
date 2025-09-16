import os
import unittest

import pytest

from parsons import FacebookAds, Table

users_table = Table(
    [
        {
            "first": "Bob",
            "middle": "J",
            "last": "Smith",
            "phone": "1234567890",
            "cell": None,
            "vb_voterbase_dob": "19820413",
        },
        {
            "first": "Sue",
            "middle": "Lucy",
            "last": "Doe",
            "phone": None,
            "cell": "2345678901",
            "vb_voterbase_dob": None,
        },
    ]
)


@unittest.skipIf(not os.environ.get("LIVE_TEST"), "Skipping because not running live test")
class TestFacebookAdsIntegration(unittest.TestCase):
    def setUp(self):
        self.fb_ads = FacebookAds()

        self.audience_id = self.fb_ads.create_custom_audience(
            name="Test Audience", data_source="USER_PROVIDED_ONLY"
        )

    def tearDown(self):
        self.fb_ads.delete_custom_audience(self.audience_id)

    def test_create_custom_audience(self):
        # Audience created in setUp
        assert self.audience_id is not None

    def test_create_custom_audience_bad_data_source(self):
        with pytest.raises(KeyError):
            self.fb_ads.create_custom_audience(
                name="Something",
                data_source="INVALID",
            )

    def test_add_users_to_custom_audience(self):
        # Note we don't actually check the results of adding these users, eg. how many were
        # matched by FB. This test just ensures the method doesn't error.
        # TODO See if we can do a more effective test.
        self.fb_ads.add_users_to_custom_audience(self.audience_id, users_table)

    def test_add_users_to_custom_audience_no_valid_columns(self):
        # We don't yet support full names for matching, so this shouldn't work
        tbl = Table(
            [
                {"full name": "Bob Smith"},
            ]
        )
        with pytest.raises(KeyError):
            self.fb_ads.add_users_to_custom_audience(self.audience_id, tbl)


class TestFacebookAdsUtilities(unittest.TestCase):
    def test_get_match_key_for_column(self):
        # Test just a few of the mappings
        assert FacebookAds._get_match_key_for_column("email") == "EMAIL"
        assert FacebookAds._get_match_key_for_column("voterbase_email") == "EMAIL"
        assert FacebookAds._get_match_key_for_column("first name") == "FN"
        assert FacebookAds._get_match_key_for_column("FIRST-NAME ") == "FN"
        assert FacebookAds._get_match_key_for_column("vb_tsmart_first_name") == "FN"
        assert FacebookAds._get_match_key_for_column("Last Name!") == "LN"
        assert FacebookAds._get_match_key_for_column("state code") == "ST"
        assert FacebookAds._get_match_key_for_column("vb_vf_source_state") == "ST"
        assert FacebookAds._get_match_key_for_column("vb_voterbase_gender") == "GEN"
        assert FacebookAds._get_match_key_for_column("vb_voterbase_phone_wireless") == "PHONE"
        assert FacebookAds._get_match_key_for_column("invalid") is None

    def test_get_preprocess_key_for_column(self):
        assert FacebookAds._get_preprocess_key_for_column("vb_voterbase_dob") == "DOB YYYYMMDD"

    def test_get_match_table_for_users_table(self):
        # This tests basic column matching, as well as the more complex cases like:
        # - Where multiple columns map to the same FB key ("PHONE").
        # - Parsing of a YYYYMMDD birth date column.
        t = FacebookAds.get_match_table_for_users_table(users_table)

        row0 = t[0]
        assert t.columns == ["FN", "LN", "PHONE", "DOBY", "DOBM", "DOBD"]
        assert row0["FN"] == "Bob"
        assert row0["LN"] == "Smith"
        assert row0["PHONE"] == "1234567890"
        assert row0["DOBY"] == "1982"
        assert row0["DOBM"] == "04"
        assert row0["DOBD"] == "13"

        row1 = t[1]
        assert row1["FN"] == "Sue"
        assert row1["LN"] == "Doe"
        assert row1["PHONE"] == "2345678901"
        assert row1["DOBY"] == ""
        assert row1["DOBM"] == ""
        assert row1["DOBD"] == ""

    def test_get_match_schema_and_data(self):
        match_table = Table(
            [
                {"FN": "Bob", "LN": "Smith"},
                {"FN": "Sue", "LN": "Doe"},
            ]
        )
        (schema, data) = FacebookAds._get_match_schema_and_data(match_table)
        assert schema == ["FN", "LN"]
        assert data[0] == ("Bob", "Smith")
        assert data[1] == ("Sue", "Doe")
