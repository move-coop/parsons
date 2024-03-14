import unittest
import os
import requests_mock
import unittest.mock as mock
from parsons import VAN, Table
from test.utils import assert_matching_tables


class TestNGPVAN(unittest.TestCase):
    def setUp(self):

        self.van = VAN(os.environ["VAN_API_KEY"], db="MyVoters", raise_for_status=False)

    @requests_mock.Mocker()
    def test_get_changed_entity_resources(self, m):

        json = ["ActivistCodes", "ContactHistory", "Contacts", "ContactsActivistCodes"]
        m.get(self.van.connection.uri + "changedEntityExportJobs/resources", json=json)
        self.assertEqual(json, self.van.get_changed_entity_resources())

    @requests_mock.Mocker()
    def test_get_changed_entity_resource_fields(self, m):

        json = [
            {
                "fieldName": "ActivistCodeID",
                "fieldType": "N",
                "maxTextboxCharacters": None,
                "isCoreField": True,
                "availableValues": None,
            },
            {
                "fieldName": "ActivistCodeType",
                "fieldType": "T",
                "maxTextboxCharacters": 20,
                "isCoreField": True,
                "availableValues": None,
            },
            {
                "fieldName": "Campaign",
                "fieldType": "T",
                "maxTextboxCharacters": 150,
                "isCoreField": True,
                "availableValues": None,
            },
        ]

        m.get(
            self.van.connection.uri + "changedEntityExportJobs/fields/ActivistCodes",
            json=json,
        )
        assert_matching_tables(
            Table(json), self.van.get_changed_entity_resource_fields("ActivistCodes")
        )

    @requests_mock.Mocker()
    def test_get_changed_entities(self, m):

        json = {
            "dateChangedFrom": "2021-10-10T00:00:00-04:00",
            "dateChangedTo": "2021-10-11T00:00:00-04:00",
            "files": [],
            "message": "Created export job",
            "code": None,
            "exportedRecordCount": 0,
            "exportJobId": 2170181229,
            "jobStatus": "Pending",
        }

        json2 = {
            "dateChangedFrom": "2021-10-10T00:00:00-04:00",
            "dateChangedTo": "2021-10-11T00:00:00-04:00",
            "files": [
                {
                    "downloadUrl": "https://box.com/file.csv",
                    "dateExpired": "2021-11-03T15:27:01.8687339-04:00",
                }
            ],
            "message": "Finished processing export job",
            "code": None,
            "exportedRecordCount": 6110,
            "exportJobId": 2170181229,
            "jobStatus": "Complete",
        }

        tbl = Table([{"a": 1, "b": 2}])

        m.post(self.van.connection.uri + "changedEntityExportJobs", json=json)
        m.get(self.van.connection.uri + "changedEntityExportJobs/2170181229", json=json2)

        Table.from_csv = mock.MagicMock()
        Table.from_csv.return_value = tbl

        out_tbl = self.van.get_changed_entities("ContactHistory", "2021-10-10")

        assert_matching_tables(out_tbl, tbl)
