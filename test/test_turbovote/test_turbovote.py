"""Tests for the TurboVote connector."""

from test.conftest import validate_list

FAKE_TOKEN = {"id-token": "FAKE-TOKEN"}

EXPECTED_USER_COLUMNS = [
    "id",
    "first-name",
    "middle-name",
    "last-name",
    "phone",
    "email",
    "registered-address-street",
    "registered-address-street-2",
    "registered-address-city",
    "registered-address-state",
    "registered-address-zip",
    "mailing-address-street",
    "mailing-address-street-2",
    "mailing-address-city",
    "mailing-address-state",
    "mailing-address-zip",
    "dob",
    "language-preference",
    "hostname",
    "referral-code",
    "partner-comms-opt-in",
    "created-at",
    "updated-at",
    "voter-registration-status",
    "voter-registration-source",
    "voter-registration-method",
    "voting-method-preference",
    "email subscribed",
    "sms subscribed",
]


def test_init(turbovote):
    assert turbovote.username == "usr"
    assert turbovote.password == "pwd"
    assert turbovote.subdomain == "myorg"


def test_get_token(turbovote, requests_mock):
    requests_mock.post(turbovote.uri + "login", json=FAKE_TOKEN)

    assert turbovote._get_token() == FAKE_TOKEN["id-token"]


def test_get_users(turbovote, requests_mock, shared_datadir):
    requests_mock.post(turbovote.uri + "login", json=FAKE_TOKEN)
    requests_mock.get(
        turbovote.uri + f"partners/{turbovote.subdomain}.turbovote.org/users",
        text=(shared_datadir / "users.csv").read_text(),
    )

    assert validate_list(EXPECTED_USER_COLUMNS, turbovote.get_users())


def test_get_users_sends_token(turbovote, requests_mock, shared_datadir):
    """The bearer token from login should be sent on the users request."""
    requests_mock.post(turbovote.uri + "login", json=FAKE_TOKEN)
    requests_mock.get(
        turbovote.uri + f"partners/{turbovote.subdomain}.turbovote.org/users",
        text=(shared_datadir / "users.csv").read_text(),
    )

    turbovote.get_users()

    assert FAKE_TOKEN["id-token"] in requests_mock.last_request.headers["Authorization"]
