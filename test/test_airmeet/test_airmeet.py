"""Tests for the Airmeet connector.

Airmeet is built on ``APIConnector``, so tests mock the real HTTP boundary with
the ``requests_mock`` fixture (see docs/contrib_docs/write_tests.rst). Registering the exact
endpoint URL means an unexpected call raises ``NoMockAddress``, so the request
path is verified implicitly; query-string params are checked where they matter.
"""

from urllib.parse import parse_qs, urlparse

import pytest

from parsons import Airmeet, Table

BASE = "https://api-gateway.airmeet.com/prod/"


def _qs(request) -> dict:
    """Parse a request's query string, preserving parameter-name case."""
    return parse_qs(urlparse(request.url).query)


def test_from_environ(requests_mock, monkeypatch):
    monkeypatch.setenv("AIRMEET_URI", "https://env_api_endpoint")
    monkeypatch.setenv("AIRMEET_ACCESS_KEY", "env_access_key")
    monkeypatch.setenv("AIRMEET_SECRET_KEY", "env_secret_key")
    requests_mock.post("https://env_api_endpoint/auth", json={"token": "test_token"})

    airmeet = Airmeet()

    assert airmeet.uri == "https://env_api_endpoint"
    assert airmeet.airmeet_client_key == "env_access_key"
    assert airmeet.airmeet_client_secret == "env_secret_key"
    assert airmeet.token == "test_token"


def test_get_all_pages_single_page(airmeet, requests_mock):
    requests_mock.get(
        f"{BASE}airmeet/some_endpoint",
        json={
            "data": [{"id": "1", "name": "Item 1"}],
            "cursors": {"pageCount": 1, "after": None},
        },
    )

    result = airmeet._get_all_pages("airmeet/some_endpoint")

    assert _qs(requests_mock.last_request) == {"size": ["50"]}
    assert isinstance(result, Table)
    assert len(result) == 1


def test_get_all_pages_multiple_pages(airmeet, requests_mock):
    requests_mock.get(
        f"{BASE}airmeet/some_endpoint",
        [
            {
                "json": {
                    "data": [{"id": "1", "name": "Item 1"}],
                    "cursors": {"pageCount": 2, "after": "abc123"},
                }
            },
            {
                "json": {
                    "data": [{"id": "2", "name": "Item 2"}],
                    "cursors": {"pageCount": 2, "after": None},
                }
            },
        ],
    )

    result = airmeet._get_all_pages("airmeet/some_endpoint")

    # The second page is fetched with the cursor from the first.
    assert _qs(requests_mock.last_request) == {"size": ["50"], "after": ["abc123"]}
    assert isinstance(result, Table)
    assert len(result) == 2


def test_list_airmeets(airmeet, requests_mock):
    requests_mock.get(
        f"{BASE}airmeets",
        json={"data": [{"id": "1"}], "cursors": {"pageCount": 1, "after": None}},
    )

    result = airmeet.list_airmeets()

    assert _qs(requests_mock.last_request) == {"size": ["500"]}
    assert isinstance(result, Table)


def test_fetch_airmeet_participants_single_page(airmeet, requests_mock):
    requests_mock.get(
        f"{BASE}airmeet/test_airmeet_id/participants",
        json={
            "participants": [{"user_id": "abc123", "name": "Test User 1"}],
            "userCount": 1,
            "totalUserCount": 1,
        },
    )

    result = airmeet.fetch_airmeet_participants("test_airmeet_id")

    assert _qs(requests_mock.last_request) == {
        "pageNumber": ["1"],
        "resultSize": ["1000"],
        "sortingKey": ["registrationDate"],
        "sortingDirection": ["DESC"],
    }
    assert isinstance(result, Table)
    assert len(result) == 1


def test_fetch_airmeet_participants_multiple_pages(airmeet, requests_mock):
    # totalUserCount of 2000 with a page size of 1000 forces a second page.
    requests_mock.get(
        f"{BASE}airmeet/test_airmeet_id/participants",
        [
            {
                "json": {
                    "participants": [{"user_id": "abc123", "name": "Test User 1"}],
                    "userCount": 1,
                    "totalUserCount": 2000,
                }
            },
            {
                "json": {
                    "participants": [{"user_id": "def456", "name": "Test User 2"}],
                    "userCount": 1,
                    "totalUserCount": 2000,
                }
            },
        ],
    )

    result = airmeet.fetch_airmeet_participants("test_airmeet_id")

    assert _qs(requests_mock.last_request)["pageNumber"] == ["2"]
    assert isinstance(result, Table)
    assert len(result) == 2


def test_fetch_airmeet_sessions(airmeet, requests_mock):
    requests_mock.get(
        f"{BASE}airmeet/test_airmeet_id/info",
        json={
            "name": "Test Event",
            "sessions": [
                {"sessionid": "test_session_id_1", "name": "Test Session 1"},
                {"sessionid": "test_session_id_2", "name": "Test Session 2"},
            ],
        },
    )

    result = airmeet.fetch_airmeet_sessions("test_airmeet_id")

    assert isinstance(result, Table)
    assert len(result) == 2


def test_fetch_airmeet_info(airmeet, requests_mock):
    requests_mock.get(
        f"{BASE}airmeet/test_airmeet_id/info",
        json={
            "name": "Test Event",
            "sessions": [
                {"sessionid": "test_session_id_1", "name": "Test Session 1"},
                {"sessionid": "test_session_id_2", "name": "Test Session 2"},
            ],
            "session_hosts": [{"id": "abc123", "name": "Test Host 1"}],
        },
    )

    result = airmeet.fetch_airmeet_info("test_airmeet_id", lists_to_tables=True)

    assert isinstance(result, dict)
    assert isinstance(result["sessions"], Table)
    assert isinstance(result["session_hosts"], Table)
    assert len(result["sessions"]) == 2
    assert len(result["session_hosts"]) == 1


def test_fetch_airmeet_custom_registration_fields(airmeet, requests_mock):
    requests_mock.get(
        f"{BASE}airmeet/test_airmeet_id/custom-fields",
        json={
            "customFields": [
                {"fieldId": "test_field_id_1", "label": "Test Label 1"},
                {"fieldId": "test_field_id_2", "label": "Test Label 2"},
            ],
        },
    )

    result = airmeet.fetch_airmeet_custom_registration_fields("test_airmeet_id")

    assert isinstance(result, Table)
    assert len(result) == 2


def test_fetch_event_attendance(airmeet, requests_mock):
    requests_mock.get(
        f"{BASE}airmeet/test_airmeet_id/attendees",
        json={"data": [{"name": "Test User 1", "user_id": "abc123"}]},
    )

    result = airmeet.fetch_event_attendance("test_airmeet_id")

    assert _qs(requests_mock.last_request) == {"size": ["50"]}
    assert isinstance(result, Table)
    assert len(result) == 1


def test_fetch_session_attendance(airmeet, requests_mock):
    requests_mock.get(
        f"{BASE}session/test_session_id/attendees",
        json={"data": [{"name": "Test User 1", "user_id": "abc123"}]},
    )

    result = airmeet.fetch_session_attendance("test_session_id")

    assert _qs(requests_mock.last_request) == {"size": ["50"]}
    assert isinstance(result, Table)
    assert len(result) == 1


def test_fetch_session_attendance_exception_202(airmeet, requests_mock):
    # A body statusCode of 202 signals an async result that isn't ready yet.
    requests_mock.get(
        f"{BASE}session/test_session_id/attendees",
        json={
            "statusCode": 202,
            "statusMessage": "Preparing your results. Try after 5 minutes to get the updated results",
        },
    )

    with pytest.raises(
        Exception,
        match="'statusCode': 202",
    ):
        airmeet.fetch_session_attendance("test_session_id")


def test_fetch_session_attendance_exception_400(airmeet, requests_mock):
    requests_mock.get(
        f"{BASE}session/test_session_id/attendees",
        json={"data": {}, "statusCode": 400, "statusMessage": "Session status is not valid"},
    )

    with pytest.raises(Exception, match="'statusCode': 400"):
        airmeet.fetch_session_attendance("test_session_id")


def test_fetch_airmeet_booths(airmeet, requests_mock):
    requests_mock.get(
        f"{BASE}airmeet/test_airmeet_id/booths",
        json={"booths": [{"uid": "test_booth_uid_1", "name": "Test Booth 1"}]},
    )

    result = airmeet.fetch_airmeet_booths("test_airmeet_id")

    assert isinstance(result, Table)
    assert len(result) == 1


def test_fetch_booth_attendance(airmeet, requests_mock):
    requests_mock.get(
        f"{BASE}airmeet/test_airmeet_id/booth/test_booth_id/booth-attendance",
        json={"data": [{"name": "Test User 1", "user_id": "abc123"}]},
    )

    result = airmeet.fetch_booth_attendance("test_airmeet_id", booth_id="test_booth_id")

    assert _qs(requests_mock.last_request) == {"size": ["50"]}
    assert isinstance(result, Table)
    assert len(result) == 1


def test_fetch_poll_responses(airmeet, requests_mock):
    requests_mock.get(
        f"{BASE}airmeet/test_airmeet_id/polls",
        json={
            "data": [
                {
                    "name": "Test User 1",
                    "polls": [
                        {"question": "Poll Question 1", "answer": "Poll Answer 1"},
                        {"question": "Poll Question 2", "answer": "Poll Answer 2"},
                    ],
                }
            ],
        },
    )

    result = airmeet.fetch_poll_responses("test_airmeet_id")

    assert isinstance(result, Table)
    assert len(result[0]["polls"]) == 2


def test_fetch_questions_asked(airmeet, requests_mock):
    requests_mock.get(
        f"{BASE}airmeet/test_airmeet_id/questions",
        json={
            "data": [
                {
                    "name": "Test User 1",
                    "questions": [
                        {"question": "Question 1", "session_id": "session_id_1"},
                        {"question": "Question 2", "session_id": "session_id_2"},
                    ],
                }
            ],
        },
    )

    result = airmeet.fetch_questions_asked("test_airmeet_id")

    assert isinstance(result, Table)
    assert len(result[0]["questions"]) == 2


def test_fetch_event_tracks(airmeet, requests_mock):
    requests_mock.get(
        f"{BASE}airmeet/test_airmeet_id/tracks",
        json={
            "tracks": [
                {
                    "uid": "test_track_uid_1",
                    "name": "Test Track 1",
                    "sessions": ["session_id_1", "session_id_2"],
                }
            ],
        },
    )

    result = airmeet.fetch_event_tracks("test_airmeet_id")

    assert isinstance(result, Table)
    assert len(result[0]["sessions"]) == 2


def test_fetch_registration_utms(airmeet, requests_mock):
    requests_mock.get(
        f"{BASE}airmeet/test_airmeet_id/utms",
        json={
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
        },
    )

    result = airmeet.fetch_registration_utms("test_airmeet_id")

    assert _qs(requests_mock.last_request) == {"size": ["50"]}
    assert isinstance(result, Table)
    assert len(result) == 1
    assert len(result[0]["utms"]) == 3


def test_download_session_recordings(airmeet, requests_mock):
    requests_mock.get(
        f"{BASE}airmeet/test_airmeet_id/session-recordings",
        json={
            "recordings": [
                {
                    "session_id": "test_session_id_1",
                    "session_name": "Test Session 1",
                    "download_link": "https://example.com/test_download_link",
                }
            ],
        },
    )

    # NOTE: the ``session_id`` filter is intentionally not exercised here. The
    # connector currently forwards ``sessionIds`` as a request kwarg instead of a
    # query param, so passing ``session_id`` raises TypeError and the filter never
    # reaches the API. That bug and its coverage are handled in a separate fix PR.
    result = airmeet.download_session_recordings("test_airmeet_id")

    assert _qs(requests_mock.last_request) == {}
    assert isinstance(result, Table)
    assert len(result) == 1


def test_fetch_event_replay_attendance(airmeet, requests_mock):
    requests_mock.get(
        f"{BASE}airmeet/test_airmeet_id/event-replay-attendees",
        json={"data": [{"id": 1, "name": "Test User 1", "session_id": "test_session_id"}]},
    )

    result = airmeet.fetch_event_replay_attendance("test_airmeet_id")

    assert _qs(requests_mock.last_request) == {"size": ["50"]}
    assert isinstance(result, Table)
    assert len(result) == 1


def test_fetch_event_replay_attendance_exception_400(airmeet, requests_mock):
    requests_mock.get(
        f"{BASE}airmeet/test_airmeet_id/event-replay-attendees",
        json={"data": {}, "statusCode": 400, "statusMessage": "Airmeet status is not valid"},
    )

    with pytest.raises(Exception, match="'statusCode': 400"):
        airmeet.fetch_event_replay_attendance("test_airmeet_id")
