"""Tests for the Controlshift connector."""

import pytest

from parsons import Controlshift
from test.conftest import validate_list


@pytest.mark.live
def test_get_petitions_live(load):
    tbl = Controlshift().get_petitions()

    assert validate_list(load("expected_petition_columns"), tbl)


def test_get_petitions(controlshift, hostname, requests_mock, load):
    requests_mock.get(
        f"{hostname}/api/v1/petitions",
        json=load("petitions"),
    )

    tbl = controlshift.get_petitions()

    assert validate_list(load("expected_petition_columns"), tbl)
    assert tbl.num_rows == 1


def test_get_petitions_follows_pagination(controlshift, hostname, requests_mock, load):
    """Paging starts at page 1 and follows ``meta.next_page`` until it is null."""
    page_one = load("petitions")
    page_one["meta"]["next_page"] = 2
    page_two = load("petitions")

    requests_mock.get(
        f"{hostname}/api/v1/petitions",
        [{"json": page_one}, {"json": page_two}],
    )

    tbl = controlshift.get_petitions()

    assert tbl.num_rows == 2
    requested_pages = [r.qs["page"] for r in requests_mock.request_history if r.method == "GET"]
    assert requested_pages == [["1"], ["2"]]


@pytest.mark.parametrize(
    ("given", "expected"),
    [
        ("http://test.example.com", "https://test.example.com"),
        ("test.example.com", "https://test.example.com"),
        ("https://test.example.com", "https://test.example.com"),
    ],
)
def test_hostname_is_normalized_to_https(given, expected, requests_mock):
    """The connector upgrades http:// and adds a missing scheme."""
    requests_mock.post(f"{expected}/oauth/token", json={"access_token": "123"})

    cs = Controlshift(hostname=given, client_id="1234", client_secret="1234")

    assert cs.hostname == expected
