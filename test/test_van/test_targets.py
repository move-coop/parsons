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

