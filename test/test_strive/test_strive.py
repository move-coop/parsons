from parsons import Strive
import pytest
import unittest
import strive_test_data
from parsons import Table
from unittest.mock import patch

class TestStrive(unittest.TestCase):
    
    def setUp(self):
        self.strive = Strive()
    
    def test_get_members_with_first_name(self):
        mock_response =  strive_test_data.get_members_expected_output
        # Mock the GET request method to return the mock response
        with patch.object(self.strive, "get_members", return_value=mock_response):
            # Call the get_members method with the first_name parameter
            result = self.strive.get_members(first_name="brittany")
            # Verify that the result is a Table object
            assert isinstance(result, Table)
            # Verify that the result contains the expected data
            expected_data = [{"id": 252025504, "first_name": "brittany", "last_name": "bennett", "phone_number": "+1234567891"}]
            assert result.columns == ['id', 'first_name', 'last_name', 'phone_number']
            assert result.data == expected_data
        
    def test_get_members_with_last_name(self):
        mock_response =  strive_test_data.get_members_expected_output
        # Mock the GET request method to return the mock response
        with patch.object(self.strive, "get_members", return_value=mock_response):
            # Call the get_members method with the first_name parameter
            result = self.strive.get_members(first_name="bennett")
            # Verify that the result is a Table object
            assert isinstance(result, Table)
            # Verify that the result contains the expected data
            expected_data = [{"id": 252025504, "first_name": "brittany", "last_name": "bennett", "phone_number": "+1234567891"}]
            assert result.columns == ['id', 'first_name', 'last_name', 'phone_number']
            assert result.data == expected_data
