import os
import requests_mock
from unittest import TestCase
from test.utils import mark_live_test, validate_list
from parsons.controlshift.controlshift import Controlshift
from test.test_controlshift import test_data  # type: ignore


@mark_live_test
class TestControlshiftLive(TestCase):

    def test_get_live_petitions(self):
        cs = Controlshift()
        tbl = cs.get_petitions()
        self.assertTrue(validate_list(test_data.expected_petition_columns, tbl))


class TestControlshiftMock(TestCase):

    def setUp(self):
        self.hostname = os.environ["CONTROLSHIFT_HOSTNAME"]

    @requests_mock.Mocker()
    def test_get_petitions(self, m):
        m.post(
            f'{self.hostname}/oauth/token',
            json={'access_token': '123'})
        cs = Controlshift()

        m.get(f'{self.hostname}/api/v1/petitions', json=test_data.petition_test_data)
        tbl = cs.get_petitions()

        self.assertTrue(validate_list(test_data.expected_petition_columns, tbl))
