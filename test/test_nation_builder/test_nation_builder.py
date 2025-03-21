import unittest

import requests_mock

from parsons import NationBuilder as NB

from .fixtures import GET_PEOPLE_RESPONSE, PERSON_RESPONSE


class TestNationBuilder(unittest.TestCase):
    def test_client(self):
        nb = NB("test-slug", "test-token")
        assert nb.client.uri == "https://test-slug.nationbuilder.com/api/v1/"
        assert nb.client.headers == {
            "authorization": "Bearer test-token",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def test_get_uri_success(self):
        assert NB.get_uri("foo") == "https://foo.nationbuilder.com/api/v1"
        assert NB.get_uri("bar") == "https://bar.nationbuilder.com/api/v1"

    def test_get_uri_errors(self):
        values = ["", "  ", None, 1337, {}, []]

        for v in values:
            with self.assertRaises(ValueError):
                NB.get_uri(v)

    def test_get_auth_headers_success(self):
        assert NB.get_auth_headers("foo") == {"authorization": "Bearer foo"}
        assert NB.get_auth_headers("bar") == {"authorization": "Bearer bar"}

    def test_get_auth_headers_errors(self):
        values = ["", "  ", None, 1337, {}, []]

        for v in values:
            with self.assertRaises(ValueError):
                NB.get_auth_headers(v)

    def test_parse_next_params_success(self):
        n, t = NB.parse_next_params("/a/b/c?__nonce=foo&__token=bar")
        assert n == "foo"
        assert t == "bar"

    def test_get_next_params_errors(self):
        with self.assertRaises(ValueError):
            NB.parse_next_params("/a/b/c?baz=1")

        with self.assertRaises(ValueError):
            NB.parse_next_params("/a/b/c?__nonce=1")

        with self.assertRaises(ValueError):
            NB.parse_next_params("/a/b/c?__token=1")

    def test_make_next_url(self):
        assert (
            NB.make_next_url("example.com", "bar", "baz")
            == "example.com?limit=100&__nonce=bar&__token=baz"
        )

    @requests_mock.Mocker()
    def test_get_people_handle_empty_response(self, m):
        nb = NB("test-slug", "test-token")
        m.get("https://test-slug.nationbuilder.com/api/v1/people", json={"results": []})
        table = nb.get_people()
        assert table.num_rows == 0

    @requests_mock.Mocker()
    def test_get_people(self, m):
        nb = NB("test-slug", "test-token")
        m.get(
            "https://test-slug.nationbuilder.com/api/v1/people",
            json=GET_PEOPLE_RESPONSE,
        )
        table = nb.get_people()

        assert table.num_rows == 2
        assert len(table.columns) == 59

        assert table[0]["first_name"] == "Foo"
        assert table[0]["last_name"] == "Bar"
        assert table[0]["email"] == "foo@example.com"

    @requests_mock.Mocker()
    def test_get_people_with_next(self, m):
        """Make two requests and get the same data twice. This will exercise the while loop."""
        nb = NB("test-slug", "test-token")

        GET_PEOPLE_RESPONSE_WITH_NEXT = GET_PEOPLE_RESPONSE.copy()
        GET_PEOPLE_RESPONSE_WITH_NEXT["next"] = (
            "https://test-slug.nationbuilder.com/api/v1/people?limit=100&__nonce=bar&__token=baz"
        )

        m.get(
            "https://test-slug.nationbuilder.com/api/v1/people",
            json=GET_PEOPLE_RESPONSE_WITH_NEXT,
        )

        m.get(
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

        with self.assertRaises(ValueError):
            nb.update_person(None, {})

        with self.assertRaises(ValueError):
            nb.update_person(1, {})

        with self.assertRaises(ValueError):
            nb.update_person(" ", {})

        with self.assertRaises(ValueError):
            nb.update_person("1", None)

        with self.assertRaises(ValueError):
            nb.update_person("1", "bad value")

    @requests_mock.Mocker()
    def test_update_person(self, m):
        """Requests the correct URL, returns the correct data and doesn't raise exceptions."""
        nb = NB("test-slug", "test-token")

        m.put(
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

        with self.assertRaises(ValueError):
            nb.upsert_person({"tags": ["zoot", "boot"]})

    @requests_mock.Mocker()
    def test_upsert_person(self, m):
        """Requests the correct URL, returns the correct data and doesn't raise exceptions."""
        nb = NB("test-slug", "test-token")

        m.put(
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
