from parsons import Freshdesk
import unittest
import requests_mock
from test.test_freshdesk import expected_json

DOMAIN = "myorg"
API_KEY = "mykey"


class TestFreshdesk(unittest.TestCase):
    def setUp(self):

        self.fd = Freshdesk(DOMAIN, API_KEY)

    @requests_mock.Mocker()
    def test_get_agents(self, m):

        # Test that agents are returned correctly.
        m.get(self.fd.uri + "agents", json=expected_json.test_agent)
        self.fd.get_agents()

    @requests_mock.Mocker()
    def test_get_tickets(self, m):

        # Test that tickets are returned correctly.
        m.get(self.fd.uri + "tickets", json=expected_json.test_ticket)
        self.fd.get_tickets()

    @requests_mock.Mocker()
    def test_get_companies(self, m):

        # Test that tickets are returned correctly.
        m.get(self.fd.uri + "companies", json=expected_json.test_company)
        self.fd.get_companies()

    @requests_mock.Mocker()
    def test_get_contacts(self, m):

        # Test that tickets are returned correctly.
        m.get(self.fd.uri + "contacts", json=expected_json.test_contact)
        self.fd.get_contacts()

    @requests_mock.Mocker()
    def test_create_ticket(self, m):
        # Import the expected JSON
        from .expected_json import test_create_ticket_response

        # Setup mock response
        m.post(self.fd.uri + "tickets", json=test_create_ticket_response)

        # Call the function
        response = self.fd.create_ticket(
            subject="Support Needed...",
            description="Details about the issue...",
            email="tom@outerspace.com",
            priority=1,
            status=2,
            cc_emails=["ram@freshdesk.com", "diana@freshdesk.com"],
        )

        # Assertions to check if the function behaves as expected
        self.assertEqual(response, test_create_ticket_response)

    @requests_mock.Mocker()
    def test_create_ticket_with_custom_fields(self, m):
        # Import the expected JSON
        from .expected_json import test_create_ticket_with_custom_fields_response

        # Setup mock response
        m.post(self.fd.uri + "tickets", json=test_create_ticket_with_custom_fields_response)

        # Call the function
        response = self.fd.create_ticket(
            subject="Support Needed...",
            description="Details about the issue...",
            email="tom@outerspace.com",
            priority=1,
            status=2,
            cc_emails=["ram@freshdesk.com", "diana@freshdesk.com"],
            custom_fields={"category": "Primary"},
        )

        # Assertions to check if the function behaves as expected
        self.assertEqual(response, test_create_ticket_with_custom_fields_response)
