import pytest

from parsons import VAN, Table
from parsons.utilities import cloud_storage
from test.conftest import validate_list


def test_get_scores(van: VAN, requests_mock):
    json = {
        "count": 2,
        "items": [
            {
                "origin": None,
                "scoreId": 2716,
                "name": "Democratic Party Support",
                "maxValue": 100.0,
                "minValue": 1.0,
                "state": None,
                "shortName": "Dem Support",
                "description": None,
            }
        ],
        "nextPageLink": None,
    }

    requests_mock.get(van.connection.uri + "scores", json=json)

    expected = [
        "origin",
        "scoreId",
        "name",
        "maxValue",
        "minValue",
        "state",
        "shortName",
        "description",
    ]

    assert validate_list(expected, van.get_scores())


def test_get_score(van: VAN, requests_mock):
    score_id = 2716

    json = {
        "origin": None,
        "scoreId": 2716,
        "name": "Democratic Party Support",
        "maxValue": 100.0,
        "minValue": 1.0,
        "state": None,
        "shortName": "Dem Support",
        "description": None,
    }

    requests_mock.get(van.connection.uri + f"scores/{score_id}", json=json)
    assert json == van.get_score(score_id)


def test_get_score_updates(van: VAN, requests_mock):
    json = {
        "items": [
            {
                "scoreUpdateId": 58319,
                "score": {
                    "scoreId": 29817,
                    "name": "TargetSmart Gun Ownership",
                    "shortName": None,
                    "description": None,
                    "minValue": 0.0,
                    "maxValue": 100.0,
                    "state": "MT",
                    "origin": None,
                },
                "updateStatistics": {
                    "totalRows": 856644,
                    "duplicateRows": 0,
                    "matchedRows": 856644,
                    "matchPercent": 100.0,
                    "increasedBy": 441264,
                    "decreasedBy": 280588,
                    "nulledOut": 3649,
                    "added": 115129,
                    "outOfRange": 0,
                    "badValues": 0,
                    "maxValue": 95.9,
                    "minValue": 11.2,
                    "averageValue": 72.3338,
                    "medianValue": 76.3,
                },
                "loadStatus": "Completed",
                "dateProcessed": "2019-09-10T02:07:00Z",
            }
        ],
        "nextPageLink": None,
        "count": 306,
    }

    requests_mock.get(van.connection.uri + "scoreUpdates", json=json)

    expected = [
        "scoreUpdateId",
        "loadStatus",
        "dateProcessed",
        "added",
        "averageValue",
        "badValues",
        "decreasedBy",
        "duplicateRows",
        "increasedBy",
        "matchPercent",
        "matchedRows",
        "maxValue",
        "medianValue",
        "minValue",
        "nulledOut",
        "outOfRange",
        "totalRows",
        "description",
        "maxValue",
        "minValue",
        "name",
        "origin",
        "scoreId",
        "shortName",
        "state",
    ]

    assert validate_list(expected, van.get_score_updates())


def test_get_score_update(van: VAN, requests_mock):
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
            "decreasedBy": 2,
        },
        "score": {
            "origin": "null",
            "scoreId": 2716,
            "name": "Democratic Party Support",
            "maxValue": 100.0,
            "minValue": 1.0,
            "state": "null",
            "shortName": "null",
            "description": "null",
        },
        "dateProcessed": "null",
        "scoreUpdateId": 27892,
    }

    requests_mock.get(van.connection.uri + f"scoreUpdates/{score_update_id}", json=json)

    # expected = ['loadStatus', 'updateStatistics', 'score', 'dateProcessed', 'scoreUpdateId']

    assert json == van.get_score_update(score_update_id)


def test_update_score_status(van: VAN, requests_mock):
    score_update_id = 27892

    requests_mock.patch(
        van.connection.uri + f"scoreUpdates/{score_update_id}",
        status_code=204,
    )

    # Test bad input
    with pytest.raises(
        ValueError,
        match="Valid inputs for status are, 'pending approval','approved','disapproved','canceled'",
    ):
        van.update_score_status(score_update_id, "not a thing.")

    # Test good input
    assert van.update_score_status(score_update_id, "approved")


def test_upload_scores(van: VAN, requests_mock, mocker):
    # Mock Cloud Storage
    post_file = mocker.patch.object(cloud_storage, "post_file")
    post_file.return_value = "https://box.com/my_file.zip"

    # Test uploading a job
    tbl = Table([["vanid", "col"], ["1", ".5"]])
    json = {"jobId": 9749}
    requests_mock.post(van.connection.uri + "FileLoadingJobs", json=json, status_code=201)
    van.upload_scores(tbl, [{"score_id": 9999, "score_column": "col"}], url_type="S3")


def test_create_file_load(van: VAN, requests_mock):
    file_name = "test_scores.csv"
    file_url_good = "http://tmc.org/test_scores.zip"
    # file_url_bad = 'http://tmc.org/test_scores'
    columns = ["vanid", "score"]
    id_column = "vanid"
    id_type = "VANID"
    score_id = 2716
    score_column = "score"
    bad_delimiter = "*"

    json = {"jobId": 9749}

    requests_mock.post(van.connection.uri + "FileLoadingJobs", json=json, status_code=201)

    # Test bad delimiter
    with pytest.raises(ValueError, match="Delimiter must be one of 'csv', 'tab' or 'pipe'"):
        van.create_file_load(
            file_name,
            file_url_good,
            columns,
            id_column,
            id_type,
            score_id,
            score_column,
            delimiter=bad_delimiter,
        )

    # Test good request
    assert json["jobId"] == van.create_file_load(
        file_name, file_url_good, columns, id_column, id_type, score_id, score_column
    )
