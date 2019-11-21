import unittest
import os
import requests_mock
from parsons.ngpvan.van import VAN
from parsons.etl.table import Table
from test.utils import validate_list, assert_matching_tables
from requests.exceptions import HTTPError


class TestNGPVAN(unittest.TestCase):

    def setUp(self):

        self.van = VAN(os.environ['VAN_API_KEY'], db="MyVoters", raise_for_status=False)

    def tearDown(self):

        pass

    @requests_mock.Mocker()
    def test_get_canvass_responses_contact_types(self, m):

        json = {"name": "Auto Dial",
                "contactTypeId": 19,
                "channelTypeName": "Phone"}

        m.get(self.van.connection.uri + 'canvassResponses/contactTypes', json=json)

        assert_matching_tables(Table(json), self.van.get_canvass_responses_contact_types())

    @requests_mock.Mocker()
    def test_get_canvass_responses_input_types(self, m):

        json = {"inputTypeId": 11, "name": "API"}
        m.get(self.van.connection.uri + 'canvassResponses/inputTypes', json=json)
        assert_matching_tables(Table(json), self.van.get_canvass_responses_input_types())

    @requests_mock.Mocker()
    def test_get_canvass_responses_result_codes(self, m):

        json = {
            "shortName": "BZ",
            "resultCodeId": 18,
            "name": "Busy",
            "mediumName": "Busy"
        }

        m.get(self.van.connection.uri + 'canvassResponses/resultCodes', json=json)
        assert_matching_tables(Table(json), self.van.get_canvass_responses_result_codes())

    @requests_mock.Mocker()
    def test_get_saved_lists(self, m):

        json = {'count': 1, 'items': [
            {"savedListId": 517612,
             "listCount": 974656,
             "name": "LikelyParents(16andunder)_DWID_S... - MN",
             "doorCount": 520709,
             "description": "null"
             }
        ], 'nextPageLink': None}

        m.get(self.van.connection.uri + 'savedLists', json=json)

        expected = ['savedListId', 'listCount', 'name', 'doorCount','description']

        self.assertTrue(validate_list(expected, self.van.get_saved_lists()))

    @requests_mock.Mocker()
    def test_get_saved_list(self, m):

        saved_list_id = 517612

        json = {"savedListId": 517612,
                "listCount": 974656,
                "name": "LikelyParents(16andunder)_DWID_S... - MN",
                "doorCount": 520709,
                "description": "null"
                }

        m.get(self.van.connection.uri + f'savedLists/{saved_list_id}', json=json)

        expected = ['savedListId', 'listCount', 'name', 'doorCount', 'description']

        self.assertEqual(self.van.get_saved_list(saved_list_id), json)

    @requests_mock.Mocker()
    def test_get_folders(self, m):

        json = {u'count': 2,
                u'items': [
                    {
                        u'folderId': 5046,
                        u'name': u'#2018_MN_active_universe'
                    },
                    {u'folderId': 2168,
                     u'name': u'API Generated Lists'
                     }
                ], u'nextPageLink': None}

        m.get(self.van.connection.uri + 'folders', json=json)

        expected = ['folderId', 'name']

        self.assertTrue(validate_list(expected, self.van.get_folders()))

    @requests_mock.Mocker()
    def test_get_folder(self, m):

        folder_id = 5046

        json = {"folderId": 5046, "name": "#2018_MN_active_universe"}

        m.get(self.van.connection.uri + f'folders/{folder_id}', json=json)

        self.assertEqual(json, self.van.get_folder(folder_id))

    @requests_mock.Mocker()
    def test_export_job_types(self, m):

        json = {u'count': 1, u'items':
                [{u'exportJobTypeId': 4, u'name': u'SavedListExport'}],
                u'nextPageLink': None}

        m.get(self.van.connection.uri + 'exportJobTypes', json=json)

        expected = ['exportJobTypeId', 'name']

        self.assertTrue(validate_list(expected, self.van.get_export_job_types()))

    @requests_mock.Mocker()
    def test_export_job_create(self, m):

        saved_list_id = 517612

        json = {"status": "Completed",
                "errorCode": "null",
                "exportJobGuid": "bf4d1297-1c77-3fb2-03bd-f0acda122d37",
                "activistCodes": "null",
                "canvassFileRequestId": 448,
                "dateExpired": "2018-09-08T16:04:00Z",
                "surveyQuestions": "null",
                "webhookUrl": "https://www.nothing.com/",
                "downloadUrl": "https://ngpvan.blob.core.windows.net/canvass-files-savedlistexport/bf4d1297-1c77-3fb2-03bd-f0acda122d37_2018-09-08T13:03:27.7191831-04:00.csv",  # noqa: E501
                "savedListId": 517612,
                "districtFields": "null",
                "canvassFileRequestGuid": "bf4d1297-1c77-3fb2-03bd-f0acda122d37",
                "customFields": "null",
                "type": 4,
                "exportJobId": 448}

        m.post(self.van.connection.uri + 'exportJobs', json=json, status_code=201)

        expected = [
            'status',
            'errorCode',
            'exportJobGuid',
            'activistCodes',
            'canvassFileRequestId',
            'dateExpired',
            'surveyQuestions',
            'webhookUrl',
            'downloadUrl',
            'savedListId',
            'districtFields',
            'canvassFileRequestGuid',
            'customFields',
            'type',
            'exportJobId']

        self.assertEqual(json,self.van.export_job_create(saved_list_id))

    @requests_mock.Mocker()
    def test_get_export_job(self, m):

        export_job_id = 448

        json = {"status": "Completed",
                "errorCode": "null",
                "exportJobGuid": "bf4d1297-1c77-3fb2-03bd-f0acda122d37",
                "activistCodes": "null",
                "canvassFileRequestId": 448,
                "dateExpired": "2018-09-08T16:04:00Z",
                "surveyQuestions": "null",
                "webhookUrl": "https://www.nothing.com/",
                "downloadUrl": "https://ngpvan.blob.core.windows.net/canvass-files-savedlistexport/bf4d1297-1c77-3fb2-03bd-f0acda122d37_2018-09-08T13:03:27.7191831-04:00.csv",  # noqa: E501
                "savedListId": 517612,
                "districtFields": "null",
                "canvassFileRequestGuid": "bf4d1297-1c77-3fb2-03bd-f0acda122d37",
                "customFields": "null",
                "type": 4,
                "exportJobId": 448}

        expected = [
            'status',
            'errorCode',
            'exportJobGuid',
            'activistCodes',
            'canvassFileRequestId',
            'dateExpired',
            'surveyQuestions',
            'webhookUrl',
            'downloadUrl',
            'savedListId',
            'districtFields',
            'canvassFileRequestGuid',
            'customFields',
            'type',
            'exportJobId']

        m.get(self.van.connection.uri + f'exportJobs/{export_job_id}', json=json)

        self.assertEqual(json, self.van.get_export_job(export_job_id))

    @requests_mock.Mocker()
    def test_get_survey_questions(self, m):

        json = {u'count': 67, u'items': [{
            "status": "Active",
            "responses": [
                {"shortName": "1",
                 "surveyResponseId": 1288926,
                 "name": "1-Strong Walz",
                         "mediumName": "1"},
                {"shortName": "2",
                 "surveyResponseId": 1288928,
                 "name": "2-Lean Walz",
                         "mediumName": "2"}],
            "scriptQuestion": "Who do you support for Governor?",
            "name": "MN Governor Gen",
                    "surveyQuestionId": 311838,
                    "mediumName": "MNGovG",
                    "shortName": "MGG",
                    "type": "Candidate",
                    "cycle": 2018
        }],
            u'nextPageLink': None}

        m.get(self.van.connection.uri + 'surveyQuestions', json=json)

        expected = ['status', 'responses', 'scriptQuestion', 'name',
                    'surveyQuestionId', 'mediumName', 'shortName',
                    'type', 'cycle']

        self.assertTrue(validate_list(expected, self.van.get_survey_questions()))

    @requests_mock.Mocker()
    def test_get_supporter_groups(self, m):

        json = {"items": [
            {
                "id": 12,
                "name": "tmc",
                "description": "A fun group."
            },
            {
                "id": 13,
                "name": "tmc",
                "description": "A fun group."
            },
        ],
            "nextPageLink": None,
            "count": 3
        }

        m.get(self.van.connection.uri + 'supporterGroups', json=json)

        expected = ['id', 'name', 'description']

        self.van.get_supporter_groups()

    @requests_mock.Mocker()
    def test_get_supporter_group(self, m):

        json = {"id": 12, "name": "tmc", "description": "A fun group."}
        m.get(self.van.connection.uri + 'supporterGroups/12', json=json)

        # Test that columns are expected columns
        self.assertEqual(self.van.get_supporter_group(12), json)

    @requests_mock.Mocker()
    def test_add_person_supporter_group(self, m):

        # Test good input
        good_supporter_group_id = 5
        good_vanid = 12345
        good_uri = f'supporterGroups/{good_vanid}/people/{good_supporter_group_id}'
        m.put(self.van.connection.uri + good_uri, status_code=204)
        self.van.add_person_supporter_group(good_vanid, good_supporter_group_id)

        # Test bad input
        bad_supporter_group_id = 999
        bad_vanid = 99999
        bad_uri = f'supporterGroups/{bad_vanid}/people/{bad_supporter_group_id}'
        m.put(self.van.connection.uri + bad_uri, status_code=404)
        self.assertRaises(HTTPError, self.van.add_person_supporter_group, bad_vanid, bad_supporter_group_id)

    @requests_mock.Mocker()
    def test_delete_person_supporter_group(self, m):

        # Test good input
        good_supporter_group_id = 5
        good_vanid = 12345
        good_ep = f'supporterGroups/{good_vanid}/people/{good_supporter_group_id}'
        m.delete(self.van.connection.uri + good_ep, status_code=204)
        self.van.delete_person_supporter_group(good_vanid, good_supporter_group_id)

        # Test bad input raises
        bad_supporter_group_id = 999
        bad_vanid = 99999
        bad_ep = f'supporterGroups/{bad_vanid}/people/{bad_supporter_group_id}'
        m.delete(self.van.connection.uri + bad_ep, status_code=404)
        self.assertRaises(HTTPError, self.van.delete_person_supporter_group, bad_vanid, bad_supporter_group_id)

if __name__ == '__main__':

    unittest.main()
