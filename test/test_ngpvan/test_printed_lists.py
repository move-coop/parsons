from parsons import VAN
from test.test_ngpvan.responses_printed_lists import list_json, single_list_json


def test_get_printed_lists(van: VAN, requests_mock):
    requests_mock.get(van.connection.uri + "printedLists", json=list_json)

    result = van.get_printed_lists(folder_name="Covington Canvass Turfs")

    assert result.num_rows == 14


def test_get_printed_list(van: VAN, requests_mock):
    requests_mock.get(van.connection.uri + "printedLists/43-0000", json=single_list_json)

    result = van.get_printed_list(printed_list_number="43-0000")

    assert result["number"] == "43-0000"
