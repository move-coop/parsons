import pytest
import requests
from requests.exceptions import HTTPError

from parsons import Table
from parsons.utilities.api_connector import APIConnector


@pytest.fixture
def connector() -> APIConnector:
    return APIConnector(
        uri="https://api.example.com/v1", headers={"content-type": "application/json"}
    )


def test_init_adds_trailing_slash() -> None:
    conn = APIConnector(uri="https://api.example.com/v1")
    assert conn.uri == "https://api.example.com/v1/"


def test_init_adds_headers(connector: APIConnector, requests_mock) -> None:
    requests_mock.get(
        "https://api.example.com/v1/data", json={"status": "authorized"}, status_code=200
    )

    connector.request("data", "GET")

    req = requests_mock.last_request
    assert req.headers["content-type"] == "application/json"


def test_request_with_additional_headers(connector: APIConnector, requests_mock) -> None:
    requests_mock.get(
        "https://api.example.com/v1/data", json={"status": "authorized"}, status_code=200
    )

    connector.request(
        "data",
        "GET",
        additional_headers={"Authorization": "Bearer token123", "X-Custom-Header": "value"},
    )

    req = requests_mock.last_request
    assert req.headers["Authorization"] == "Bearer token123"
    assert req.headers["X-Custom-Header"] == "value"


def test_request_merges_base_and_additional_headers(connector: APIConnector, requests_mock) -> None:
    requests_mock.get("https://api.example.com/v1/data", json={}, status_code=200)

    connector.request(
        "data",
        "GET",
        additional_headers={"Authorization": "Bearer token123", "X-Custom-Header": "value"},
    )

    req = requests_mock.last_request
    assert req.headers["content-type"] == "application/json"
    assert req.headers["Authorization"] == "Bearer token123"
    assert req.headers["X-Custom-Header"] == "value"


def test_request_success(connector: APIConnector, requests_mock) -> None:
    requests_mock.get(
        "https://api.example.com/v1/users", json={"status": "success"}, status_code=200
    )

    resp = connector.request("users", "GET")
    assert resp.status_code == 200
    assert resp.json() == {"status": "success"}


def test_get_request_json(connector: APIConnector, requests_mock) -> None:
    requests_mock.get("https://api.example.com/v1/data", json={"data": [1, 2, 3]}, status_code=200)

    result = connector.get_request("data", return_format="json")
    assert result == {"data": [1, 2, 3]}


def test_get_request_content(connector: APIConnector, requests_mock) -> None:
    requests_mock.get(
        "https://api.example.com/v1/file", content=b"file content bytes", status_code=200
    )

    result = connector.get_request("file", return_format="content")
    assert result == b"file content bytes"


def test_get_request_invalid_format(connector: APIConnector, requests_mock) -> None:
    requests_mock.get(
        "https://api.example.com/v1/data", content=b"file content bytes", status_code=200
    )

    with pytest.raises(RuntimeError, match="is not a valid format, change to json or content"):
        connector.get_request("data", return_format="invalid")  # type: ignore


def test_post_request(connector: APIConnector, requests_mock) -> None:
    requests_mock.post(
        "https://api.example.com/v1/items", json={"id": 123, "created": True}, status_code=201
    )

    result = connector.post_request("items", json={"name": "test"})
    assert result == {"id": 123, "created": True}


def test_delete_request(connector: APIConnector, requests_mock) -> None:
    requests_mock.delete("https://api.example.com/v1/items/1", status_code=204)

    result = connector.delete_request("items/1")
    assert result == 204


def test_put_request(connector: APIConnector, requests_mock) -> None:
    requests_mock.put("https://api.example.com/v1/items/1", json={"updated": True}, status_code=200)

    result = connector.put_request("items/1", json={"name": "new_name"})
    assert result == {"updated": True}


def test_patch_request(connector: APIConnector, requests_mock) -> None:
    requests_mock.patch(
        "https://api.example.com/v1/items/1", json={"patched": True}, status_code=200
    )

    result = connector.patch_request("items/1", json={"name": "patch_name"})
    assert result == {"patched": True}


def test_validate_response_error(connector: APIConnector, requests_mock) -> None:
    requests_mock.get(
        "https://api.example.com/v1/error", json={"error": "Unauthorized"}, status_code=401
    )

    with pytest.raises(HTTPError) as exc_info:
        connector.get_request("error")

    assert "Code: 401" in str(exc_info.value)
    assert "Unauthorized" in str(exc_info.value)


def test_data_parse_with_data_key() -> None:
    conn = APIConnector(uri="https://api.example.com/v1/", data_key="results")
    payload = {"results": [{"id": 1}, {"id": 2}], "count": 2}
    parsed = conn.data_parse(payload)
    assert parsed == [{"id": 1}, {"id": 2}]


def test_data_parse_list_input() -> None:
    conn = APIConnector(uri="https://api.example.com/v1/")
    payload = [{"id": 1}, {"id": 2}]
    parsed = conn.data_parse(payload)
    assert parsed == payload


def test_next_page_check_url() -> None:
    conn = APIConnector(uri="https://api.example.com/v1/", pagination_key="next")

    assert conn.next_page_check_url({"next": "https://api.example.com/v1/data?page=2"}) is True
    assert conn.next_page_check_url({"next": None}) is False
    assert conn.next_page_check_url({"other_key": "val"}) is False


def test_json_check(connector: APIConnector, requests_mock) -> None:
    requests_mock.get("https://api.example.com/v1/json-check", json={"test": True}, status_code=200)
    requests_mock.get(
        "https://api.example.com/v1/text-check", text="Plain text response", status_code=200
    )

    resp_json = requests.get("https://api.example.com/v1/json-check")
    resp_text = requests.get("https://api.example.com/v1/text-check")

    assert connector.json_check(resp_json) is True
    assert connector.json_check(resp_text) is False


def test_convert_to_table(connector) -> None:
    list_data = [{"col1": "A", "col2": 1}, {"col1": "B", "col2": 2}]
    dict_data = {"col1": "A", "col2": 1}

    table_from_list = connector.convert_to_table(list_data)
    table_from_dict = connector.convert_to_table(dict_data)

    assert isinstance(table_from_list, Table)
    assert table_from_list.num_rows == 2

    assert isinstance(table_from_dict, Table)
    assert table_from_dict.num_rows == 1
