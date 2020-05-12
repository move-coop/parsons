import unittest
import os
import requests_mock
from parsons.ngpvan import VAN
from test.utils import validate_list, assert_matching_tables

os.environ['VAN_API_KEY'] = 'SOME_KEY'

class TestTargetExport(unittest.TestCase):

    def setUp(self):

        self.van = VAN(os.environ['VAN_API_KEY'], db="MyVoters", raise_for_status=False)

    def tearDown(self):

        pass


    @requests_mock.Mocker()
    def test_create_target_export(self, m):

        export_job_id = 1234
        target_id = 15723

        m.post(self.van.connection.uri + 'targetExportJobs', json=export_job_id, status_code=204)

        # Test that it doesn't throw and error
        r = self.van.create_target_export(target_id, webhook_url=None)

        self.assertEqual(r, export_job_id)


    @requests_mock.Mocker()
    def test_get_target_export(self, m):

        # Create response
        json = {u'targetId': 15723, 
                u'file':
                [{u'downloadUrl': u'https://www.example.com/some-unique-file-name.csv',
                  u'dateExpired': u'2020-04-07T09:45:51.4954493-04:00',
                  u'recordCount': 8}],
                u'webhookUrl': u'https://webhook.example.org/completedExportJobs',
                u'exportJobId': 1234,
                u'jobStatus': "Complete"}

        m.get(self.van.connection.uri + 'targetExportJobs', json=json)

        # Expected Structure
        expected = ['targetId', 'file', 'downloadUrl', 'dateExpired',
                    'recordCount', 'webhookUrl', 'exportJobId', 'jobStatus']

        export_job_id = 1234

        # Assert response is expected structure
        self.assertTrue(validate_list(expected, self.van.get_target_export(export_job_id)))

