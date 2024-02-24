import unittest
import os
import requests_mock
from parsons import VAN
from test.utils import assert_matching_tables
from responses_email import mock_get_emails

os.environ["VAN_API_KEY"] = "SOME_KEY"


class TestEmail(unittest.TestCase):
    def setUp(self):

        self.van = VAN(
            os.environ["VAN_API_KEY"], db="EveryAction", raise_for_status=False
        )

    def tearDown(self):

        pass

    @requests_mock.Mocker()
    def test_get_emails(self, m):

        mock_response = mock_get_emails

        m.get(f"{self.van.connection.uri}/emails", json=mock_response)

        # Test the method
        assert_matching_tables(self.van.get_emails(), mock_response["emails"])

    @requests_mock.Mocker()
    def test_get_email(self, m):

        mock_response = mock_get_emails[0]

        m.get(f"{self.van.connection.uri}/email/messages/1", json=mock_response)

        # Test the method
        assert_matching_tables(self.van.get_email(1), mock_response)

    @requests_mock.Mocker()
    def test_get_email_stats(self, m):

        mock_response = mock_get_emails

        m.get(f"{self.van.connection.uri}/emails", json=mock_response)

        # Test the method
        assert_matching_tables(self.van.get_email_stats(), mock_response)
