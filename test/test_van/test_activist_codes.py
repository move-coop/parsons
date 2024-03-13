import unittest
import os
import requests_mock
from parsons import VAN
from test.utils import validate_list

os.environ["VAN_API_KEY"] = "SOME_KEY"


class TestActivistCodes(unittest.TestCase):
    def setUp(self):

        self.van = VAN(os.environ["VAN_API_KEY"], db="MyVoters", raise_for_status=False)

    def tearDown(self):

        pass

    @requests_mock.Mocker()
    def test_get_activist_codes(self, m):

        # Create response
        json = {
            "count": 43,
            "items": [
                {
                    "status": "Active",
                    "scriptQuestion": None,
                    "name": "TEST CODE",
                    "mediumName": "TEST CODE",
                    "activistCodeId": 4388538,
                    "shortName": "TC",
                    "type": "Action",
                    "description": None,
                }
            ],
            "nextPageLink": None,
        }

        m.get(self.van.connection.uri + "activistCodes", json=json)

        # Expected Structure
        expected = [
            "status",
            "scriptQuestion",
            "name",
            "mediumName",
            "activistCodeId",
            "shortName",
            "type",
            "description",
        ]

        # Assert response is expected structure
        self.assertTrue(validate_list(expected, self.van.get_activist_codes()))

        # To Do: Test what happens when it doesn't find any ACs

    @requests_mock.Mocker()
    def test_get_activist_code(self, m):

        # Create response
        json = {
            "status": "Active",
            "scriptQuestion": "null",
            "name": "Anti-Choice",
            "mediumName": "Anti",
            "activistCodeId": 4135099,
            "shortName": "AC",
            "type": "Constituency",
            "description": "A person who has been flagged as anti-choice.",
        }

        m.get(self.van.connection.uri + "activistCodes/4388538", json=json)

        self.assertEqual(json, self.van.get_activist_code(4388538))

    @requests_mock.Mocker()
    def test_toggle_activist_code(self, m):

        # Test apply activist code
        m.post(self.van.connection.uri + "people/2335282/canvassResponses", status_code=204)
        self.assertTrue(self.van.toggle_activist_code(2335282, 4429154, "apply"), 204)

        # Test remove activist code
        m.post(self.van.connection.uri + "people/2335282/canvassResponses", status_code=204)
        self.assertTrue(self.van.toggle_activist_code(2335282, 4429154, "remove"), 204)

    @requests_mock.Mocker()
    def test_apply_activist_code(self, m):

        # Test apply activist code
        m.post(self.van.connection.uri + "people/2335282/canvassResponses", status_code=204)
        self.assertEqual(self.van.apply_activist_code(2335282, 4429154), 204)

    @requests_mock.Mocker()
    def test_remove_activist_code(self, m):

        # Test remove activist code
        m.post(self.van.connection.uri + "people/2335282/canvassResponses", status_code=204)
        self.assertEqual(self.van.remove_activist_code(2335282, 4429154), 204)
