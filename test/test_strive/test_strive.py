import unittest
from parsons import Table, Strive
import os 
import requests_mock
from strive_test_data import mock_member_data
from test.utils import assert_matching_tables
class TestConnector(unittest.TestCase):

    def setUp(self):
        self.api_key = os.environ["STRIVE_SANDBOX_KEY"]
        self.connector = Strive(api_key=self.api_key)
        self.base_uri = "https://api.strivedigital.org"

    def tearDown(self):
        pass

    @requests_mock.Mocker()
    def test_get_members(self, m):
        m.get(self.base_uri + '/members', json=mock_member_data)
        response = self.connector.get_members()
        assert m.called == True  
        assert_matching_tables(response, Table(mock_member_data))
        

        # Want to be sure that Auth header is being passed correctly  
        # PARAMS are being passed through correctly 
        # pass in params and assert that those were passed in correctly 
        # asserting response.params == params, check mock requests documentation 
        # 
        # Live tests
        # Instead of asserting table values 
        # 
        # User validate_list to assert that live tests return right data 
        #  


        
        