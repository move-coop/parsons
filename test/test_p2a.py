import copy
import os
import unittest

import pytest
import requests_mock

from parsons import Phone2Action
from test.utils import validate_list

adv_json = {
    "data": [
        {
            "id": 7125439,
            "prefix": "Mr.",
            "firstname": "Bob",
            "middlename": "Smith",
            "lastname": "Smit",
            "suffix": None,
            "notes": None,
            "stage": None,
            "connections": 3,
            "tags": [
                "register-to-vote-38511",
                "registered-to-vote-for-2018-38511",
            ],
            "created_at": "2017-05-23 23:36:04.000000",
            "updated_at": "2018-12-17 21:55:24.000000",
            "address": {
                "street1": "25255 Maine Ave",
                "street2": "",
                "city": "Los Angeles",
                "state": "CA",
                "zip5": 96055,
                "zip4": 9534,
                "county": "Tehama",
                "latitude": "50.0632635",
                "longitude": "-122.09654",
            },
            "districts": {
                "congressional": "1",
                "stateSenate": "4",
                "stateHouse": "3",
                "cityCouncil": None,
            },
            "ids": [],
            "memberships": [
                {
                    "id": 15151443,
                    "campaignid": 25373,
                    "name": "20171121 Businesses for Responsible Tax Reform - Contact Congress",
                    "source": None,
                    "created_at": "2017-11-21 23:28:30.000000",
                },
                {
                    "id": 20025582,
                    "campaignid": 32641,
                    "name": "20180524 March for America",
                    "source": None,
                    "created_at": "2018-05-24 21:09:49.000000",
                },
            ],
            "fields": [],
            "phones": [{"id": 10537860, "address": "+19995206447", "subscribed": "false"}],
            "emails": [
                {"id": 10537871, "address": "N@k.com", "subscribed": "false"},
                {"id": 10950446, "address": "email@me.com", "subscribed": "false"},
            ],
        }
    ],
    "pagination": {
        "count": 1,
        "per_page": 100,
        "current_page": 1,
        "next_url": "https://api.phone2action.com/2.0/advocates?page=2",
    },
}

camp_json = [
    {
        "id": 25373,
        "name": "20171121 Businesses for Responsible Tax Reform - Contact Congress",
        "display_name": "Businesses for Responsible Tax Reform",
        "subtitle": "Tell Congress: Stand up for responsible tax reform!",
        "public": 1,
        "topic": None,
        "type": "CAMPAIGN",
        "link": "http://p2a.co/KHcUyTK",
        "restrict_allow": None,
        "content": {
            "summary": "",
            "introduction": "Welcome",
            "call_to_action": "Contact your officials in one click!",
            "thank_you": "<p>Thanks for taking action. Please encourage others to act by "
            "sharing on social media.</p>",
            "background_image": None,
        },
        "updated_at": {
            "date": "2017-11-21 23:27:11.000000",
            "timezone_type": 3,
            "timezone": "UTC",
        },
    }
]


def parse_request_body(m):
    kvs = m.split("&")
    return {kv.split("=")[0]: kv.split("=")[1] for kv in kvs}


class TestP2A(unittest.TestCase):
    def setUp(self):
        self.p2a = Phone2Action(app_id="an_id", app_key="app_key")

    def tearDown(self):
        pass

    def test_init_args(self):
        # Test initializing class with args
        # Done in the setUp

        pass

    def test_init_envs(self):
        # Test initilizing class with envs

        os.environ["PHONE2ACTION_APP_ID"] = "id"
        os.environ["PHONE2ACTION_APP_KEY"] = "key"

        p2a_envs = Phone2Action()
        assert p2a_envs.app_id == "id"
        assert p2a_envs.app_key == "key"

    @requests_mock.Mocker()
    def test_get_advocates(self, m):
        m.get(self.p2a.client.uri + "advocates", json=adv_json)

        adv_exp = [
            "id",
            "prefix",
            "firstname",
            "middlename",
            "lastname",
            "suffix",
            "notes",
            "stage",
            "connections",
            "created_at",
            "updated_at",
            "address_city",
            "address_county",
            "address_latitude",
            "address_longitude",
            "address_state",
            "address_street1",
            "address_street2",
            "address_zip4",
            "address_zip5",
            "districts_cityCouncil",
            "districts_congressional",
            "districts_stateHouse",
            "districts_stateSenate",
        ]

        assert validate_list(adv_exp, self.p2a.get_advocates()["advocates"])
        ids_exp = ["advocate_id", "ids"]

        assert validate_list(ids_exp, self.p2a.get_advocates()["ids"])

        phone_exp = ["advocate_id", "phones_address", "phones_id", "phones_subscribed"]
        assert validate_list(phone_exp, self.p2a.get_advocates()["phones"])

        tags_exp = ["advocate_id", "tags"]
        assert validate_list(tags_exp, self.p2a.get_advocates()["tags"])

        email_exp = ["advocate_id", "emails_address", "emails_id", "emails_subscribed"]
        assert validate_list(email_exp, self.p2a.get_advocates()["emails"])

        member_exp = [
            "advocate_id",
            "memberships_campaignid",
            "memberships_created_at",
            "memberships_id",
            "memberships_name",
            "memberships_source",
        ]
        assert validate_list(member_exp, self.p2a.get_advocates()["memberships"])

        fields_exp = ["advocate_id", "fields"]
        assert validate_list(fields_exp, self.p2a.get_advocates()["fields"])

    @requests_mock.Mocker()
    def test_get_advocates__by_page(self, m):
        response = copy.deepcopy(adv_json)
        # Make it look like there's more data
        response["pagination"]["count"] = 100

        m.get(self.p2a.client.uri + "advocates?page=1", json=adv_json)
        m.get(
            self.p2a.client.uri + "advocates?page=2",
            exc=Exception("Should only call once"),
        )

        results = self.p2a.get_advocates(page=1)
        assert results["advocates"].num_rows, 1

    @requests_mock.Mocker()
    def test_get_advocates__empty(self, m):
        response = copy.deepcopy(adv_json)
        response["data"] = []
        # Make it look like there's more data
        response["pagination"]["count"] = 0

        m.get(self.p2a.client.uri + "advocates", json=adv_json)

        results = self.p2a.get_advocates()
        assert results["advocates"].num_rows, 0

    @requests_mock.Mocker()
    def test_get_campaigns(self, m):
        camp_exp = [
            "id",
            "name",
            "display_name",
            "subtitle",
            "public",
            "topic",
            "type",
            "link",
            "restrict_allow",
            "updated_at_date",
            "updated_at_timezone",
            "updated_at_timezone_type",
            "content_background_image",
            "content_call_to_action",
            "content_introduction",
            "content_summary",
            "content_thank_you",
        ]

        m.get(self.p2a.client.uri + "campaigns", json=camp_json)

        assert validate_list(camp_exp, self.p2a.get_campaigns())

    @requests_mock.Mocker()
    def test_create_advocate(self, m):
        m.post(self.p2a.client.uri + "advocates", json={"advocateid": 1})

        # Test arg validation - create requires a phone or an email
        with pytest.raises(
            ValueError,
            match="When creating an advocate, you must provide an email address or a phone number",
        ):
            self.p2a.create_advocate(campaigns=[1], firstname="Foo", lastname="bar")

        # Test arg validation - sms opt in requires a phone
        with pytest.raises(
            ValueError,
            match="When opting an advocate in or out of SMS messages, you must specify a valid phone and one or more campaigns",
        ):
            self.p2a.create_advocate(campaigns=[1], email="foo@bar.com", sms_optin=True)

        # Test arg validation - email opt in requires a email
        with pytest.raises(
            ValueError,
            match="When opting an advocate in or out of email messages, you must specify a valid email address and one or more campaigns",
        ):
            self.p2a.create_advocate(campaigns=[1], phone="1234567890", email_optin=True)

        # Test a successful call
        advocateid = self.p2a.create_advocate(
            campaigns=[1], email="foo@bar.com", email_optin=True, firstname="Test"
        )
        assert m.called
        assert advocateid == 1

        # Check that the properties were mapped
        data = parse_request_body(m.last_request.text)
        assert data["firstname"] == "Test"
        assert "lastname" not in data
        assert data["emailOptin"] == "1"
        assert data["email"] == "foo%40bar.com"

    @requests_mock.Mocker()
    def test_update_advocate(self, m):
        m.post(self.p2a.client.uri + "advocates")

        # Test arg validation - sms opt in requires a phone
        with pytest.raises(
            ValueError,
            match="When opting an advocate in or out of SMS messages, you must specify a valid phone and one or more campaigns",
        ):
            self.p2a.update_advocate(advocate_id=1, sms_optin=True)

        # Test arg validation - email opt in requires a email
        with pytest.raises(
            ValueError,
            match="When opting an advocate in or out of email messages, you must specify a valid email address and one or more campaigns",
        ):
            self.p2a.update_advocate(advocate_id=1, email_optin=True)

        # Test a successful call
        self.p2a.update_advocate(
            advocate_id=1,
            campaigns=[1],
            email="foo@bar.com",
            email_optin=True,
            firstname="Test",
        )
        assert m.called

        # Check that the properties were mapped
        data = parse_request_body(m.last_request.text)
        assert data["firstname"] == "Test"
        assert "lastname" not in data
        assert data["emailOptin"] == "1"
        assert data["email"] == "foo%40bar.com"
