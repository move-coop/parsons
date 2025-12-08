import unittest
from parsons.utilities.api_connector import APIConnector
from parsons import Table, Strive
import os 
import requests_mock
from strive_test_data import mock_member_data
from test.utils import assert_matching_tables
from test.utils import mark_live_test
import pandas as pd
import json

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
        history = m.request_history[0] # Get the first request made
        # Assert that a get request was made
        self.assertEqual(history.method, 'GET')
        # Assert mock object has been called
        assert m.called == True  
        # Assert mock data was successfully passed and retrieved 
        assert_matching_tables(response, Table(mock_member_data))
        # Assert headers passed correctly 
        assert f"Bearer {self.api_key}" == history.headers.get("Authorization")
    
        # Mock a request with params, asser that params were passed successfully 
        m.get(self.base_uri + '/members?first_name=eq.brittany&city=eq.pittsburgh', json=mock_member_data)        
        response = self.connector.get_members(first_name='eq.brittany', city='eq.Pittsburgh')
        history = m.request_history[1] # Get the second request made
        assert history.qs == {'first_name':['eq.brittany'], 'city': ['eq.pittsburgh']}

    @mark_live_test
    def test_get_members_live_test(self):
        # Test filtering on first name 
        response = self.connector.get_members(first_name='eq.Rudolph')
        assert (response.to_dataframe()["first_name"] == 'Rudolph').all()
    
        # Test that selecting for opt_in=True returns only subscribed members
        response = self.connector.get_members(opt_in='eq.True')
        self.assertTrue(all(response.to_dataframe()["opt_in"]))

        # Test filtering on NULL values
        response = self.connector.get_members(email='eq.')
        assert (response.to_dataframe()["email"] == '').all()
    
    @requests_mock.Mocker()
    def test_post_members(self, m):
        mock_member_payload = {
            "phone_number": "+15555555555",
            "campaign_id": 273,
            "first_name": "Lucy",
            "last_name": "Parsons"
            }
        m.post(self.base_uri + '/members', json=mock_member_payload)
        response = self.connector.post_members(data=mock_member_payload)
        history = m.request_history[0] # Get the first request made
        # Assert that a get request was made
        self.assertEqual(history.method, 'POST')
        # Assert mock object has been called
        assert m.called == True
        import pytest; pytest.set_trace()









      


        
        