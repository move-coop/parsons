import time
from unittest.mock import MagicMock

import pytest

from parsons import CatalistMatch, Table

TEST_CLIENT_ID = "some_client_id"
TEST_CLIENT_SECRET = "some_client_secret"
TEST_SFTP_USERNAME = "username"
TEST_SFTP_PASSWORD = "password"


def table_for_test(include_last_name: bool = True) -> Table:
    """Parsons Table for tests"""
    table = Table(
        [
            {"first_name": "John", "last_name": "Doe"},
            {"first_name": "Jane", "last_name": "Doe"},
        ]
    )
    if not include_last_name:
        table = table.cut("first_name")
    return table


def match_client() -> CatalistMatch:
    result = CatalistMatch(
        client_id=TEST_CLIENT_ID,
        client_secret=TEST_CLIENT_SECRET,
        sftp_username=TEST_SFTP_USERNAME,
        sftp_password=TEST_SFTP_PASSWORD,
    )
    result._token_expired_at = time.time() + 99999
    return result


class TestCatalist:
    def test_fixtures_active(self) -> None:
        """Test to ensure fixtures are active and relevant clients are mocked."""
        match = match_client()
        assert isinstance(match.sftp, MagicMock)
        assert match.connection.request("url", "get").json()[0]["test"]

    def test_validate_table(self) -> None:
        """Check that table validation method works as expected."""
        match = match_client()
        table = table_for_test()
        match.validate_table(table)

        # first_name and last_name are required
        # We expect an exception raised if last_name is missing
        table_to_fail = table_for_test(include_last_name=False)
        with pytest.raises(ValueError, match="Input table does not have the right structure"):
            match.validate_table(table_to_fail)

    def test_load_table_to_sftp(self) -> None:
        """Check that table load to SFTP executes as expected."""
        match = match_client()
        source_table = table_for_test()
        response = match.load_table_to_sftp(source_table)

        assert response.startswith("file://")
        assert "myUploads" not in response
        assert response.endswith(".csv.gz")

        # We expect one call to the SFTP client to put the file
        assert len(match.sftp.mock_calls) == 1
        mocked_call = match.sftp.mock_calls[0]
        called_method = str(mocked_call).split("(")[0].split(".")[1]
        assert called_method == "put_file"
        temp_local_file = mocked_call.args[0]
        remote_path = mocked_call.args[1]

        # Expect local temp file CSV is the same as the source table CSV
        table_to_load = Table.from_csv(temp_local_file)
        for row_index in range(table_to_load.num_rows):
            assert source_table[row_index] == table_to_load[row_index]

        # Expect the remote path is structured as expected
        assert remote_path.startswith("myUploads/")
        assert remote_path.endswith(".csv.gz")

    def test_upload(self, mock_requests) -> None:
        """Mock use of upload() method, check API calls are structured as expected."""
        match = match_client()
        source_table = table_for_test()

        # Execute upload
        match.upload(source_table)

        requested_endpoint = mock_requests._adapter.request_history[1].path
        requested_queries = mock_requests._adapter.request_history[1].qs
        requested_base_url = mock_requests._adapter.request_history[1]._url_parts.netloc

        assert requested_base_url == "api.catalist.us"
        assert set(requested_queries.keys()) == {"token"}
        assert requested_queries["token"] == ["tokenexample"]
        assert requested_endpoint.startswith("/mapi/upload/template/48827/action/publish/url/")

    def test_upload_with_options(self, mock_requests) -> None:
        """Mock use of upload() method with options, check API calls."""
        match = match_client()
        source_table = table_for_test()

        # Execute upload
        match.upload(
            source_table,
            copy_to_sandbox=True,
            static_values={"phone": 123456789},
        )

        requested_queries = mock_requests._adapter.request_history[1].qs

        assert set(requested_queries.keys()) == {"token", "copytosandbox", "phone"}
        assert requested_queries["copytosandbox"] == ["true"]
        assert requested_queries["phone"] == ["123456789"]

    def test_status(self, mock_requests) -> None:
        """Mock use of status() method, check API calls are structured as expected."""
        match = match_client()

        # Check status
        match.status("12345")

        requested_endpoint = mock_requests._adapter.request_history[1].path
        requested_queries = mock_requests._adapter.request_history[1].qs
        requested_base_url = mock_requests._adapter.request_history[1]._url_parts.netloc

        assert requested_base_url == "api.catalist.us"
        assert set(requested_queries.keys()) == {"token"}
        assert requested_queries["token"] == ["tokenexample"]
        assert requested_endpoint == "/mapi/status/id/12345"

    def test_load_matches(self) -> None:
        """Check that table download method from SFTP executes as expected."""
        match = match_client()

        # Execute download
        match.sftp.list_directory = MagicMock(return_value=["example_12345"])
        match.load_matches("12345")

        # We expect two calls to the SFTP client to list the directory and get the file
        assert len(match.sftp.mock_calls) == 2

        first_mocked_call = match.sftp.mock_calls[0]
        first_called_method = str(first_mocked_call).split("(")[0].split(".")[1]

        assert first_called_method == "list_directory"
        assert set(first_mocked_call.args) == {"/myDownloads/"}

        second_mocked_call = match.sftp.mock_calls[1]
        second_called_method = str(second_mocked_call).split("(")[0].split(".")[1]

        assert second_called_method == "get_file"

        assert second_mocked_call.kwargs == {
            "remote_path": "/myDownloads/example_12345",
            "export_chunk_size": 52428800,
        }
