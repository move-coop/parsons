import unittest
import os
import requests_mock
from parsons.ngpvan.van import VAN
from parsons.etl.table import Table
from test.utils import validate_list, assert_matching_tables

os.environ['VAN_API_KEY'] = 'SOME_KEY'


class TestNGPVAN(unittest.TestCase):

    def setUp(self):

        self.van = VAN(os.environ['VAN_API_KEY'], db="MyVoters", raise_for_status=False)

    def tearDown(self):

        pass

    @requests_mock.Mocker()
    def test_connection(self, m):

        # Create response
        json = {u'message': u'True',
                u'dateSent': u'2018-08-11T15:08:20.1679461Z'}
        m.post(self.van.connection.uri + 'echoes/', json=json)

        # Tests API connection with a key.
        self.assertTrue(self.van.connection.api_test())

    @requests_mock.Mocker()
    def test_get_activist_codes(self, m):

        # Create response
        json = {u'count': 43, u'items':
                [{u'status': u'Active',
                  u'scriptQuestion': None,
                  u'name': u'TEST CODE',
                  u'mediumName': u'TEST CODE',
                  u'activistCodeId': 4388538,
                  u'shortName': u'TC',
                  u'type': u'Action',
                  u'description': None}],
                u'nextPageLink': None}

        m.get(self.van.connection.uri + 'activistCodes', json=json)

        # Expected Structure
        expected = ['status', 'scriptQuestion', 'name', 'mediumName',
                    'activistCodeId', 'shortName', 'type', 'description']

        # Assert response is expected structure
        self.assertTrue(validate_list(expected, self.van.get_activist_codes()))

        # To Do: Test what happens when it doesn't find any ACs

    @requests_mock.Mocker()
    def test_get_activist_code(self, m):

        # Create response
        json = {"status": "Active",
                "scriptQuestion": "null",
                "name": "Anti-Choice",
                "mediumName": "Anti",
                "activistCodeId": 4135099,
                "shortName": "AC",
                "type": "Constituency",
                "description": "A person who has been flagged as anti-choice."}

        m.get(self.van.connection.uri + 'activistCodes/4388538', json=json)

        self.assertEqual(json, self.van.get_activist_code(4388538))

        # To Do: Test what happens when it doesn't find the AC

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

        m.post(self.van.connection.uri + 'exportJobs', json=json)

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

        good_supporter_group_id = 5
        good_vanid = 12345

        bad_supporter_group_id = 999
        bad_vanid = 99999

        good_ep = 'supporterGroups/{}/people/{}'.format(good_vanid, good_supporter_group_id)

        m.put(self.van.connection.uri + good_ep, status_code=204)

        bad_ep = 'supporterGroups/{}/people/{}'.format(bad_vanid, bad_supporter_group_id)

        m.put(self.van.connection.uri + bad_ep, status_code=404)

        # Test bad input
        self.assertEqual(self.van.add_person_supporter_group(bad_vanid, bad_supporter_group_id)[0], 404)

        # Test good input
        self.assertEqual(self.van.add_person_supporter_group(good_vanid, good_supporter_group_id)[0], 204)

    @requests_mock.Mocker()
    def test_delete_person_supporter_group(self, m):

        good_supporter_group_id = 5
        good_vanid = 12345

        bad_supporter_group_id = 999
        bad_vanid = 99999

        good_ep = 'supporterGroups/{}/people/{}'.format(good_vanid, good_supporter_group_id)

        m.delete(self.van.connection.uri + good_ep, status_code=204)

        bad_ep = 'supporterGroups/{}/people/{}'.format(bad_vanid, bad_supporter_group_id)

        m.delete(self.van.connection.uri + bad_ep, status_code=404)

        # Test bad input
        self.assertEqual(self.van.delete_person_supporter_group(bad_vanid, bad_supporter_group_id)[0], 404)

        # Test good input
        self.assertEqual(self.van.delete_person_supporter_group(good_vanid, good_supporter_group_id)[0], 204)

    @requests_mock.Mocker()
    def test_get_scores(self, m):

        json = {u'count': 2, u'items':
                [{u'origin': None,
                  u'scoreId': 2716,
                  u'name': u'Democratic Party Support',
                  u'maxValue': 100.0,
                  u'minValue': 1.0,
                  u'state': None,
                  u'shortName': u'Dem Support',
                  u'description': None}],
                u'nextPageLink': None}

        m.get(self.van.connection.uri + 'scores', json=json)

        expected = ['origin', 'scoreId', 'name', 'maxValue', 'minValue',
                    'state', 'shortName', 'description']

        self.assertTrue(validate_list(expected, self.van.get_scores()))

    @requests_mock.Mocker()
    def test_get_score(self, m):

        score_id = 2716

        json = {u'origin': None,
                u'scoreId': 2716,
                u'name': u'Democratic Party Support',
                u'maxValue': 100.0,
                u'minValue': 1.0,
                u'state': None,
                u'shortName': u'Dem Support',
                u'description': None}

        m.get(self.van.connection.uri + 'scores/{}'.format(score_id), json=json)
        self.assertEqual(json, self.van.get_score(score_id))

    @requests_mock.Mocker()
    def test_get_score_updates(self, m):

        json = {'items': [{
                'scoreUpdateId': 58319,
                'score': {
                  'scoreId': 29817,
                  'name': 'TargetSmart Gun Ownership',
                  'shortName': None,
                  'description': None,
                  'minValue': 0.0,
                  'maxValue': 100.0,
                  'state': 'MT',
                  'origin': None
                },
                'updateStatistics': {
                  'totalRows': 856644,
                  'duplicateRows': 0,
                  'matchedRows': 856644,
                  'matchPercent': 100.0,
                  'increasedBy': 441264,
                  'decreasedBy': 280588,
                  'nulledOut': 3649,
                  'added': 115129,
                  'outOfRange': 0,
                  'badValues': 0,
                  'maxValue': 95.9,
                  'minValue': 11.2,
                  'averageValue': 72.3338,
                  'medianValue': 76.3
                },
                'loadStatus': 'Completed',
                'dateProcessed': '2019-09-10T02:07:00Z'
              }],
              'nextPageLink': None,
              'count': 306
            }

        m.get(self.van.connection.uri + 'scoreUpdates', json=json)

        expected = ['scoreUpdateId', 'loadStatus', 'dateProcessed', 'added', 'averageValue',
                    'badValues', 'decreasedBy', 'duplicateRows', 'increasedBy', 'matchPercent',
                    'matchedRows', 'maxValue', 'medianValue', 'minValue', 'nulledOut',
                    'outOfRange', 'totalRows', 'description', 'maxValue', 'minValue', 'name',
                    'origin', 'scoreId', 'shortName', 'state']

        self.assertTrue(validate_list(expected, self.van.get_score_updates()))

    @requests_mock.Mocker()
    def test_get_score_update(self, m):

        score_update_id = 27892

        json = {
            "loadStatus": "Canceled",
            "updateStatistics": {
                "increasedBy": 1,
                "nulledOut": 1,
                "added": 0,
                "matchedRows": 4,
                "matchPercent": 100.0,
                "outOfRange": 0,
                "badValues": 1,
                "totalRows": 4,
                "maxValue": 30.0,
                "medianValue": 15.0,
                "minValue": 10.0,
                "duplicateRows": "null",
                "averageValue": 20.0,
                "decreasedBy": 2
            },
            "score": {
                "origin": "null",
                "scoreId": 2716,
                "name": "Democratic Party Support",
                        "maxValue": 100.0,
                        "minValue": 1.0,
                        "state": "null",
                        "shortName": "null",
                        "description": "null"
            },
            "dateProcessed": "null",
            "scoreUpdateId": 27892
        }

        m.get(self.van.connection.uri + f'scoreUpdates/{score_update_id}', json=json)

        expected = ['loadStatus', 'updateStatistics', 'score', 'dateProcessed', 'scoreUpdateId']

        self.assertEqual(json, self.van.get_score_update(score_update_id))

    @requests_mock.Mocker()
    def test_update_score_status(self, m):

        score_update_id = 27892

        m.patch(self.van.connection.uri + 'scoreUpdates/{}'.format(score_update_id),
                status_code=204)

        # Test bad input
        self.assertRaises(ValueError, self.van.update_score_status, score_update_id, 'not a thing.')

        # Test good input
        self.assertTrue(self.van.update_score_status(score_update_id, 'approved'))

    @requests_mock.Mocker()
    def test_create_file_load(self, m):

        file_name = 'test_scores.csv'
        file_url_good = 'http://tmc.org/test_scores.zip'
        file_url_bad = 'http://tmc.org/test_scores'
        columns = ['vanid', 'score']
        id_column = 'vanid'
        id_type = 'VANID'
        score_id = 2716
        score_column = 'score'
        bad_delimiter = '*'

        json = {'jobId': 9749}

        m.post(self.van.connection.uri + 'FileLoadingJobs', json=json)

        # Test bad delimiter
        self.assertRaises(ValueError, self.van.create_file_load, file_name, file_url_good, columns,
                          id_column, id_type, score_id, score_column, delimiter=bad_delimiter)

        # Test good request
        self.assertEqual(json['jobId'], self.van.create_file_load(file_name, file_url_good, columns,
                                                                  id_column, id_type, score_id,
                                                                  score_column))

    # TO DO: Test Volunteer Activites


if __name__ == '__main__':

    unittest.main()
