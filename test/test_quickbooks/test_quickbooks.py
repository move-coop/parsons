import os
import unittest
import requests_mock
from parsons.etl.table import Table
from parsons.quickbooks.quickbooks import QuickBooks
from test_quickbooks_data import mock_group_data, mock_user_data


class TestQuickBooks(unittest.TestCase):

    @requests_mock.Mocker()
    def setUp(self, mock_request):
        self.qb = QuickBooks(token="abc123")
        self.qb.url = "https://rest.tsheets.com/api/v1/"
    
    def tearDown(self):
        pass

    @requests_mock.Mocker()
    def test_qb_get_request(self, mock_request):
        # Arrange
        end_point = "test_endpoint"
        querystring = {"page": 1}
        mock_request.get(requests_mock.ANY, json={"results": {end_point: {"1": "test"}}, "more": False})

        # Act
        result = self.qb.qb_get_request(end_point, querystring)

        # Assert
        self.assertIsInstance(result, list)
        self.assertEqual(result[0], "test")

    @requests_mock.Mocker()
    def test_get_groups(self, mock_request):
        # Arrange
        mock_request.get(requests_mock.ANY, json=mock_group_data)

        # Act
        result = self.qb.get_groups()

        # Assert
        self.assertIsInstance(result, Table)

    @requests_mock.Mocker()
    def test_get_jobcodes(self, mock_request):
        # Arrange
        mock_request.get(requests_mock.ANY, json=mock_group_data)

        # Act
        result = self.qb.get_jobcodes()

        # Assert
        self.assertIsInstance(result, Table)

    @requests_mock.Mocker()
    def test_get_timesheets(self, mock_request):
        # Arrange
        mock_request.get(requests_mock.ANY, json=mock_group_data)

        # Act
        result = self.qb.get_timesheets()

        # Assert
        self.assertIsInstance(result, Table)