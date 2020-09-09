import unittest
import os
import requests_mock
import unittest.mock as mock
from parsons.ngpvan.van import VAN
from parsons.etl.table import Table
from test.utils import assert_matching_tables
from parsons.utilities import cloud_storage

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

        m.get(self.van.connection.uri + 'bulkImportMappingTypes', json=mapping_type)

        assert_matching_tables(self.van.get_bulk_import_mapping_types(), Table(mapping_type))

    @requests_mock.Mocker()
    def test_get_bulk_import_mapping_type(self, m):

        m.get(self.van.connection.uri + 'bulkImportMappingTypes/ActivistCode', json=mapping_type)

        self.assertEqual(self.van.get_bulk_import_mapping_type('ActivistCode'), mapping_type)

    @requests_mock.Mocker()
    def test_post_bulk_import(self, m):

        # Mock Cloud Storage
        cloud_storage.post_file = mock.MagicMock()
        cloud_storage.post_file.return_value = 'https://s3.com/my_file.zip'

        tbl = Table([['Vanid', 'ActivistCodeID'], [1234, 345345]])

        m.post(self.van.connection.uri + 'bulkImportJobs', json={'jobId': 54679})

        r = self.van.post_bulk_import(tbl,
                                      'S3',
                                      'ContactsActivistCodes',
                                      [{"name": "ActivistCode"}],
                                      'Activist Code Upload',
                                      bucket='my-bucket')

        self.assertEqual(r, 54679)

    @requests_mock.Mocker()
    def test_bulk_apply_activist_codes(self, m):

        # Mock Cloud Storage
        cloud_storage.post_file = mock.MagicMock()
        cloud_storage.post_file.return_value = 'https://s3.com/my_file.zip'

        tbl = Table([['Vanid', 'ActivistCodeID'], [1234, 345345]])

        m.post(self.van.connection.uri + 'bulkImportJobs', json={'jobId': 54679})

        job_id = self.van.bulk_apply_activist_codes(tbl, url_type="S3", bucket='my-bucket')

        self.assertEqual(job_id, 54679)


mapping_type = {
    'name': 'ActivistCode',
    'displayName': 'Apply Activist Code',
    'allowMultipleMode': 'Multiple',
    'resourceTypes': ['Contacts', 'ContactsActivistCodes'],
    'fields': [
        {
            'name': 'ActivistCodeID',
            'description': 'Activist Code ID',
            'hasPredefinedValues': True,
            'isRequired': True,
            'canBeMappedToColumn': True,
            'canBeMappedByName': True,
            'parents': None
        }, {
            'name': 'CanvassedBy',
            'description': 'Recruited By, Must be a Valid User ID',
            'hasPredefinedValues': False,
            'isRequired': False,
            'canBeMappedToColumn': True,
            'canBeMappedByName': True,
            'parents': None
        }, {
            'name': 'DateCanvassed',
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
        }
    ]
}
