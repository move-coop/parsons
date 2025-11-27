import unittest
from pathlib import Path

import requests_mock

from parsons import TurboVote
from test.utils import validate_list

_dir = Path(__file__).parent

fake_token = {"id-token": "FAKE-TOKEN"}


class TestTurboVote(unittest.TestCase):
    def setUp(self):
        self.tv = TurboVote("usr", "pwd", "myorg")

    def test_init(self):
        assert self.tv.username == "usr"
        assert self.tv.password == "pwd"
        assert self.tv.subdomain == "myorg"

    @requests_mock.Mocker()
    def test_get_token(self, m):
        # Assert the token is returned
        m.post(self.tv.uri + "login", json=fake_token)
        assert fake_token["id-token"] == self.tv._get_token()

    @requests_mock.Mocker()
    def test_get_users(self, m):
        expected = [
            "id",
            "first-name",
            "middle-name",
            "last-name",
            "phone",
            "email",
            "registered-address-street",
            "registered-address-street-2",
            "registered-address-city",
            "registered-address-state",
            "registered-address-zip",
            "mailing-address-street",
            "mailing-address-street-2",
            "mailing-address-city",
            "mailing-address-state",
            "mailing-address-zip",
            "dob",
            "language-preference",
            "hostname",
            "referral-code",
            "partner-comms-opt-in",
            "created-at",
            "updated-at",
            "voter-registration-status",
            "voter-registration-source",
            "voter-registration-method",
            "voting-method-preference",
            "email subscribed",
            "sms subscribed",
        ]

        with (_dir / "users.txt").open(mode="r") as users_text:
            # Mock endpoints
            m.post(self.tv.uri + "login", json=fake_token)
            m.get(
                self.tv.uri + f"partners/{self.tv.subdomain}.turbovote.org/users",
                text=users_text.read(),
            )

        assert validate_list(expected, self.tv.get_users())
