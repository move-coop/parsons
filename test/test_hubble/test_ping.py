import unittest
import os
import requests_mock
import unittest.mock as mock
from parsons import Hubble, Table
from test.utils import validate_list
from parsons.utilities import cloud_storage

os.environ['VAN_API_KEY'] = 'SOME_KEY'

class TestScores(unittest.TestCase):

    def setUp(self):

        self.hubble = Hubble(os.environ['VAN_API_KEY'], db="MyVoters", raise_for_status=False)

    @requests_mock.Mocker()
    def test_get_score(self, m):

        score_id = 2716

        json = {u'origin': None,
                u'scoreId': 2716,
                u'name': u'Democratic Party Support',
                u'maxValue': 100.0,
                u'minValue': 1.0,
                u'state': None,
                u'shortName': u'Dem Support',
                u'description': None}

        m.get(self.van.connection.uri + 'scores/{}'.format(score_id), json=json)
        self.assertEqual(json, self.van.get_score(score_id))
