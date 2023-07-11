import unittest
from parsons import Table, Connector
import os 
import requests_mock
from strive_test_data import mock_member_data
class TestConnector(unittest.TestCase):

    def setUp(self):
        self.api_key = os.environ["STRIVE_KEY"]
        self.connector = Connector(api_key=self.api_key)

    def tearDown(self):
        pass
    
    @requests_mock.Mocker()
    def test_get_members(self, m):
        m.get(self.base_uri + '/members', json=mock_member_data)
        result = self.connector.get_members(params={'first_name' : 'brittany'})


        # want to make sure that each of the functions being called is
        # using the correct URL

        # Want to be sure that Auth is being sent in the header 

        # PARAMS are being passed through correctly 
        # want to assert proper auth
        # want to assert structure of request 

        # What happens if you don't have the correct environment variables 
        # if you don't have an API key 

        # have the same test per function -- fail if the URLs ont heir end change 

        
        