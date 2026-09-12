import pytest
from requests_mock import Mocker

from parsons import NationBuilder as NB

from .fixtures import GET_PEOPLE_RESPONSE, PERSON_RESPONSE


class TestNationBuilder:
    def test_client(self):
        nb = NB("test-slug", "test-token")
        assert nb.client.uri == "https://test-slug.nationbuilder.com/api/v1/"
        assert nb.client.headers == {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        assert nb.client.auth.api_key == "test-token"

    def test_get_uri_success(self):
        assert NB.get_uri("foo") == "https://foo.nationbuilder.com/api/v1"
        assert NB.get_uri("bar") == "https://bar.nationbuilder.com/api/v1"

    @pytest.mark.parametrize(
        ("slug", "expected_exception"),
        [
            ("", ValueError),
            ("  ", ValueError),
            (None, TypeError),
            (1337, TypeError),
            ({}, TypeError),
            ([], TypeError),
        ],
    )
    def test_get_uri_errors(self, slug: str, expected_exception):
        with pytest.raises(
            expected_exception, match=r"(slug must be an str|slug can't be (None|an empty str))"
        ):
            NB.get_uri(slug)

    def test_validate_auth_success(self):
        assert NB.validate_auth("foo") == "foo"
        assert NB.validate_auth("bar") == "bar"

    @pytest.mark.parametrize(
        ("access_token", "expected_exception"),
        [
            ("", ValueError),
            ("  ", ValueError),
            (None, TypeError),
            (1337, TypeError),
            ({}, TypeError),
            ([], TypeError),
        ],
    )
    def test_validate_auth_errors(self, access_token: str, expected_exception):
        with pytest.raises(
            expected_exception,
            match=r"(access_token must be an str|access_token can't be (None|an empty str))",
        ):
            NB.validate_auth(access_token)

    def test_parse_next_params_success(self):
        n, t = NB.parse_next_params("/a/b/c?__nonce=foo&__token=bar")
        assert n == "foo"
        assert t == "bar"

    def test_get_next_params_errors(self):
        with pytest.raises(ValueError, match="__nonce param not found"):
            NB.parse_next_params("/a/b/c?baz=1")

        with pytest.raises(ValueError, match="__token param not found"):
            NB.parse_next_params("/a/b/c?__nonce=1")

        with pytest.raises(ValueError, match="__nonce param not found"):
            NB.parse_next_params("/a/b/c?__token=1")

    def test_make_next_url(self):
        assert (
            NB.make_next_url("example.com", "bar", "baz")
            == "example.com?limit=100&__nonce=bar&__token=baz"
        )

    def test_get_people_handle_empty_response(self, requests_mock: Mocker):
        nb = NB("test-slug", "test-token")
        requests_mock.get("https://test-slug.nationbuilder.com/api/v1/people", json={"results": []})
        table = nb.get_people()
        assert table.num_rows == 0

    def test_get_people(self, requests_mock: Mocker):
        nb = NB("test-slug", "test-token")
        requests_mock.get(
            "https://test-slug.nationbuilder.com/api/v1/people",
            json=GET_PEOPLE_RESPONSE,
        )
        table = nb.get_people()

        assert table.num_rows == 2
        assert len(table.columns) == 59

        assert table[0]["first_name"] == "Foo"
        assert table[0]["last_name"] == "Bar"
        assert table[0]["email"] == "foo@example.com"

    def test_get_people_with_next(self, requests_mock: Mocker):
        """Make two requests and get the same data twice. This will exercise the while loop."""
        nb = NB("test-slug", "test-token")

        GET_PEOPLE_RESPONSE_WITH_NEXT = GET_PEOPLE_RESPONSE.copy()
        GET_PEOPLE_RESPONSE_WITH_NEXT["next"] = (
            "https://test-slug.nationbuilder.com/api/v1/people?limit=100&__nonce=bar&__token=baz"
        )

        requests_mock.get(
            "https://test-slug.nationbuilder.com/api/v1/people",
            json=GET_PEOPLE_RESPONSE_WITH_NEXT,
        )

        requests_mock.get(
            "https://test-slug.nationbuilder.com/api/v1/people?limit=100&__nonce=bar&__token=baz",
            json=GET_PEOPLE_RESPONSE,
        )

        table = nb.get_people()

        assert table.num_rows == 4
        assert len(table.columns) == 59

        assert table[1]["first_name"] == "Zoo"
        assert table[1]["last_name"] == "Baz"
        assert table[1]["email"] == "bar@example.com"

    def test_update_person_raises_with_bad_params(self):
        nb = NB("test-slug", "test-token")

        with pytest.raises(ValueError, match="person_id can't be None"):
            nb.update_person(None, {})

        with pytest.raises(ValueError, match="person_id must be a str"):
            nb.update_person(1, {})

        with pytest.raises(ValueError, match="person_id can't be an empty str"):
            nb.update_person(" ", {})

        with pytest.raises(ValueError, match="person must be a dict"):
            nb.update_person("1", None)

        with pytest.raises(ValueError, match="person must be a dict"):
            nb.update_person("1", "bad value")

    def test_update_person(self, requests_mock: Mocker):
        """Requests the correct URL, returns the correct data and doesn't raise exceptions."""
        nb = NB("test-slug", "test-token")

        requests_mock.put(
            "https://test-slug.nationbuilder.com/api/v1/people/1",
            json=PERSON_RESPONSE,
        )

        response = nb.update_person("1", {"tags": ["zoot", "boot"]})
        person = response["person"]

        assert person["id"] == 1
        assert person["first_name"] == "Foo"
        assert person["last_name"] == "Bar"
        assert person["email"] == "foo@example.com"

    def test_upsert_person_raises_with_bad_params(self):
        nb = NB("test-slug", "test-token")

        with pytest.raises(ValueError, match="person dict must contain at least one key of"):
            nb.upsert_person({"tags": ["zoot", "boot"]})

    def test_upsert_person(self, requests_mock: Mocker):
        """Requests the correct URL, returns the correct data and doesn't raise exceptions."""
        nb = NB("test-slug", "test-token")

        requests_mock.put(
            "https://test-slug.nationbuilder.com/api/v1/people/push",
            json=PERSON_RESPONSE,
        )

        created, response = nb.upsert_person({"email": "foo@example.com"})
        assert not created

        person = response["person"]

        assert person["id"] == 1
        assert person["first_name"] == "Foo"
        assert person["last_name"] == "Bar"
        assert person["email"] == "foo@example.com"
