from parsons import VAN, Table
from parsons.utilities import cloud_storage
from test.conftest import validate_list


def test_get_saved_lists(van: VAN, requests_mock):
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

    requests_mock.get(van.connection.uri + "savedLists", json=json)

    expected = ["savedListId", "listCount", "name", "doorCount", "description"]

    assert validate_list(expected, van.get_saved_lists())


def test_get_saved_list(van: VAN, requests_mock):
    saved_list_id = 517612

    json = {
        "savedListId": 517612,
        "listCount": 974656,
        "name": "LikelyParents(16andunder)_DWID_S... - MN",
        "doorCount": 520709,
        "description": "null",
    }

    requests_mock.get(van.connection.uri + f"savedLists/{saved_list_id}", json=json)

    # expected = ['savedListId', 'listCount', 'name', 'doorCount', 'description']

    assert van.get_saved_list(saved_list_id) == json


def test_upload_saved_list(van: VAN, mocker):
    post_file = mocker.patch.object(cloud_storage, "post_file")
    post_file.return_value = "https://box.com/my_file.zip"

    van.connection._soap_client = mocker.MagicMock()
    van.get_folders = mocker.MagicMock()
    van.get_folders.return_value = [{"folderId": 1}]

    tbl = Table([["VANID"], ["1"], ["2"], ["3"]])
    van.upload_saved_list(tbl, "GOTV List", 1, replace=True, url_type="S3", bucket="tmc-scratch")
    assert van.connection._soap_client.service.CreateAndStoreSavedList.called


def test_upload_saved_list_rest(van: VAN, requests_mock, mocker):
    post_file = mocker.patch.object(cloud_storage, "post_file")
    post_file.return_value = "https://box.com/my_file.zip"

    van.get_folders = mocker.MagicMock()
    van.get_folders.return_value = [{"folderId": 1}]
    van.get_saved_lists = mocker.MagicMock()
    van.get_saved_lists.return_value = []

    requests_mock.post(van.connection.uri + "fileLoadingJobs", json={"jobId": 54679})

    tbl = Table([["VANID"], ["1"], ["2"], ["3"]])
    response = van.upload_saved_list_rest(
        tbl=tbl,
        url_type="S3",
        folder_id=1,
        list_name="GOTV List",
        description="parsons test list",
        callback_url="https://webhook.site/69ab58c3-a3a7-4ed8-828c-1ea850cb4160",
        columns=["VANID"],
        id_column="VANID",
        bucket="tmc-scratch",
        overwrite=517612,
    )
    assert "jobId" in response


def test_get_folders(van: VAN, requests_mock):
    json = {
        "count": 2,
        "items": [
            {"folderId": 5046, "name": "#2018_MN_active_universe"},
            {"folderId": 2168, "name": "API Generated Lists"},
        ],
        "nextPageLink": None,
    }

    requests_mock.get(van.connection.uri + "folders", json=json)

    expected = ["folderId", "name"]

    assert validate_list(expected, van.get_folders())


def test_get_folder(van: VAN, requests_mock):
    folder_id = 5046

    json = {"folderId": 5046, "name": "#2018_MN_active_universe"}

    requests_mock.get(van.connection.uri + f"folders/{folder_id}", json=json)

    assert json == van.get_folder(folder_id)


def test_export_job_types(van: VAN, requests_mock):
    json = {
        "count": 1,
        "items": [{"exportJobTypeId": 4, "name": "SavedListExport"}],
        "nextPageLink": None,
    }

    requests_mock.get(van.connection.uri + "exportJobTypes", json=json)

    expected = ["exportJobTypeId", "name"]

    assert validate_list(expected, van.get_export_job_types())


def test_export_job_create(van: VAN, requests_mock):
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

    requests_mock.post(van.connection.uri + "exportJobs", json=json, status_code=201)

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

    assert json == van.export_job_create(saved_list_id)


def test_get_export_job(van: VAN, requests_mock):
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

    requests_mock.get(van.connection.uri + f"exportJobs/{export_job_id}", json=json)

    assert json == van.get_export_job(export_job_id)
