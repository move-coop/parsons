import unittest
import requests_mock
from parsons.mobilecommons import MobileCommons
from parsons.etl import Table
from mobilecommons_responses import (
    get_profiles_response,
    get_broadcasts_response,
    post_profile_response,
)


MOBILECOMMONS_USERNAME = "MOBILECOMMONS_USERNAME"
MOBILECOMMONS_PASSWORD = "MOBILECOMMONS_PASSWORD"
DEFAULT_GET_PARAMS = {"page": 1, "limit": 1000}
DEFAULT_GET_ENDPOINT = "broadcasts"
DEFAULT_FIRST_KEY = "broadcasts"
DEFAULT_SECOND_KEY = "broadcast"
DEFAULT_POST_PARAMS = {"phone": 13073997994}
DEFAULT_POST_ENDPOINT = "profile_update"


class TestMobileCommons(unittest.TestCase):
    @requests_mock.Mocker()
    def setUp(self, m):
        self.base_uri = "https://secure.mcommons.com/api/"

        self.mc = MobileCommons(
            username=MOBILECOMMONS_USERNAME, password=MOBILECOMMONS_PASSWORD
        )

    @requests_mock.Mocker()
    def test_parse_get_request(self, m):
        m.get(
            self.base_uri + DEFAULT_GET_ENDPOINT,
            status_code=get_profiles_response.status_code,
            text=get_profiles_response.text,
        )
        parsed_get_request_text = self.mc._parse_get_request(
            endpoint=DEFAULT_GET_ENDPOINT, params=DEFAULT_GET_PARAMS
        )
        self.assertIsInstance(parsed_get_request_text, dict)

    @requests_mock.Mocker()
    def test_mc_get_request(self, m):
        m.get(
            self.base_uri + DEFAULT_GET_ENDPOINT,
            status_code=get_broadcasts_response.status_code,
            text=get_broadcasts_response.text,
        )
        parsed_get_response_text = self.mc._mc_get_request(
            params=DEFAULT_GET_PARAMS,
            endpoint=DEFAULT_GET_ENDPOINT,
            first_data_key=DEFAULT_FIRST_KEY,
            second_data_key=DEFAULT_SECOND_KEY,
        )
        self.assertIsInstance(
            parsed_get_response_text,
            Table,
            "MobileCommons.mc_get_request does output parsons table",
        )

    @requests_mock.Mocker()
    def test_get_profiles(self, m):
        m.get(
            self.base_uri + "profiles",
            status_code=get_profiles_response.status_code,
            text=get_profiles_response.text,
        )
        profiles = self.mc.get_profiles(limit=1000)
        self.assertIsInstance(
            profiles,
            Table,
            "MobileCommons.get_profiles method did not return a parsons Table",
        )
        self.assertEqual(
            profiles[0]["first_name"],
            "James",
            "MobileCommons.get_profiles method not returning a table structured"
            "as expected",
        )

    @requests_mock.Mocker()
    def test_get_broadcasts(self, m):
        m.get(
            self.base_uri + "broadcasts",
            status_code=get_broadcasts_response.status_code,
            text=get_broadcasts_response.text,
        )
        broadcasts = self.mc.get_broadcasts(limit=1000)
        self.assertIsInstance(
            broadcasts,
            Table,
            "MobileCommons.get_broadcasts method did not return a parsons Table",
        )
        self.assertEqual(
            broadcasts[0]["id"],
            "2543129",
            "MobileCommons.get_broadcasts method not returning a table structured"
            "as expected",
        )

    @requests_mock.Mocker()
    def test_mc_post_request(self, m):
        m.post(self.base_uri + "profile_update", text=post_profile_response.text)
        response_dict = self.mc._mc_post_request(
            endpoint=DEFAULT_POST_ENDPOINT, params=DEFAULT_POST_PARAMS
        )
        self.assertIsInstance(
            response_dict,
            dict,
            "MobileCommons.mc_post_request output not expected type dictionary",
        )
        self.assertEqual(
            response_dict["profile"]["id"],
            "602169563",
            "MobileCommons.mc_post_request output value not expected",
        )

    @requests_mock.Mocker()
    def test_create_profile(self, m):
        m.post(self.base_uri + "profile_update", text=post_profile_response.text)
        profile_id = self.mc.create_profile(phone=13073997994)
        self.assertEqual(
            profile_id,
            "602169563",
            "MobileCommons.create_profile does not return expected profile_id",
        )
