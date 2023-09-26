from parsons import VAN
from test.test_van.responses_people import get_person_response
from test.utils import assert_matching_tables
import requests_mock
import os
import unittest

os.environ["VAN_API_KEY"] = "SOME_KEY"


class TestNGPVAN(unittest.TestCase):
    def setUp(self):
        self.van = VAN(os.environ["VAN_API_KEY"], db="MyVoters", raise_for_status=False)

    @requests_mock.Mocker()
    def test_create_contact_note(self, m):
        m.post(self.van.connection.uri + "people/1/notes", status_code=204)
        self.van.create_contact_note(1, "a", True)

    @requests_mock.Mocker()
    def test_get_contact_notes(self, m):
        json = get_person_response["notes"]
        m.get(self.van.connection.uri + "people/1/notes", json=json)
        assert_matching_tables(json, self.van.get_contact_notes("1"))
