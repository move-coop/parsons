import os
import unittest

import requests_mock

from parsons import VAN
from test.conftest import validate_list


class TestSavedLists(unittest.TestCase):
    def setUp(self):
        self.van = VAN(os.environ["VAN_API_KEY"], db="MyVoters")

    def tearDown(self):
        pass

    @requests_mock.Mocker()
    def test_get_saved_lists(self, m):
        json = {
            "count": 1,
            "items": [
                {
                    "savedListId": 517612,
                    "listCount": 974656,
                    "name": "LikelyParents(16andunder)_DWID_S... - MN",
                    "doorCount": 520709,
                    "description": "null",
                }
            ],
            "nextPageLink": None,
        }

        m.get(self.van.connection.uri + "savedLists", json=json)

        expected = ["savedListId", "listCount", "name", "doorCount", "description"]

        assert validate_list(expected, self.van.get_saved_lists())

    @requests_mock.Mocker()
    def test_get_saved_list(self, m):
        saved_list_id = 517612

        json = {
            "savedListId": 517612,
            "listCount": 974656,
            "name": "LikelyParents(16andunder)_DWID_S... - MN",
            "doorCount": 520709,
            "description": "null",
        }

        m.get(self.van.connection.uri + f"savedLists/{saved_list_id}", json=json)

        # expected = ['savedListId', 'listCount', 'name', 'doorCount', 'description']

        assert self.van.get_saved_list(saved_list_id) == json

    @requests_mock.Mocker()
    def test_get_folders(self, m):
        json = {
            "count": 2,
            "items": [
                {"folderId": 5046, "name": "#2018_MN_active_universe"},
                {"folderId": 2168, "name": "API Generated Lists"},
            ],
            "nextPageLink": None,
        }

        m.get(self.van.connection.uri + "folders", json=json)

        expected = ["folderId", "name"]

        assert validate_list(expected, self.van.get_folders())

    @requests_mock.Mocker()
    def test_get_folder(self, m):
        folder_id = 5046

        json = {"folderId": 5046, "name": "#2018_MN_active_universe"}

        m.get(self.van.connection.uri + f"folders/{folder_id}", json=json)

        assert json == self.van.get_folder(folder_id)

    @requests_mock.Mocker()
    def test_export_job_types(self, m):
        json = {
            "count": 1,
            "items": [{"exportJobTypeId": 4, "name": "SavedListExport"}],
            "nextPageLink": None,
        }

        m.get(self.van.connection.uri + "exportJobTypes", json=json)

        expected = ["exportJobTypeId", "name"]

        assert validate_list(expected, self.van.get_export_job_types())

    @requests_mock.Mocker()
    def test_export_job_create(self, m):
        saved_list_id = 517612

        json = {
            "status": "Completed",
            "errorCode": "null",
            "exportJobGuid": "bf4d1297-1c77-3fb2-03bd-f0acda122d37",
            "activistCodes": "null",
            "canvassFileRequestId": 448,
            "dateExpired": "2018-09-08T16:04:00Z",
            "surveyQuestions": "null",
            "webhookUrl": "https://www.nothing.com/",
            "downloadUrl": "https://ngpvan.blob.core.windows.net/canvass-files-savedlistexport/bf4d1297-1c77-3fb2-03bd-f0acda122d37_2018-09-08T13:03:27.7191831-04:00.csv",
            "savedListId": 517612,
            "districtFields": "null",
            "canvassFileRequestGuid": "bf4d1297-1c77-3fb2-03bd-f0acda122d37",
            "customFields": "null",
            "type": 4,
            "exportJobId": 448,
        }

        m.post(self.van.connection.uri + "exportJobs", json=json, status_code=201)

        # expected = [
        #     'status',
        #     'errorCode',
        #     'exportJobGuid',
        #     'activistCodes',
        #     'canvassFileRequestId',
        #     'dateExpired',
        #     'surveyQuestions',
        #     'webhookUrl',
        #     'downloadUrl',
        #     'savedListId',
        #     'districtFields',
        #     'canvassFileRequestGuid',
        #     'customFields',
        #     'type',
        #     'exportJobId']

        assert json == self.van.export_job_create(saved_list_id)

    @requests_mock.Mocker()
    def test_get_export_job(self, m):
        export_job_id = 448

        json = {
            "status": "Completed",
            "errorCode": "null",
            "exportJobGuid": "bf4d1297-1c77-3fb2-03bd-f0acda122d37",
            "activistCodes": "null",
            "canvassFileRequestId": 448,
            "dateExpired": "2018-09-08T16:04:00Z",
            "surveyQuestions": "null",
            "webhookUrl": "https://www.nothing.com/",
            "downloadUrl": "https://ngpvan.blob.core.windows.net/canvass-files-savedlistexport/bf4d1297-1c77-3fb2-03bd-f0acda122d37_2018-09-08T13:03:27.7191831-04:00.csv",
            "savedListId": 517612,
            "districtFields": "null",
            "canvassFileRequestGuid": "bf4d1297-1c77-3fb2-03bd-f0acda122d37",
            "customFields": "null",
            "type": 4,
            "exportJobId": 448,
        }

        # expected = [
        #     'status',
        #     'errorCode',
        #     'exportJobGuid',
        #     'activistCodes',
        #     'canvassFileRequestId',
        #     'dateExpired',
        #     'surveyQuestions',
        #     'webhookUrl',
        #     'downloadUrl',
        #     'savedListId',
        #     'districtFields',
        #     'canvassFileRequestGuid',
        #     'customFields',
        #     'type',
        #     'exportJobId']

        m.get(self.van.connection.uri + f"exportJobs/{export_job_id}", json=json)

        assert json == self.van.get_export_job(export_job_id)
