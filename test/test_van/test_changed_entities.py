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
