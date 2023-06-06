import unittest

from parsons import NationBuilder as NB


class TestNationBuilder(unittest.TestCase):
    def test_client(self):
        nb = NB("test-slug", "test-token")
        self.assertEqual(nb.client.uri, "https://test-slug.nationbuilder.com/api/v1/")
        self.assertEqual(
            nb.client.headers,
            {
                "authorization": "Bearer test-token",
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
        )

    def test_get_uri_success(self):
        self.assertEqual(NB.get_uri("foo"), "https://foo.nationbuilder.com/api/v1")
        self.assertEqual(NB.get_uri("bar"), "https://bar.nationbuilder.com/api/v1")

    def test_get_uri_errors(self):
        values = ["", "  ", None, 1337, {}, []]

        for v in values:
            with self.assertRaises(ValueError):
                NB.get_uri(v)

    def test_get_auth_headers_success(self):
        self.assertEqual(NB.get_auth_headers("foo"), {"authorization": "Bearer foo"})
        self.assertEqual(NB.get_auth_headers("bar"), {"authorization": "Bearer bar"})

    def test_get_auth_headers_errors(self):
        values = ["", "  ", None, 1337, {}, []]

        for v in values:
            with self.assertRaises(ValueError):
                NB.get_auth_headers(v)

    def test_parse_next_params_success(self):
        n, t = NB.parse_next_params("/a/b/c?__nonce=foo&__token=bar")
        self.assertEqual(n, "foo")
        self.assertEqual(t, "bar")

    def test_get_next_params_errors(self):
        with self.assertRaises(ValueError):
            NB.parse_next_params("/a/b/c?baz=1")

        with self.assertRaises(ValueError):
            NB.parse_next_params("/a/b/c?__nonce=1")

        with self.assertRaises(ValueError):
            NB.parse_next_params("/a/b/c?__token=1")

    def test_make_next_url(self):
        self.assertEqual(
            NB.make_next_url("example.com", "bar", "baz"),
            "example.com?limit=100&__nonce=bar&__token=baz",
        )
