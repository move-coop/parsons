from pathlib import Path

import pytest

from parsons import Table
from test.test_actblue import test_columns_data
from test.test_actblue.conftest import TEST_URI

TEST_ID = "12345"

TEST_CSV_TYPE = "refunded_contributions"
TEST_DATE_RANGE_START = "2017-07-07"
TEST_DATE_RANGE_END = "2017-08-07"

TEST_POST_RESPONSE = {"id": TEST_ID}

TEST_DOWNLOAD_URL = "https://www.example.com/example.csv"

TEST_GET_RESPONSE = {
    "id": TEST_ID,
    "download_url": TEST_DOWNLOAD_URL,
    "status": "complete",
}


def test_successful_post_request(actblue, requests_mock):
    requests_mock.post(f"{TEST_URI}/csvs", json=TEST_POST_RESPONSE)

    response = actblue.post_request(TEST_CSV_TYPE, TEST_DATE_RANGE_START, TEST_DATE_RANGE_END)
    assert response["id"] == TEST_POST_RESPONSE["id"]


def test_successful_get_download_url(actblue, requests_mock):
    requests_mock.get(f"{TEST_URI}/csvs/{TEST_ID}", json=TEST_GET_RESPONSE)

    assert actblue.get_download_url(csv_id=TEST_ID) == TEST_DOWNLOAD_URL


def test_successful_poll_for_download_url(actblue, requests_mock):
    mocked_get_response_no_download_url = {
        "id": TEST_ID,
        "download_url": None,
        "status": "in_progress",
    }

    requests_mock.get(
        f"{TEST_URI}/csvs/{TEST_ID}",
        [
            {"json": mocked_get_response_no_download_url},
            {"json": TEST_GET_RESPONSE},
        ],
    )

    assert actblue.poll_for_download_url(csv_id=TEST_ID) == TEST_DOWNLOAD_URL


def test_successful_get_contributions(actblue, requests_mock, mocker):
    requests_mock.post(f"{TEST_URI}/csvs", json=TEST_POST_RESPONSE)
    requests_mock.get(f"{TEST_URI}/csvs/{TEST_ID}", json=TEST_GET_RESPONSE)

    test_csv_data = Table.from_csv_string(Path("test/test_actblue/test_csv_data.csv").read_text())
    mocker.patch.object(Table, "from_csv", name="mocked from_csv", return_value=test_csv_data)

    table = actblue.get_contributions(TEST_CSV_TYPE, TEST_DATE_RANGE_START, TEST_DATE_RANGE_END)
    assert test_columns_data.expected_table_columns == table.columns


def test_error_on_complete_without_download_url(actblue, requests_mock):
    mocked_get_response_no_url = {
        "id": TEST_ID,
        "download_url": None,
        "status": "complete",
    }

    requests_mock.get(f"{TEST_URI}/csvs/{TEST_ID}", json=mocked_get_response_no_url)

    with pytest.raises(ValueError, match="CSV generation failed"):
        actblue.get_download_url(csv_id=TEST_ID)


def test_error_on_unexpected_status(actblue, requests_mock):
    mocked_get_response_no_url = {
        "id": TEST_ID,
        "download_url": None,
        "status": "error",
    }

    requests_mock.get(f"{TEST_URI}/csvs/{TEST_ID}", json=mocked_get_response_no_url)

    with pytest.raises(ValueError, match="CSV generation failed"):
        actblue.get_download_url(csv_id=TEST_ID)


def test_no_error_on_expected_status(actblue, requests_mock):
    mocked_get_response_no_url = {
        "id": TEST_ID,
        "download_url": "www.actblue.com",
        "status": "complete",
    }

    requests_mock.get(f"{TEST_URI}/csvs/{TEST_ID}", json=mocked_get_response_no_url)

    assert actblue.get_download_url(csv_id=TEST_ID) == "www.actblue.com"
