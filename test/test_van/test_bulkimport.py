import unittest
import os
import requests_mock
from parsons.ngpvan.van import VAN
from parsons.etl.table import Table
from test.utils import assert_matching_tables

os.environ['VAN_API_KEY'] = 'SOME_KEY'


class TestBulkImport(unittest.TestCase):

    def setUp(self):

        self.van = VAN(os.environ['VAN_API_KEY'],
                       db="MyVoters", raise_for_status=False)

    def tearDown(self):

        pass

    @requests_mock.Mocker()
    def test_get_bulk_import_resources(self, m):

        json = ['Contacts', 'Contributions',
                'ActivistCodes', 'ContactsActivistCodes']

        m.get(self.van.connection.uri + 'bulkImportJobs/resources', json=json)

        self.assertEqual(self.van.get_bulk_import_resources(), json)

    @requests_mock.Mocker()
    def test_get_bulk_import_job(self, m):

        json = {'id': 59,
                'status': 'InProgress',
                'resourceType': 'ContactsActivistCodes',
                'webhookUrl': None,
                'resultFileSizeLimitKb': 5000,
                'errors': [],
                'resultFiles': []}

        m.get(self.van.connection.uri + 'bulkImportJobs/53407', json=json)

        self.assertEqual(self.van.get_bulk_import_job(53407), json)

    @requests_mock.Mocker()
    def test_get_bulk_import_mapping_types(self, m):

        json = {'name': 'ActivistCode',
                'displayName': 'Apply Activist Code',
                'allowMultipleMode': 'Multiple',
                'resourceTypes': ['Contacts', 'ContactsActivistCodes'],
                'fields': [{
                    'name': 'ActivistCodeID',
                    'description': 'Activist Code ID',
                    'hasPredefinedValues': True,
                    'isRequired': True,
                    'canBeMappedToColumn': True,
                    'canBeMappedByName': True,
                    'parents': None},
                    {'name': 'CanvassedBy',
                     'description': 'Recruited By, Must be a Valid User ID',
                     'hasPredefinedValues': False,
                     'isRequired': False,
                     'canBeMappedToColumn': True,
                     'canBeMappedByName': True,
                     'parents': None},
                    {'name': 'DateCanvassed',
                     'description': 'Contacted When',
                     'hasPredefinedValues': False,
                     'isRequired': False,
                     'canBeMappedToColumn': True,
                     'canBeMappedByName': True,
                     'parents': [{
                         'parentFieldName': 'CanvassedBy',
                         'limitedToParentValues': None
                     }]
                     }, {
                    'name': 'ContactTypeID',
                    'description': 'Contacted How',
                    'hasPredefinedValues': True,
                    'isRequired': False,
                    'canBeMappedToColumn': True,
                    'canBeMappedByName': True,
                    'parents': [{
                        'parentFieldName': 'CanvassedBy',
                        'limitedToParentValues': None
                    }]
                }]
                }

        m.get(self.van.connection.uri + 'bulkImportMappingTypes', json=json)

        assert_matching_tables(self.van.get_bulk_import_mapping_types(), Table(json))
