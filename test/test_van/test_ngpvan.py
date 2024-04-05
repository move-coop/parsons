import os
import unittest
import requests_mock
from parsons import VAN, Table
from test.utils import validate_list, assert_matching_tables
from requests.exceptions import HTTPError


class TestNGPVAN(unittest.TestCase):
    def setUp(self):

        self.van = VAN(os.environ["VAN_API_KEY"], db="MyVoters", raise_for_status=False)

    def tearDown(self):

        pass

    @requests_mock.Mocker()
    def test_get_canvass_responses_contact_types(self, m):

        json = [{"name": "Auto Dial", "contactTypeId": 19, "channelTypeName": "Phone"}]

        m.get(self.van.connection.uri + "canvassResponses/contactTypes", json=json)

        assert_matching_tables(Table(json), self.van.get_canvass_responses_contact_types())

    @requests_mock.Mocker()
    def test_get_canvass_responses_input_types(self, m):

        json = [{"inputTypeId": 11, "name": "API"}]
        m.get(self.van.connection.uri + "canvassResponses/inputTypes", json=json)
        assert_matching_tables(Table(json), self.van.get_canvass_responses_input_types())

    @requests_mock.Mocker()
    def test_get_canvass_responses_result_codes(self, m):

        json = [
            {
                "shortName": "BZ",
                "resultCodeId": 18,
                "name": "Busy",
                "mediumName": "Busy",
            }
        ]

        m.get(self.van.connection.uri + "canvassResponses/resultCodes", json=json)
        assert_matching_tables(Table(json), self.van.get_canvass_responses_result_codes())

    @requests_mock.Mocker()
    def test_get_survey_questions(self, m):

        json = {
            "count": 67,
            "items": [
                {
                    "status": "Active",
                    "responses": [
                        {
                            "shortName": "1",
                            "surveyResponseId": 1288926,
                            "name": "1-Strong Walz",
                            "mediumName": "1",
                        },
                        {
                            "shortName": "2",
                            "surveyResponseId": 1288928,
                            "name": "2-Lean Walz",
                            "mediumName": "2",
                        },
                    ],
                    "scriptQuestion": "Who do you support for Governor?",
                    "name": "MN Governor Gen",
                    "surveyQuestionId": 311838,
                    "mediumName": "MNGovG",
                    "shortName": "MGG",
                    "type": "Candidate",
                    "cycle": 2018,
                }
            ],
            "nextPageLink": None,
        }

        m.get(self.van.connection.uri + "surveyQuestions", json=json)

        expected = [
            "status",
            "responses",
            "scriptQuestion",
            "name",
            "surveyQuestionId",
            "mediumName",
            "shortName",
            "type",
            "cycle",
        ]

        self.assertTrue(validate_list(expected, self.van.get_survey_questions()))

    @requests_mock.Mocker()
    def test_get_supporter_groups(self, m):

        json = {
            "items": [
                {"id": 12, "name": "tmc", "description": "A fun group."},
                {"id": 13, "name": "tmc", "description": "A fun group."},
            ],
            "nextPageLink": None,
            "count": 3,
        }

        m.get(self.van.connection.uri + "supporterGroups", json=json)

        ["id", "name", "description"]

        self.van.get_supporter_groups()

    @requests_mock.Mocker()
    def test_get_supporter_group(self, m):

        json = [{"id": 12, "name": "tmc", "description": "A fun group."}]
        m.get(self.van.connection.uri + "supporterGroups/12", json=json)

        # Test that columns are expected columns
        self.assertEqual(self.van.get_supporter_group(12), json)

    @requests_mock.Mocker()
    def test_delete_supporter_group(self, m):

        # Test good input
        good_supporter_group_id = 5
        good_ep = f"supporterGroups/{good_supporter_group_id}"
        m.delete(self.van.connection.uri + good_ep, status_code=204)
        self.van.delete_supporter_group(good_supporter_group_id)

        # Test bad input raises
        bad_supporter_group_id = 999
        # bad_vanid = 99999
        bad_ep = f"supporterGroups/{bad_supporter_group_id}"
        m.delete(self.van.connection.uri + bad_ep, status_code=404)
        self.assertRaises(HTTPError, self.van.delete_supporter_group, bad_supporter_group_id)

    @requests_mock.Mocker()
    def test_add_person_supporter_group(self, m):

        # Test good input
        good_supporter_group_id = 5
        good_vanid = 12345
        good_uri = f"supporterGroups/{good_vanid}/people/{good_supporter_group_id}"
        m.put(self.van.connection.uri + good_uri, status_code=204)
        self.van.add_person_supporter_group(good_vanid, good_supporter_group_id)

        # Test bad input
        bad_supporter_group_id = 999
        bad_vanid = 99999
        bad_uri = f"supporterGroups/{bad_vanid}/people/{bad_supporter_group_id}"
        m.put(self.van.connection.uri + bad_uri, status_code=404)
        self.assertRaises(
            HTTPError,
            self.van.add_person_supporter_group,
            bad_vanid,
            bad_supporter_group_id,
        )

    @requests_mock.Mocker()
    def test_delete_person_supporter_group(self, m):

        # Test good input
        good_supporter_group_id = 5
        good_vanid = 12345
        good_ep = f"supporterGroups/{good_vanid}/people/{good_supporter_group_id}"
        m.delete(self.van.connection.uri + good_ep, status_code=204)
        self.van.delete_person_supporter_group(good_vanid, good_supporter_group_id)

        # Test bad input raises
        bad_supporter_group_id = 999
        bad_vanid = 99999
        bad_ep = f"supporterGroups/{bad_vanid}/people/{bad_supporter_group_id}"
        m.delete(self.van.connection.uri + bad_ep, status_code=404)
        self.assertRaises(
            HTTPError,
            self.van.delete_person_supporter_group,
            bad_vanid,
            bad_supporter_group_id,
        )


if __name__ == "__main__":

    unittest.main()
