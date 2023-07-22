import unittest
from parsons.utilities.api_connector import APIConnector
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
        history = m.request_history[0] # Get the first (and only) request made
        # Assert that a get request was made
        self.assertEqual(history.method, 'GET')
        # Assert mock object has been called
        assert m.called == True  
        # Assert mock data was successfully passed and retrieved 
        assert_matching_tables(response, Table(mock_member_data))
        # Assert headers passed correctly 
        assert f"Bearer {self.api_key}" == history.headers.get("Authorization")

        
    
        # Define the data to be returned by the mock request
        m.get(self.base_uri + '/members', json=mock_member_data)        
        # Call the function that makes the HTTP request (replace get_members with the actual function name)
        response = self.connector.get_members(first_name='eq.brittany', city='eq.Pittsburgh')
        import pytest; pytest.set_trace()
        history = m.request_history[0]
        assert history.qs == {'first_name':'eq.brittany', 'city': 'eq.Pittsburgh'}







      


        
        