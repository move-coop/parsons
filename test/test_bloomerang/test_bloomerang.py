from parsons import Bloomerang, Table
from test.conftest import assert_matching_tables
from test.test_bloomerang.test_data import (
    ENV_PARAMETERS,
    ID,
    TEST_CREATE_CONSTITUENT,
    TEST_CREATE_INTERACTION,
    TEST_CREATE_TRANSACTION,
    TEST_DELETE,
    TEST_GET_CONSTITUENT,
    TEST_GET_CONSTITUENTS,
    TEST_GET_INTERACTION,
    TEST_GET_INTERACTIONS,
    TEST_GET_TRANSACTION,
    TEST_GET_TRANSACTIONS,
)


def test_init_env(monkeypatch):
    for key, value in ENV_PARAMETERS.items():
        monkeypatch.setenv(key, value)

    bloomerang = Bloomerang()
    assert bloomerang.api_key == "env_api_key"
    assert bloomerang.client_id == "env_client_id"
    assert bloomerang.client_secret == "env_client_secret"


def test_authentication(requests_mock):
    # API key
    bloomerang = Bloomerang(api_key="my_key")
    assert bloomerang.conn.headers["X-API-KEY"] == "my_key"

    # OAuth2
    requests_mock.post(url=bloomerang.uri_auth, json={"code": "my_auth_code"})
    requests_mock.post(url=bloomerang.uri + "oauth/token", json={"access_token": "my_access_token"})
    bloomerang = Bloomerang(client_id="my_id", client_secret="my_secret")
    assert bloomerang.authorization_code == "my_auth_code"
    assert bloomerang.access_token == "my_access_token"
    assert bloomerang.conn.headers["Authorization"] == "Bearer my_access_token"


def test_base_endpoint(bloomerang):
    url = bloomerang._base_endpoint("constituent")
    assert url == "https://api.bloomerang.co/v2/constituent/"

    url = bloomerang._base_endpoint("constituent", 1234)
    assert url == "https://api.bloomerang.co/v2/constituent/1234/"

    url = bloomerang._base_endpoint("constituent", "1234")
    assert url == "https://api.bloomerang.co/v2/constituent/1234/"


def test_create_constituent(bloomerang, requests_mock):
    requests_mock.post(f"{bloomerang.uri}constituent/", json=TEST_CREATE_CONSTITUENT)
    assert bloomerang.create_constituent() == TEST_CREATE_CONSTITUENT


def test_update_constituent(bloomerang, requests_mock):
    requests_mock.put(f"{bloomerang.uri}constituent/{ID}/", json=TEST_CREATE_CONSTITUENT)
    assert bloomerang.update_constituent(ID) == TEST_CREATE_CONSTITUENT


def test_get_constituent(bloomerang, requests_mock):
    requests_mock.get(f"{bloomerang.uri}constituent/{ID}/", json=TEST_GET_CONSTITUENT)
    assert bloomerang.get_constituent(ID) == TEST_GET_CONSTITUENT


def test_delete_constituent(bloomerang, requests_mock):
    requests_mock.delete(f"{bloomerang.uri}constituent/{ID}/", json=TEST_DELETE)
    assert bloomerang.delete_constituent(ID) == TEST_DELETE


def test_get_constituents(bloomerang, requests_mock):
    requests_mock.get(
        f"{bloomerang.uri}constituents/?skip=0&take=50",
        json=TEST_GET_CONSTITUENTS,
    )
    assert_matching_tables(bloomerang.get_constituents(), Table(TEST_GET_CONSTITUENTS["Results"]))


def test_create_transaction(bloomerang, requests_mock):
    requests_mock.post(f"{bloomerang.uri}transaction/", json=TEST_CREATE_TRANSACTION)
    assert bloomerang.create_transaction() == TEST_CREATE_TRANSACTION


def test_update_transaction(bloomerang, requests_mock):
    requests_mock.put(f"{bloomerang.uri}transaction/{ID}/", json=TEST_CREATE_TRANSACTION)
    assert bloomerang.update_transaction(ID) == TEST_CREATE_TRANSACTION


def test_get_transaction(bloomerang, requests_mock):
    requests_mock.get(f"{bloomerang.uri}transaction/{ID}/", json=TEST_GET_TRANSACTION)
    assert bloomerang.get_transaction(ID) == TEST_GET_TRANSACTION


def test_delete_transaction(bloomerang, requests_mock):
    requests_mock.delete(f"{bloomerang.uri}transaction/{ID}/", json=TEST_DELETE)
    assert bloomerang.delete_transaction(ID) == TEST_DELETE


def test_get_transactions(bloomerang, requests_mock):
    requests_mock.get(
        f"{bloomerang.uri}transactions/?skip=0&take=50",
        json=TEST_GET_TRANSACTIONS,
    )
    assert_matching_tables(bloomerang.get_transactions(), Table(TEST_GET_TRANSACTIONS["Results"]))


def test_get_transaction_designation(bloomerang, requests_mock):
    requests_mock.get(
        f"{bloomerang.uri}transaction/designation/{ID}/",
        json=TEST_GET_TRANSACTION,
    )
    assert bloomerang.get_transaction_designation(ID) == TEST_GET_TRANSACTION


def test_get_transaction_designations(bloomerang, requests_mock):
    requests_mock.get(
        f"{bloomerang.uri}transactions/designations/?skip=0&take=50",
        json=TEST_GET_TRANSACTIONS,
    )
    assert_matching_tables(
        bloomerang.get_transaction_designations(),
        Table(TEST_GET_TRANSACTIONS["Results"]),
    )


def test_create_interaction(bloomerang, requests_mock):
    requests_mock.post(f"{bloomerang.uri}interaction/", json=TEST_CREATE_INTERACTION)
    assert bloomerang.create_interaction() == TEST_CREATE_INTERACTION


def test_update_interaction(bloomerang, requests_mock):
    requests_mock.put(f"{bloomerang.uri}interaction/{ID}/", json=TEST_CREATE_INTERACTION)
    assert bloomerang.update_interaction(ID) == TEST_CREATE_INTERACTION


def test_get_interaction(bloomerang, requests_mock):
    requests_mock.get(f"{bloomerang.uri}interaction/{ID}/", json=TEST_GET_INTERACTION)
    assert bloomerang.get_interaction(ID) == TEST_GET_INTERACTION


def test_delete_interaction(bloomerang, requests_mock):
    requests_mock.delete(f"{bloomerang.uri}interaction/{ID}/", json=TEST_DELETE)
    assert bloomerang.delete_interaction(ID) == TEST_DELETE


def test_get_interactions(bloomerang, requests_mock):
    requests_mock.get(
        f"{bloomerang.uri}interactions/?skip=0&take=50",
        json=TEST_GET_INTERACTIONS,
    )
    assert_matching_tables(bloomerang.get_interactions(), Table(TEST_GET_INTERACTIONS["Results"]))
