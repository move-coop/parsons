"""Tests for the NationBuilder connector."""

import pytest

from parsons import NationBuilder as NB

INVALID_SLUGS = ["", "  ", None, 1337, {}, []]


def test_client(nb):
    assert nb.client.uri == "https://test-slug.nationbuilder.com/api/v1/"
    assert nb.client.headers == {
        "authorization": "Bearer test-token",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }


def test_get_uri_success():
    assert NB.get_uri("foo") == "https://foo.nationbuilder.com/api/v1"
    assert NB.get_uri("bar") == "https://bar.nationbuilder.com/api/v1"


@pytest.mark.parametrize("value", INVALID_SLUGS)
def test_get_uri_errors(value):
    with pytest.raises(
        ValueError, match=r"(slug must be an str|slug can't be (None|an empty str))"
    ):
        NB.get_uri(value)


def test_get_auth_headers_success():
    assert NB.get_auth_headers("foo") == {"authorization": "Bearer foo"}
    assert NB.get_auth_headers("bar") == {"authorization": "Bearer bar"}


@pytest.mark.parametrize("value", INVALID_SLUGS)
def test_get_auth_headers_errors(value):
    with pytest.raises(
        ValueError,
        match=r"(access_token must be an str|access_token can't be (None|an empty str))",
    ):
        NB.get_auth_headers(value)


def test_parse_next_params_success():
    nonce, token = NB.parse_next_params("/a/b/c?__nonce=foo&__token=bar")

    assert nonce == "foo"
    assert token == "bar"


@pytest.mark.parametrize(
    ("path", "match"),
    [
        ("/a/b/c?baz=1", "__nonce param not found"),
        ("/a/b/c?__nonce=1", "__token param not found"),
        ("/a/b/c?__token=1", "__nonce param not found"),
    ],
)
def test_parse_next_params_errors(path, match):
    with pytest.raises(ValueError, match=match):
        NB.parse_next_params(path)


def test_make_next_url():
    assert (
        NB.make_next_url("example.com", "bar", "baz")
        == "example.com?limit=100&__nonce=bar&__token=baz"
    )


def test_get_people_handle_empty_response(nb, base_url, requests_mock):
    requests_mock.get(f"{base_url}/people", json={"results": []})

    assert nb.get_people().num_rows == 0


def test_get_people(nb, base_url, requests_mock, load):
    requests_mock.get(f"{base_url}/people", json=load("get_people_response"))

    table = nb.get_people()

    assert table.num_rows == 2
    assert len(table.columns) == 59
    assert table[0]["first_name"] == "Foo"
    assert table[0]["last_name"] == "Bar"
    assert table[0]["email"] == "foo@example.com"


def test_get_people_follows_next(nb, base_url, requests_mock, load):
    """The `next` link is followed, so paging accumulates rows across requests."""
    first_page = load("get_people_response")
    first_page["next"] = f"{base_url}/people?limit=100&__nonce=bar&__token=baz"

    requests_mock.get(f"{base_url}/people", json=first_page)
    requests_mock.get(
        f"{base_url}/people?limit=100&__nonce=bar&__token=baz",
        json=load("get_people_response"),
    )

    table = nb.get_people()

    assert table.num_rows == 4
    assert len(table.columns) == 59
    assert table[1]["first_name"] == "Zoo"
    assert table[1]["last_name"] == "Baz"
    assert table[1]["email"] == "bar@example.com"


@pytest.mark.parametrize(
    ("person_id", "person", "match"),
    [
        (None, {}, "person_id can't be None"),
        (1, {}, "person_id must be a str"),
        (" ", {}, "person_id can't be an empty str"),
        ("1", None, "person must be a dict"),
        ("1", "bad value", "person must be a dict"),
    ],
)
def test_update_person_raises_with_bad_params(nb, person_id, person, match):
    with pytest.raises(ValueError, match=match):
        nb.update_person(person_id, person)


def test_update_person(nb, base_url, requests_mock, load):
    requests_mock.put(f"{base_url}/people/1", json=load("person_response"))

    response = nb.update_person("1", {"tags": ["zoot", "boot"]})

    person = response["person"]
    assert person["id"] == 1
    assert person["first_name"] == "Foo"
    assert person["last_name"] == "Bar"
    assert person["email"] == "foo@example.com"


def test_upsert_person_raises_with_bad_params(nb):
    with pytest.raises(ValueError, match="person dict must contain at least one key of"):
        nb.upsert_person({"tags": ["zoot", "boot"]})


def test_upsert_person(nb, base_url, requests_mock, load):
    requests_mock.put(f"{base_url}/people/push", json=load("person_response"))

    created, response = nb.upsert_person({"email": "foo@example.com"})

    assert not created
    person = response["person"]
    assert person["id"] == 1
    assert person["first_name"] == "Foo"
    assert person["last_name"] == "Bar"
    assert person["email"] == "foo@example.com"
