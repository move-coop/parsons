import unittest
import os
import requests_mock
from parsons.ngpvan.van import VAN

os.environ['VAN_API_KEY'] = 'SOME_KEY'


class TestBulkImport(unittest.TestCase):

    def setUp(self):

        self.van = VAN(os.environ['VAN_API_KEY'], db="MyVoters", raise_for_status=False)

    def tearDown(self):

        pass

    @requests_mock.Mocker()
    def test_get_bulk_import_resources(self, m):

        json = ['Contacts', 'Contributions', 'ActivistCodes', 'ContactsActivistCodes']

        m.get(self.van.connection.uri + 'bulkImportJobs/resources', json=json)

        self.assertEqual(self.van.get_bulk_import_resources(), json)
