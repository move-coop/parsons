import os
import unittest
from unittest import mock

import pytest
import requests_mock

from parsons import Airmeet, Table

ENV_PARAMETERS = {
    "AIRMEET_URI": "https://env_api_endpoint",
    "AIRMEET_ACCESS_KEY": "env_access_key",
    "AIRMEET_SECRET_KEY": "env_secret_key",
}


class TestAirmeet(unittest.TestCase):
    @requests_mock.Mocker()
    def setUp(self, m):
        m.post("https://api-gateway.airmeet.com/prod/auth", json={"token": "test_token"})
        self.airmeet = Airmeet(airmeet_access_key="fake_key", airmeet_secret_key="fake_secret")
        self.airmeet.client = mock.MagicMock()

    def tearDown(self):
        pass

    @requests_mock.Mocker()
    @mock.patch.dict(os.environ, ENV_PARAMETERS)
    def test_from_environ(self, m):
        m.post("https://env_api_endpoint/auth", json={"token": "test_token"})
        airmeet = Airmeet()
        self.assertEqual(airmeet.uri, "https://env_api_endpoint")
        self.assertEqual(airmeet.airmeet_client_key, "env_access_key")
        self.assertEqual(airmeet.airmeet_client_secret, "env_secret_key")
        self.assertEqual(airmeet.token, "test_token")

    def test_get_all_pages_single_page(self):
        # Simulate API response for a single page without further cursors.
        self.airmeet.client.get_request = mock.MagicMock(
            return_value={
                "data": [{"id": "1", "name": "Item 1"}],
                "cursors": {"pageCount": 1, "after": None},
            }
        )

        url = "airmeet/some_endpoint"
        result = self.airmeet._get_all_pages(url)

        self.airmeet.client.get_request.assert_called_once_with(url=url, params={"size": 50})
        assert isinstance(result, Table), "The result should be a Table"
        assert len(result) == 1, "Table should contain exactly one record"

    def test_get_all_pages_multiple_pages(self):
        # Simulate API responses for multiple pages.
        responses = [
            {
                "data": [{"id": "1", "name": "Item 1"}],
                "cursors": {"pageCount": 2, "after": "abc123"},
            },
            {
                "data": [{"id": "2", "name": "Item 2"}],
                "cursors": {"pageCount": 2, "after": None},
            },  # Last page
        ]
        self.airmeet.client.get_request = mock.MagicMock(
            side_effect=lambda *args, **kwargs: responses.pop(0)
        )

        url = "airmeet/some_endpoint"
        result = self.airmeet._get_all_pages(url)

        calls = [
            mock.call(url=url, params={"size": 50, "after": "abc123"}),
            mock.call(url=url, params={"size": 50, "after": "abc123"}),
        ]
        self.airmeet.client.get_request.assert_has_calls(calls, any_order=True)
        assert isinstance(result, Table), "The result should be a Table"
        assert len(result) == 2, "Table should contain records from both pages"

    def test_list_airmeets(self):
        # Test get the list of Airmeets.
        self.airmeet.client = mock.MagicMock()

        result = self.airmeet.list_airmeets()

        self.airmeet.client.get_request.assert_called_with(
            url="airmeets",
            params={"size": 500},
        )
        assert isinstance(result, Table), "The result should be a Table"

    def test_fetch_airmeet_participants_single_page(self):
        # Simulate API response for a single page of participants. This
        # particular API doesn't use cursors like the other ones that can have
        # multiple pages, which is why this is a separate test.
        self.airmeet.client.get_request = mock.MagicMock(
            return_value={
                "participants": [{"user_id": "abc123", "name": "Test User 1"}],
                "userCount": 1,
                "totalUserCount": 1,
            }
        )

        result = self.airmeet.fetch_airmeet_participants("test_airmeet_id")

        self.airmeet.client.get_request.assert_called_once_with(
            url="airmeet/test_airmeet_id/participants",
            params={
                "pageNumber": 1,
                "resultSize": 1000,
                "sortingKey": "registrationDate",
                "sortingDirection": "DESC",
            },
        )
        assert isinstance(result, Table), "The result should be a Table"
        assert len(result) == 1, "Table should contain exactly one record"

    def test_fetch_airmeet_participants_multiple_pages(self):
        # Simulate API responses for multiple pages of participants. This
        # particular API doesn't use cursors like the other ones that can have
        # multiple pages, which is why this is a separate test.

        # The connector requests 1000 at a time, so we return a totalUserCount
        # of 2000 here to make it request a second page.
        responses = [
            {
                "participants": [{"user_id": "abc123", "name": "Test User 1"}],
                "userCount": 1,
                "totalUserCount": 2000,
            },
            {
                "participants": [{"user_id": "def456", "name": "Test User 1"}],
                "userCount": 1,
                "totalUserCount": 2000,
            },  # Last page
        ]
        self.airmeet.client.get_request = mock.MagicMock(
            side_effect=lambda *args, **kwargs: responses.pop(0)
        )

        result = self.airmeet.fetch_airmeet_participants("test_airmeet_id")

        calls = [
            mock.call(
                url="airmeet/test_airmeet_id/participants",
                params={
                    "pageNumber": 1,
                    "resultSize": 1000,
                    "sortingKey": "registrationDate",
                    "sortingDirection": "DESC",
                },
            ),
            mock.call(
                url="airmeet/test_airmeet_id/participants",
                params={
                    "pageNumber": 2,
                    "resultSize": 1000,
                    "sortingKey": "registrationDate",
                    "sortingDirection": "DESC",
                },
            ),
        ]
        self.airmeet.client.get_request.assert_has_calls(calls, any_order=True)
        assert isinstance(result, Table), "The result should be a Table"
        assert len(result) == 2, "Table should contain records from both pages"

    def test_fetch_airmeet_sessions(self):
        # Test get the list of sessions for an Airmeet.
        self.airmeet.client.get_request = mock.MagicMock(
            return_value={
                "name": "Test Event",
                "sessions": [
                    {"sessionid": "test_session_id_1", "name": "Test Session 1"},
                    {"sessionid": "test_session_id_2", "name": "Test Session 2"},
                ],
            }
        )

        result = self.airmeet.fetch_airmeet_sessions("test_airmeet_id")

        self.airmeet.client.get_request.assert_called_once_with(url="airmeet/test_airmeet_id/info")
        assert isinstance(result, Table), "The result should be a Table"
        assert len(result) == 2, "Table should contain both records"

    def test_fetch_airmeet_info(self):
        # Test get the Airmeet info.
        self.airmeet.client.get_request = mock.MagicMock(
            return_value={
                "name": "Test Event",
                "sessions": [
                    {"sessionid": "test_session_id_1", "name": "Test Session 1"},
                    {"sessionid": "test_session_id_2", "name": "Test Session 2"},
                ],
                "session_hosts": [{"id": "abc123", "name": "Test Host 1"}],
            }
        )

        result = self.airmeet.fetch_airmeet_info("test_airmeet_id", lists_to_tables=True)

        self.airmeet.client.get_request.assert_called_once_with(url="airmeet/test_airmeet_id/info")
        assert isinstance(result, dict), "The result should be a Table"
        assert isinstance(result["sessions"], Table), "The sessions should be a Table"
        assert isinstance(result["session_hosts"], Table), "The session hosts should be a Table"
        assert len(result["sessions"]) == 2, "Sessions Table should contain exactly two records"
        assert len(result["session_hosts"]) == 1, (
            "Session hosts Table should contain exactly one record"
        )

    def test_fetch_airmeet_custom_registration_fields(self):
        # Test get the custom registration fields for an Airmeet.
        self.airmeet.client.get_request = mock.MagicMock(
            return_value={
                "customFields": [
                    {"fieldId": "test_field_id_1", "label": "Test Label 1"},
                    {"fieldId": "test_field_id_2", "label": "Test Label 2"},
                ],
            }
        )

        result = self.airmeet.fetch_airmeet_custom_registration_fields("test_airmeet_id")

        self.airmeet.client.get_request.assert_called_once_with(
            url="airmeet/test_airmeet_id/custom-fields"
        )
        assert isinstance(result, Table), "The result should be a Table"
        assert len(result) == 2, "Table should contain exactly two records"

    def test_fetch_event_attendance(self):
        # Test get the attendees for an Airmeet.
        self.airmeet.client.get_request = mock.MagicMock(
            return_value={
                "data": [
                    {
                        "name": "Test User 1",
                        "user_id": "abc123",
                    }
                ],
            }
        )

        result = self.airmeet.fetch_event_attendance("test_airmeet_id")

        self.airmeet.client.get_request.assert_called_once_with(
            url="airmeet/test_airmeet_id/attendees",
            params={"size": 50},
        )
        assert isinstance(result, Table), "The result should be a Table"
        assert len(result) == 1, "The result should contain exactly one record"

    def test_fetch_session_attendance(self):
        # Test get the attendees for a session.
        self.airmeet.client.get_request = mock.MagicMock(
            return_value={
                "data": [
                    {
                        "name": "Test User 1",
                        "user_id": "abc123",
                    }
                ],
            }
        )

        result = self.airmeet.fetch_session_attendance("test_session_id")

        self.airmeet.client.get_request.assert_called_once_with(
            url="session/test_session_id/attendees",
            params={"size": 50},
        )
        assert isinstance(result, Table), "The result should be a Table"
        assert len(result) == 1, "The result should contain exactly one record"

    def test_fetch_session_attendance_exception_202(self):
        # Test that an asynchronous API raises an exception if it returns
        # a statusCode == 202.
        self.airmeet.client.get_request = mock.MagicMock(
            return_value={
                "statusCode": 202,
                "statusMessage": "Preparing your results. Try after 5 minutes"
                "to get the updated results",
            }
        )

        with pytest.raises(Exception):  # noqa: B017
            self.airmeet.fetch_session_attendance("test_session_id")

    def test_fetch_session_attendance_exception_400(self):
        # Test that the sessions attendees API raises an exception if it
        # returns a statusCode == 400.
        self.airmeet.client.get_request = mock.MagicMock(
            return_value={
                "data": {},
                "statusCode": 400,
                "statusMessage": "Session status is not valid",
            }
        )

        with pytest.raises(Exception):  # noqa: B017
            self.airmeet.fetch_session_attendance("test_session_id")

    def test_fetch_airmeet_booths(self):
        # Test get the booths for an Airmeet.
        self.airmeet.client.get_request = mock.MagicMock(
            return_value={
                "booths": [
                    {
                        "uid": "test_booth_uid_1",
                        "name": "Test Booth 1",
                    }
                ],
            }
        )

        result = self.airmeet.fetch_airmeet_booths("test_airmeet_id")

        self.airmeet.client.get_request.assert_called_once_with(
            url="airmeet/test_airmeet_id/booths"
        )
        assert isinstance(result, Table), "The result should be a Table"
        assert len(result) == 1, "The result should contain exactly one record"

    def test_fetch_booth_attendance(self):
        # Test get the attendees for a booth.
        self.airmeet.client.get_request = mock.MagicMock(
            return_value={
                "data": [
                    {
                        "name": "Test User 1",
                        "user_id": "abc123",
                    }
                ],
            }
        )

        result = self.airmeet.fetch_booth_attendance(
            "test_airmeet_id",
            booth_id="test_booth_id",
        )

        self.airmeet.client.get_request.assert_called_once_with(
            url="airmeet/test_airmeet_id/booth/test_booth_id/booth-attendance",
            params={"size": 50},
        )
        assert isinstance(result, Table), "The result should be a Table"
        assert len(result) == 1, "The result should contain exactly one record"

    def test_fetch_poll_responses(self):
        # Test get the poll responses for an Airmeet.
        self.airmeet.client.get_request = mock.MagicMock(
            return_value={
                "data": [
                    {
                        "name": "Test User 1",
                        "polls": [
                            {"question": "Poll Question 1", "answer": "Poll Answer 1"},
                            {"question": "Poll Question 2", "answer": "Poll Answer 2"},
                        ],
                    }
                ],
            }
        )

        result = self.airmeet.fetch_poll_responses("test_airmeet_id")

        self.airmeet.client.get_request.assert_called_once_with(
            url="airmeet/test_airmeet_id/polls",
            params={"size": 50},
        )
        assert isinstance(result, Table), "The result should be a Table"
        assert len(result[0]["polls"]) == 2, "The record should contain exactly two poll responses"

    def test_fetch_questions_asked(self):
        # Test get the questions asked for an Airmeet.
        self.airmeet.client.get_request = mock.MagicMock(
            return_value={
                "data": [
                    {
                        "name": "Test User 1",
                        "questions": [
                            {"question": "Question 1", "session_id": "session_id_1"},
                            {"question": "Question 2", "session_id": "session_id_2"},
                        ],
                    }
                ],
            }
        )

        result = self.airmeet.fetch_questions_asked("test_airmeet_id")

        self.airmeet.client.get_request.assert_called_once_with(
            url="airmeet/test_airmeet_id/questions"
        )
        assert isinstance(result, Table), "The result should be a Table"
        assert len(result[0]["questions"]) == 2, "The record should contain exactly two questions"

    def test_fetch_event_tracks(self):
        # Test get the tracks for an Airmeet.
        self.airmeet.client.get_request = mock.MagicMock(
            return_value={
                "tracks": [
                    {
                        "uid": "test_track_uid_1",
                        "name": "Test Track 1",
                        "sessions": [
                            "session_id_1",
                            "session_id_2",
                        ],
                    }
                ],
            }
        )

        result = self.airmeet.fetch_event_tracks("test_airmeet_id")

        self.airmeet.client.get_request.assert_called_once_with(
            url="airmeet/test_airmeet_id/tracks"
        )
        assert isinstance(result, Table), "The result should be a Table"
        assert len(result[0]["sessions"]) == 2, "The record should contain exactly two session ids"

    def test_fetch_registration_utms(self):
        # Test get the registration UTMs for an Airmeet.
        self.airmeet.client.get_request = mock.MagicMock(
            return_value={
                "data": [
                    {
                        "airmeetId": "test_airmeet_id",
                        "email": "test@example.com",
                        "id": 1,
                        "utms": {
                            "utm_campaign": "test_utm_campaign",
                            "utm_medium": None,
                            "utm_source": "test_utm_source",
                        },
                    }
                ],
            }
        )

        result = self.airmeet.fetch_registration_utms("test_airmeet_id")

        self.airmeet.client.get_request.assert_called_once_with(
            url="airmeet/test_airmeet_id/utms",
            params={"size": 50},
        )
        assert isinstance(result, Table), "The result should be a Table"
        assert len(result) == 1, "The result should contain exactly one record"
        assert len(result[0]["utms"]) == 3, "The record should contain exactly three UTMs"

    def test_download_session_recordings(self):
        # Test get the session recordings for an Airmeet.
        self.airmeet.client.get_request = mock.MagicMock(
            return_value={
                "recordings": [
                    {
                        "session_id": "test_session_id_1",
                        "session_name": "Test Session 1",
                        "download_link": "https://example.com/test_download_link",
                    }
                ],
            }
        )

        result = self.airmeet.download_session_recordings(
            "test_airmeet_id",
            session_id="test_session_id",
        )

        self.airmeet.client.get_request.assert_called_once_with(
            url="airmeet/test_airmeet_id/session-recordings",
            sessionIds="test_session_id",
        )
        assert isinstance(result, Table), "The result should be a Table"
        assert len(result) == 1, "The result should contain exactly one record"

    def test_fetch_event_replay_attendance(self):
        # Test get the replay attendees for an Airmeet.
        self.airmeet.client.get_request = mock.MagicMock(
            return_value={
                "data": [
                    {
                        "id": 1,
                        "name": "Test User 1",
                        "session_id": "test_session_id",
                    }
                ],
            }
        )

        result = self.airmeet.fetch_event_replay_attendance("test_airmeet_id")

        self.airmeet.client.get_request.assert_called_once_with(
            url="airmeet/test_airmeet_id/event-replay-attendees",
            params={"size": 50},
        )
        assert isinstance(result, Table), "The result should be a Table"
        assert len(result) == 1, "The result should contain exactly one record"

    def test_fetch_event_replay_attendance_exception_400(self):
        # Test that the replay attendees API raises an exception if it returns
        # a statusCode == 400.
        self.airmeet.client.get_request = mock.MagicMock(
            return_value={
                "data": {},
                "statusCode": 400,
                "statusMessage": "Airmeet status is not valid",
            }
        )

        with pytest.raises(Exception):  # noqa: B017
            self.airmeet.fetch_event_replay_attendance("test_airmeet_id")
