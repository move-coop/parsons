import unittest
import os
import requests_mock
import unittest.mock as mock
from parsons import VAN, Table
from test.utils import validate_list
from parsons.utilities import cloud_storage


os.environ["VAN_API_KEY"] = "SOME_KEY"


class TestScores(unittest.TestCase):
    def setUp(self):

        self.van = VAN(os.environ["VAN_API_KEY"], db="MyVoters", raise_for_status=False)

    @requests_mock.Mocker()
    def test_get_scores(self, m):

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

        m.get(self.van.connection.uri + "scores", json=json)

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

        self.assertTrue(validate_list(expected, self.van.get_scores()))

    @requests_mock.Mocker()
    def test_get_score(self, m):

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

        m.get(self.van.connection.uri + "scores/{}".format(score_id), json=json)
        self.assertEqual(json, self.van.get_score(score_id))

    @requests_mock.Mocker()
    def test_get_score_updates(self, m):

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

        m.get(self.van.connection.uri + "scoreUpdates", json=json)

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

        m.get(self.van.connection.uri + f"scoreUpdates/{score_update_id}", json=json)

        # expected = ['loadStatus', 'updateStatistics', 'score', 'dateProcessed', 'scoreUpdateId']

        self.assertEqual(json, self.van.get_score_update(score_update_id))

    @requests_mock.Mocker()
    def test_update_score_status(self, m):

        score_update_id = 27892

        m.patch(
            self.van.connection.uri + "scoreUpdates/{}".format(score_update_id),
            status_code=204,
        )

        # Test bad input
        self.assertRaises(ValueError, self.van.update_score_status, score_update_id, "not a thing.")

        # Test good input
        self.assertTrue(self.van.update_score_status(score_update_id, "approved"))

    @requests_mock.Mocker()
    def test_upload_scores(self, m):

        # Mock Cloud Storage
        cloud_storage.post_file = mock.MagicMock()
        cloud_storage.post_file.return_value = "https://box.com/my_file.zip"

        # Test uploading a job
        tbl = Table([["vanid", "col"], ["1", ".5"]])
        json = {"jobId": 9749}
        m.post(self.van.connection.uri + "FileLoadingJobs", json=json, status_code=201)
        self.van.upload_scores(tbl, [{"score_id": 9999, "score_column": "col"}], url_type="S3")

    @requests_mock.Mocker()
    def test_create_file_load(self, m):

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

        m.post(self.van.connection.uri + "FileLoadingJobs", json=json, status_code=201)

        # Test bad delimiter
        self.assertRaises(
            ValueError,
            self.van.create_file_load,
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
        self.assertEqual(
            json["jobId"],
            self.van.create_file_load(
                file_name,
                file_url_good,
                columns,
                id_column,
                id_type,
                score_id,
                score_column,
            ),
        )
