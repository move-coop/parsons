import unittest
import os
import requests_mock
from parsons import VAN
from test.test_van.responses_printed_lists import list_json, single_list_json


class TestSavedLists(unittest.TestCase):
    def setUp(self):

        self.van = VAN(os.environ["VAN_API_KEY"], db="MyVoters", raise_for_status=False)

    @requests_mock.Mocker()
    def test_get_printed_lists(self, m):

        m.get(self.van.connection.uri + "printedLists", json=list_json)

        result = self.van.get_printed_lists(folder_name="Covington Canvass Turfs")

        self.assertEqual(result.num_rows, 14)

    @requests_mock.Mocker()
    def test_get_printed_list(self, m):

        m.get(self.van.connection.uri + "printedLists/43-0000", json=single_list_json)

        result = self.van.get_printed_list(printed_list_number="43-0000")

        self.assertEqual(result["number"], "43-0000")
