import os
import unittest

import requests_mock

from parsons import VAN

os.environ["VAN_API_KEY"] = "SOME_KEY"


class TestNGPVAN(unittest.TestCase):
    def setUp(self):
        self.van = VAN(os.environ["VAN_API_KEY"], db="MyVoters")

    def tearDown(self):
        pass

    @requests_mock.Mocker()
    def test_get_apikeyprofiles(self, m):
        json = {
            "items": [
                {
                    "databaseName": "SmartVAN Massachusetts",
                    "hasMyVoters": True,
                    "hasMyCampaign": True,
                    "committeeName": "People for Good",
                    "apiKeyTypeName": "Custom Integration",
                    "keyReference": "1234",
                    "userFirstName": "peopleforgood",
                    "userLastName": "api",
                    "username": "peopleforgood.api",
                    "userId": 4321,
                }
            ],
            "nextPageLink": None,
            "count": 1,
        }

        m.get(self.van.connection.uri + "apiKeyProfiles", json=json)

        # # Call the method that makes the API request
        response = self.van.get_apikeyprofiles()

        # Assert that the response is a dictionary (JSON object)
        self.assertIsInstance(response, dict)

        # Assert that the response matches the expected JSON
        # I have to access a part of the json because the response is a list of dictionaries
        # and the VAN Connector handles the pagination and unpacks the list of dictionaries
        self.assertEqual(response, json["items"][0])
