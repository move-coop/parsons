from unittest import TestCase

import requests_mock

from parsons import Controlshift
from test.test_controlshift import test_cs_data as test_data  # type: ignore
from test.utils import mark_live_test, validate_list


@mark_live_test
class TestControlshiftLive(TestCase):
    def test_get_live_petitions(self):
        cs = Controlshift()
        tbl = cs.get_petitions()
        self.assertTrue(validate_list(test_data.expected_petition_columns, tbl))


class TestControlshiftMock(TestCase):
    def setUp(self):
        self.hostname = "https://test.example.com"

    @requests_mock.Mocker()
    def test_get_petitions(self, m):
        m.post(f"{self.hostname}/oauth/token", json={"access_token": "123"})
        cs = Controlshift(hostname=self.hostname, client_id="1234", client_secret="1234")

        m.get(f"{self.hostname}/api/v1/petitions", json=test_data.petition_test_data)
        tbl = cs.get_petitions()

        self.assertTrue(validate_list(test_data.expected_petition_columns, tbl))
