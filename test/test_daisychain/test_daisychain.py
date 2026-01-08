import unittest

import pytest
import requests_mock

from parsons import Daisychain


class TestDaisychain(unittest.TestCase):
    def setUp(self):
        self.api_token = "test_api_token"
        self.connector = Daisychain(api_token=self.api_token)

    def test_initialization(self):
        """Test that Daisychain initializes with correct API token header."""
        assert self.connector.connection.headers["X-API-Token"] == self.api_token
        assert self.connector.connection.uri == "https://go.daisychain.app/api/v1/"

    @requests_mock.Mocker()
    def test_find_person_email(self, mocker):
        """Test finding a person by email address."""
        expected_response = {
            "people": [
                {
                    "id": "person123",
                    "email": "test@example.com",
                    "first_name": "Test",
                    "last_name": "User",
                }
            ]
        }

        mocker.post("https://go.daisychain.app/api/v1/people/match", json=expected_response)

        result = self.connector.find_person(email_address="test@example.com")

        assert result == expected_response["people"]
        assert len(result) == 1
        assert result[0]["email"] == "test@example.com"

    @requests_mock.Mocker()
    def test_find_person_phone(self, mocker):
        """Test finding a person by phone number."""
        expected_response = {
            "people": [
                {
                    "id": "person456",
                    "phone_number": "+15555551234",
                    "first_name": "Jane",
                    "last_name": "Doe",
                }
            ]
        }

        mocker.post("https://go.daisychain.app/api/v1/people/match", json=expected_response)

        result = self.connector.find_person(phone_number="+15555551234")

        assert result == expected_response["people"]
        assert result[0]["phone_number"] == "+15555551234"

    @requests_mock.Mocker()
    def test_find_person_email_and_phone(self, mocker):
        """Test finding a person by both email and phone."""
        expected_response = {
            "people": [
                {
                    "id": "person789",
                    "email": "combo@example.com",
                    "phone_number": "+15555559999",
                    "first_name": "Combo",
                    "last_name": "Test",
                }
            ]
        }

        mocker.post("https://go.daisychain.app/api/v1/people/match", json=expected_response)

        result = self.connector.find_person(
            email_address="combo@example.com", phone_number="+15555559999"
        )

        assert result == expected_response["people"]

    def test_find_person_requires_parameter(self):
        """Test that find_person requires at least one parameter."""
        with pytest.raises(AssertionError):
            self.connector.find_person()

    @requests_mock.Mocker()
    def test_post_action_minimal(self, mocker):
        """Test posting an action with minimal data."""
        expected_response = {"person": {"id": "person123"}}

        mocker.post("https://go.daisychain.app/api/v1/actions", json=expected_response)

        person_id = self.connector.post_action(email_address="test@example.com")

        assert person_id == "person123"

    @requests_mock.Mocker()
    def test_post_action_full(self, mocker):
        """Test posting an action with full person data."""
        expected_response = {"person": {"id": "person456"}}

        mocker.post("https://go.daisychain.app/api/v1/actions", json=expected_response)

        person_id = self.connector.post_action(
            email_address="test@example.com",
            phone_number="+15555551234",
            first_name="Jane",
            last_name="Doe",
            addresses=[{"city": "New York", "state": "NY"}],
            email_opt_in=True,
            sms_opt_in=True,
            action_data={"type": "petition_signature", "petition_id": "12345"},
        )

        assert person_id == "person456"

    @requests_mock.Mocker()
    def test_post_action_custom_data(self, mocker):
        """Test posting an action with custom action data."""
        expected_response = {"person": {"id": "person789"}}

        mocker.post("https://go.daisychain.app/api/v1/actions", json=expected_response)

        custom_data = {
            "event_type": "volunteer_signup",
            "event_id": "canvass_2024",
            "custom_field": "custom_value",
        }

        person_id = self.connector.post_action(phone_number="+15555559999", action_data=custom_data)

        assert person_id == "person789"

    def test_post_action_requires_contact(self):
        """Test that post_action requires at least email or phone."""
        with pytest.raises(AssertionError):
            self.connector.post_action(first_name="Test", last_name="User")
