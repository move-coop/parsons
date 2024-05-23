import os
import unittest
import requests_mock
from unittest import mock
from test.utils import assert_matching_tables
from parsons import Bloomerang, Table

from test.test_bloomerang.test_data import (
    ENV_PARAMETERS,
    ID,
    TEST_DELETE,
    TEST_CREATE_CONSTITUENT,
    TEST_GET_CONSTITUENT,
    TEST_GET_CONSTITUENTS,
    TEST_CREATE_TRANSACTION,
    TEST_GET_TRANSACTION,
    TEST_GET_TRANSACTIONS,
    TEST_CREATE_INTERACTION,
    TEST_GET_INTERACTION,
    TEST_GET_INTERACTIONS,
)


class TestBloomerang(unittest.TestCase):
    def setUp(self):
        self.bloomerang = Bloomerang(api_key="test_key")

    @mock.patch.dict(os.environ, ENV_PARAMETERS)
    def test_init_env(self):
        bloomerang = Bloomerang()
        self.assertEqual(bloomerang.api_key, "env_api_key")
        self.assertEqual(bloomerang.client_id, "env_client_id")
        self.assertEqual(bloomerang.client_secret, "env_client_secret")

    @requests_mock.Mocker()
    def test_authentication(self, m):
        # API key
        bloomerang = Bloomerang(api_key="my_key")
        self.assertEqual(bloomerang.conn.headers["X-API-KEY"], "my_key")

        # OAuth2
        m.post(url=bloomerang.uri_auth, json={"code": "my_auth_code"})
        m.post(url=bloomerang.uri + "oauth/token", json={"access_token": "my_access_token"})
        bloomerang = Bloomerang(client_id="my_id", client_secret="my_secret")
        self.assertEqual(bloomerang.authorization_code, "my_auth_code")
        self.assertEqual(bloomerang.access_token, "my_access_token")
        self.assertEqual(bloomerang.conn.headers["Authorization"], "Bearer my_access_token")

    def test_base_endpoint(self):
        url = self.bloomerang._base_endpoint("constituent")
        self.assertEqual(url, "https://api.bloomerang.co/v2/constituent/")

        url = self.bloomerang._base_endpoint("constituent", 1234)
        self.assertEqual(url, "https://api.bloomerang.co/v2/constituent/1234/")

        url = self.bloomerang._base_endpoint("constituent", "1234")
        self.assertEqual(url, "https://api.bloomerang.co/v2/constituent/1234/")

    @requests_mock.Mocker()
    def test_create_constituent(self, m):
        m.post(f"{self.bloomerang.uri}constituent/", json=TEST_CREATE_CONSTITUENT)
        self.assertEqual(self.bloomerang.create_constituent(), TEST_CREATE_CONSTITUENT)

    @requests_mock.Mocker()
    def test_update_constituent(self, m):
        m.put(f"{self.bloomerang.uri}constituent/{ID}/", json=TEST_CREATE_CONSTITUENT)
        self.assertEqual(self.bloomerang.update_constituent(ID), TEST_CREATE_CONSTITUENT)

    @requests_mock.Mocker()
    def test_get_constituent(self, m):
        m.get(f"{self.bloomerang.uri}constituent/{ID}/", json=TEST_GET_CONSTITUENT)
        self.assertEqual(self.bloomerang.get_constituent(ID), TEST_GET_CONSTITUENT)

    @requests_mock.Mocker()
    def test_delete_constituent(self, m):
        m.delete(f"{self.bloomerang.uri}constituent/{ID}/", json=TEST_DELETE)
        self.assertEqual(self.bloomerang.delete_constituent(ID), TEST_DELETE)

    @requests_mock.Mocker()
    def test_get_constituents(self, m):
        m.get(
            f"{self.bloomerang.uri}constituents/?skip=0&take=50",
            json=TEST_GET_CONSTITUENTS,
        )
        assert_matching_tables(
            self.bloomerang.get_constituents(), Table(TEST_GET_CONSTITUENTS["Results"])
        )

    @requests_mock.Mocker()
    def test_create_transaction(self, m):
        m.post(f"{self.bloomerang.uri}transaction/", json=TEST_CREATE_TRANSACTION)
        self.assertEqual(self.bloomerang.create_transaction(), TEST_CREATE_TRANSACTION)

    @requests_mock.Mocker()
    def test_update_transaction(self, m):
        m.put(f"{self.bloomerang.uri}transaction/{ID}/", json=TEST_CREATE_TRANSACTION)
        self.assertEqual(self.bloomerang.update_transaction(ID), TEST_CREATE_TRANSACTION)

    @requests_mock.Mocker()
    def test_get_transaction(self, m):
        m.get(f"{self.bloomerang.uri}transaction/{ID}/", json=TEST_GET_TRANSACTION)
        self.assertEqual(self.bloomerang.get_transaction(ID), TEST_GET_TRANSACTION)

    @requests_mock.Mocker()
    def test_delete_transaction(self, m):
        m.delete(f"{self.bloomerang.uri}transaction/{ID}/", json=TEST_DELETE)
        self.assertEqual(self.bloomerang.delete_transaction(ID), TEST_DELETE)

    @requests_mock.Mocker()
    def test_get_transactions(self, m):
        m.get(
            f"{self.bloomerang.uri}transactions/?skip=0&take=50",
            json=TEST_GET_TRANSACTIONS,
        )
        assert_matching_tables(
            self.bloomerang.get_transactions(), Table(TEST_GET_TRANSACTIONS["Results"])
        )

    @requests_mock.Mocker()
    def test_get_transaction_designation(self, m):
        m.get(
            f"{self.bloomerang.uri}transaction/designation/{ID}/",
            json=TEST_GET_TRANSACTION,
        )
        self.assertEqual(self.bloomerang.get_transaction_designation(ID), TEST_GET_TRANSACTION)

    @requests_mock.Mocker()
    def test_get_transaction_designations(self, m):
        m.get(
            f"{self.bloomerang.uri}transactions/designations/?skip=0&take=50",
            json=TEST_GET_TRANSACTIONS,
        )
        assert_matching_tables(
            self.bloomerang.get_transaction_designations(),
            Table(TEST_GET_TRANSACTIONS["Results"]),
        )

    @requests_mock.Mocker()
    def test_create_interaction(self, m):
        m.post(f"{self.bloomerang.uri}interaction/", json=TEST_CREATE_INTERACTION)
        self.assertEqual(self.bloomerang.create_interaction(), TEST_CREATE_INTERACTION)

    @requests_mock.Mocker()
    def test_update_interaction(self, m):
        m.put(f"{self.bloomerang.uri}interaction/{ID}/", json=TEST_CREATE_INTERACTION)
        self.assertEqual(self.bloomerang.update_interaction(ID), TEST_CREATE_INTERACTION)

    @requests_mock.Mocker()
    def test_get_interaction(self, m):
        m.get(f"{self.bloomerang.uri}interaction/{ID}/", json=TEST_GET_INTERACTION)
        self.assertEqual(self.bloomerang.get_interaction(ID), TEST_GET_INTERACTION)

    @requests_mock.Mocker()
    def test_delete_interaction(self, m):
        m.delete(f"{self.bloomerang.uri}interaction/{ID}/", json=TEST_DELETE)
        self.assertEqual(self.bloomerang.delete_interaction(ID), TEST_DELETE)

    @requests_mock.Mocker()
    def test_get_interactions(self, m):
        m.get(
            f"{self.bloomerang.uri}interactions/?skip=0&take=50",
            json=TEST_GET_INTERACTIONS,
        )
        assert_matching_tables(
            self.bloomerang.get_interactions(), Table(TEST_GET_INTERACTIONS["Results"])
        )
