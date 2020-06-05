import unittest
import os
import requests_mock
from parsons.ngpvan import VAN
from test.utils import validate_list, assert_matching_tables

os.environ['VAN_API_KEY'] = 'SOME_KEY'

class TestTargets(unittest.TestCase):

    def setUp(self):

        self.van = VAN(os.environ['VAN_API_KEY'], db="MyVoters", raise_for_status=False)

    def tearDown(self):

        pass

    @requests_mock.Mocker()
    def test_get_targets(self, m):

        # Create response
        json = {u'count': 2, u'items':
                [{u'targetId': 12827,
                  u'type': u'TEST CODE',
                  u'name': u'TEST CODE',
                  u'description': None,
                  u'points': 20,
                  u'areSubgroupsSticky': False,
                  u'status': u'Active',
                  u'subgroups': None,
                  u'markedSubgroup': None}],
                u'nextPageLink': None}

        m.get(self.van.connection.uri + 'targets', json=json)

        # Expected Structure
        expected = ['targetId', 'type', 'name', 'description',
                    'points', 'areSubgroupsSticky', 'status', 'subgroups', 'markedSubgroup']

        # Assert response is expected structure
        self.assertTrue(validate_list(expected, self.van.get_targets()))

        # To Do: Test what happens when it doesn't find any targets

    @requests_mock.Mocker()
    def test_get_target(self, m):

        # Create response
        json = {u'targetId': 15723, 
                u'name': u'Mail_VR_Chase', 
                u'type': u'Dynamic', 
                u'description': None,
                u'points': 15,
                u'areSubgroupsSticky': False,
                u'status': u'Active',
                u'subgroups':
                [{u'targetId': 12827,
                  u'fullName': u'April_VR_Chase Calls',
                  u'name': u'April_Chase_20',
                  u'subgroupId': 46803,
                  u'isAssociatedWithBadges': True}],
                u'markedSubgroup': None}

        m.get(self.van.connection.uri + 'targets/15723', json=json)

        self.assertEqual(json, self.van.get_target(15723))


    @requests_mock.Mocker()
    def test_create_target_export(self, m):

        export_job_id = '{"exportJobId": "455961790"}'
        target_id = 12827

        m.post(self.van.connection.uri + 'targetExportJobs', json=export_job_id, status_code=204)

        # Test that it doesn't throw and error
        r = self.van.create_target_export(target_id, webhook_url=None)

        self.assertEqual(r, export_job_id)


    @requests_mock.Mocker()
    def test_get_target_export(self, m):

        export_job_id = 455961790

        # Create response
        json = [{"targetId": 12827, 
                "file": 
                    {
                    "downloadUrl": "https://ngpvan.blob.core.windows.net/target-export-files/TargetExport_455961790_1_2020-05-26T20:03:44.0530355-04:00.csv",
                    "dateExpired": "null",
                    "recordCount": 1016883
                    }
                ,
                "webhookUrl": "null",
                "exportJobId": 455961790,
                "jobStatus": "Complete"}]

        m.get(self.van.connection.uri + f'targetExportJobs/{export_job_id}', json=json)

        # Expected Structure
        # expected = ['targetId', 'file', 'downloadUrl', 'dateExpired',
        #             'recordCount', 'webhookUrl', 'exportJobId', 'jobStatus']
        # Use shortened expected structure for table columns 
        expected = ['targetId', 'file', 'webhookUrl', 'exportJobId', 'jobStatus']


        # Assert response is expected structure
        self.assertTrue(validate_list(expected, self.van.get_target_export(export_job_id)))
