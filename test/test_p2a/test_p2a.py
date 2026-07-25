"""Tests for the Phone2Action connector."""

import copy

import pytest

from parsons import Phone2Action
from test.conftest import validate_list


def parse_request_body(body: str) -> dict:
    return dict(kv.split("=") for kv in body.split("&"))


def test_init_from_env(monkeypatch):
    monkeypatch.setenv("PHONE2ACTION_APP_ID", "id")
    monkeypatch.setenv("PHONE2ACTION_APP_KEY", "key")

    p2a = Phone2Action()

    assert p2a.app_id == "id"
    assert p2a.app_key == "key"


def test_get_advocates(p2a, requests_mock, load):
    requests_mock.get(p2a.client.uri + "advocates", json=load("advocates"))

    advocates = p2a.get_advocates()

    assert validate_list(
        [
            "id",
            "prefix",
            "firstname",
            "middlename",
            "lastname",
            "suffix",
            "notes",
            "stage",
            "connections",
            "created_at",
            "updated_at",
            "address_city",
            "address_county",
            "address_latitude",
            "address_longitude",
            "address_state",
            "address_street1",
            "address_street2",
            "address_zip4",
            "address_zip5",
            "districts_cityCouncil",
            "districts_congressional",
            "districts_stateHouse",
            "districts_stateSenate",
        ],
        advocates["advocates"],
    )
    assert validate_list(["advocate_id", "ids"], advocates["ids"])
    assert validate_list(
        ["advocate_id", "phones_address", "phones_id", "phones_subscribed"], advocates["phones"]
    )
    assert validate_list(["advocate_id", "tags"], advocates["tags"])
    assert validate_list(
        ["advocate_id", "emails_address", "emails_id", "emails_subscribed"], advocates["emails"]
    )
    assert validate_list(
        [
            "advocate_id",
            "memberships_campaignid",
            "memberships_created_at",
            "memberships_id",
            "memberships_name",
            "memberships_source",
        ],
        advocates["memberships"],
    )
    assert validate_list(["advocate_id", "fields"], advocates["fields"])


def test_get_advocates_stops_after_last_page(p2a, requests_mock, load):
    """With a single page of results, page 2 must never be requested."""
    requests_mock.get(p2a.client.uri + "advocates?page=1", json=load("advocates"))
    requests_mock.get(
        p2a.client.uri + "advocates?page=2", exc=AssertionError("page 2 should not be requested")
    )

    results = p2a.get_advocates(page=1)

    assert results["advocates"].num_rows == 1


def test_get_advocates_empty(p2a, requests_mock, load):
    empty = copy.deepcopy(load("advocates"))
    empty["data"] = []
    empty["pagination"]["count"] = 0
    requests_mock.get(p2a.client.uri + "advocates", json=empty)

    results = p2a.get_advocates()

    assert results["advocates"].num_rows == 0


def test_get_campaigns(p2a, requests_mock, load):
    requests_mock.get(p2a.client.uri + "campaigns", json=load("campaigns"))

    assert validate_list(
        [
            "id",
            "name",
            "display_name",
            "subtitle",
            "public",
            "topic",
            "type",
            "link",
            "restrict_allow",
            "updated_at_date",
            "updated_at_timezone",
            "updated_at_timezone_type",
            "content_background_image",
            "content_call_to_action",
            "content_introduction",
            "content_summary",
            "content_thank_you",
        ],
        p2a.get_campaigns(),
    )


def test_create_advocate_requires_phone_or_email(p2a, requests_mock):
    requests_mock.post(p2a.client.uri + "advocates", json={"advocateid": 1})

    with pytest.raises(
        ValueError,
        match="When creating an advocate, you must provide an email address or a phone number",
    ):
        p2a.create_advocate(campaigns=[1], firstname="Foo", lastname="bar")


def test_create_advocate_sms_optin_requires_phone(p2a, requests_mock):
    requests_mock.post(p2a.client.uri + "advocates", json={"advocateid": 1})

    with pytest.raises(
        ValueError,
        match="When opting an advocate in or out of SMS messages, you must specify a valid phone",
    ):
        p2a.create_advocate(campaigns=[1], email="foo@bar.com", sms_optin=True)


def test_create_advocate_email_optin_requires_email(p2a, requests_mock):
    requests_mock.post(p2a.client.uri + "advocates", json={"advocateid": 1})

    with pytest.raises(
        ValueError,
        match="When opting an advocate in or out of email messages, you must specify a valid email",
    ):
        p2a.create_advocate(campaigns=[1], phone="1234567890", email_optin=True)


def test_create_advocate_maps_properties(p2a, requests_mock):
    requests_mock.post(p2a.client.uri + "advocates", json={"advocateid": 1})

    advocate_id = p2a.create_advocate(
        campaigns=[1], email="foo@bar.com", email_optin=True, firstname="Test"
    )

    assert advocate_id == 1
    data = parse_request_body(requests_mock.last_request.text)
    assert data["firstname"] == "Test"
    assert "lastname" not in data
    assert data["emailOptin"] == "1"
    assert data["email"] == "foo%40bar.com"


def test_update_advocate_maps_properties(p2a, requests_mock):
    requests_mock.post(p2a.client.uri + "advocates")

    p2a.update_advocate(
        advocate_id=1, campaigns=[1], email="foo@bar.com", email_optin=True, firstname="Test"
    )

    data = parse_request_body(requests_mock.last_request.text)
    assert data["firstname"] == "Test"
    assert "lastname" not in data
    assert data["emailOptin"] == "1"
    assert data["email"] == "foo%40bar.com"
