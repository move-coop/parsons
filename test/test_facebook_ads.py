import unittest
import os

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
        self.assertIsNotNone(self.audience_id)

    def test_create_custom_audience_bad_data_source(self):
        self.assertRaises(
            KeyError,
            self.fb_ads.create_custom_audience,
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
        self.assertRaises(KeyError, self.fb_ads.add_users_to_custom_audience, self.audience_id, tbl)


class TestFacebookAdsUtilities(unittest.TestCase):
    def test_get_match_key_for_column(self):
        # Test just a few of the mappings
        self.assertEqual("EMAIL", FacebookAds._get_match_key_for_column("email"))
        self.assertEqual("EMAIL", FacebookAds._get_match_key_for_column("voterbase_email"))
        self.assertEqual("FN", FacebookAds._get_match_key_for_column("first name"))
        self.assertEqual("FN", FacebookAds._get_match_key_for_column("FIRST-NAME "))
        self.assertEqual("FN", FacebookAds._get_match_key_for_column("vb_tsmart_first_name"))
        self.assertEqual("LN", FacebookAds._get_match_key_for_column("Last Name!"))
        self.assertEqual("ST", FacebookAds._get_match_key_for_column("state code"))
        self.assertEqual("ST", FacebookAds._get_match_key_for_column("vb_vf_source_state"))
        self.assertEqual("GEN", FacebookAds._get_match_key_for_column("vb_voterbase_gender"))
        self.assertEqual(
            "PHONE",
            FacebookAds._get_match_key_for_column("vb_voterbase_phone_wireless"),
        )
        self.assertIsNone(FacebookAds._get_match_key_for_column("invalid"))

    def test_get_preprocess_key_for_column(self):
        self.assertEqual(
            "DOB YYYYMMDD",
            FacebookAds._get_preprocess_key_for_column("vb_voterbase_dob"),
        )

    def test_get_match_table_for_users_table(self):
        # This tests basic column matching, as well as the more complex cases like:
        # - Where multiple columns map to the same FB key ("PHONE").
        # - Parsing of a YYYYMMDD birth date column.
        t = FacebookAds.get_match_table_for_users_table(users_table)

        row0 = t[0]
        self.assertEqual(["FN", "LN", "PHONE", "DOBY", "DOBM", "DOBD"], t.columns)
        self.assertEqual("Bob", row0["FN"])
        self.assertEqual("Smith", row0["LN"])
        self.assertEqual("1234567890", row0["PHONE"])
        self.assertEqual("1982", row0["DOBY"])
        self.assertEqual("04", row0["DOBM"])
        self.assertEqual("13", row0["DOBD"])

        row1 = t[1]
        self.assertEqual("Sue", row1["FN"])
        self.assertEqual("Doe", row1["LN"])
        self.assertEqual("2345678901", row1["PHONE"])
        self.assertEqual("", row1["DOBY"])
        self.assertEqual("", row1["DOBM"])
        self.assertEqual("", row1["DOBD"])

    def test_get_match_schema_and_data(self):
        match_table = Table(
            [
                {"FN": "Bob", "LN": "Smith"},
                {"FN": "Sue", "LN": "Doe"},
            ]
        )
        (schema, data) = FacebookAds._get_match_schema_and_data(match_table)
        self.assertEqual(["FN", "LN"], schema)
        self.assertEqual(("Bob", "Smith"), data[0])
        self.assertEqual(("Sue", "Doe"), data[1])
