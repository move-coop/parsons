import unittest
import os
import requests_mock
from parsons.ngpvan.van import VAN
from parsons.etl.table import Table
from test.utils import assert_matching_tables


class TestNGPVAN(unittest.TestCase):

    def setUp(self):

        self.van = VAN(os.environ['VAN_API_KEY'], db="MyVoters", raise_for_status=False)

    @requests_mock.Mocker()
    def test_get_changed_entity_resources(self, m):

        json = ['ActivistCodes', 'ContactHistory', 'Contacts', 'ContactsActivistCodes']
        m.get(self.van.connection.uri + 'changedEntityExportJobs/resources', json=json)
        self.assertEqual(json, self.van.get_changed_entity_resources())

    @requests_mock.Mocker()
    def test_get_changed_entity_resource_fields(self, m):

        json = [{
            'fieldName': 'ActivistCodeID',
            'fieldType': 'N',
            'maxTextboxCharacters': None,
            'isCoreField': True,
            'availableValues': None
        }, {
            'fieldName': 'ActivistCodeType',
            'fieldType': 'T',
            'maxTextboxCharacters': 20,
            'isCoreField': True,
            'availableValues': None
        }, {
            'fieldName': 'Campaign',
            'fieldType': 'T',
            'maxTextboxCharacters': 150,
            'isCoreField': True,
            'availableValues': None
        }]

        m.get(self.van.connection.uri + 'changedEntityExportJobs/fields/ActivistCodes', json=json)
        assert_matching_tables(
            Table(json), self.van.get_changed_entity_resource_fields('ActivistCodes'))

    @requests_mock.Mocker()
    def get_changed_entities(self, m):

        json = {"dateChangedFrom": "2021-10-10T00:00:00-04:00",
                "dateChangedTo": "2021-10-11T00:00:00-04:00",
                "files": [],
                "message": "Created export job",
                "code": None,
                "exportedRecordCount": 0,
                "exportJobId": 2167849242,
                "jobStatus": "Pending"}

        m.post(self.van.connection.uri + 'changedEntityExportJobs/', json=json)